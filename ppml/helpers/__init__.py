import base64
import pickle
import psutil
import requests
from fastapi import HTTPException
from Pyfhel import Pyfhel, PyCtxt
import io
import Pyfhel
import pandas as pd
import os
import numpy as np

import ppml.config as Cfg
# from ppmlp.controllers.preprocess import create_context
class Helpers:
    @staticmethod
    def get_ram_usage():
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)

    
    @staticmethod
    def load_csv_from_base64(dataset_base64: str) -> pd.DataFrame:
        decoded = base64.b64decode(dataset_base64)
        buffer = io.StringIO(decoded.decode("utf-8"))
        return pd.read_csv(buffer)

    @staticmethod
    def get_dataset_by_id(dataset_id: str) -> pd.DataFrame:
        file_path = os.path.join(Cfg.APP_RAW_DATA_PATH, f"{dataset_id}.csv")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError
        return pd.read_csv(file_path)

    @staticmethod
    def create_context():
        HE = Pyfhel()
        HE.contextGen(
            scheme='ckks', 
            n=16384, 
            scale=2**40,         
            qi_sizes=[60, 40, 40, 40, 40, 60]  
        )

        HE.keyGen()            
        HE.relinKeyGen()        
        HE.rotateKeyGen()       
            
        return HE
    @staticmethod
    def load_dataset(dataset_id: str):
        file_path = os.path.join(Cfg.APP_SINK_DATA_PATH, f"{dataset_id}.bin")
        with open(file_path, "rb") as f:
            df = pickle.load(f)
        return df
    @staticmethod
    def encrypt_dataset(dataset_id: str):
        try:
            HE = Helpers.create_context()
            df = Helpers.load_dataset(dataset_id)

            X_data = df.iloc[:, :-1].values.astype(np.float64).flatten()
            y_data = df.iloc[:, -1].values.astype(np.float64)

            cx = HE.encrypt(X_data)
            cy = HE.encrypt(y_data)

            return HE, cx, cy
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error encrypting the dataset {dataset_id}: {str(e)}")

    ###########################################################################################################
    def encrypt_datasetsssssssss(dataset_id: str):
        try:
            HE = Helpers.create_context()
            file_path = os.path.join(Cfg.APP_SINK_DATA_PATH, f"{dataset_id}.bin")
            with open(file_path, "rb") as f:
                df = pickle.load(f)
            
            # 1. Preparación de dimensiones
            n_samples = df.shape[0]
            n_features = df.shape[1] - 1
            
            # 2. Organización de los datos (IMPORTANTE)
            # Para que el servidor haga (cx * w), cx debe estar alineado.
            # Si x_data es [f1, f2, f1, f2...], al multiplicar por w [w1, w2], 
            # coincidirán perfectamente en los slots.
            X_data = df.iloc[:, :-1].values.astype(np.float64).flatten()
            y_data = df.iloc[:, -1].values.astype(np.float64)

            # 3. Cifrado
            cx = HE.encrypt(X_data)
            
            cy = HE.encrypt(y_data)

            # 4. Serialización
            package = {
                "context": HE.to_bytes_context(),
                "pk": HE.to_bytes_public_key(),
                "rlk": HE.to_bytes_relin_key(), 
                "cx": cx.to_bytes(),
                "cy": cy.to_bytes(),
                "n_features": n_features,
                "n_samples": n_samples
            }

            # 5. Envío
            url_ppml = "http://localhost:8001/train_pyfhel"
            response = requests.post(
                url_ppml, 
                data=pickle.dumps(package), 
                headers={'Content-Type': 'application/octet-stream'},
                timeout=300
            )
            
            if response.status_code == 200:
                result_package = pickle.loads(response.content)

                # 6. Reconstrucción y Descifrado de los pesos finales
                enc_w = PyCtxt(pyfhel=HE)
                enc_w.from_bytes(result_package["w"])
                
                # Desciframos (esto usa la llave privada que solo el cliente tiene)
                dec_w = HE.decrypt(enc_w)
                
                # Como el resultado es un vector de slots, tomamos los primeros n_features
                weights = np.round(dec_w[:n_features], 4).tolist()
                
                # El bias puede venir cifrado también
                bias = 0.0
                if "b" in result_package and isinstance(result_package["b"], bytes):
                    enc_b = PyCtxt(pyfhel=HE)
                    enc_b.from_bytes(result_package["b"])
                    bias = round(HE.decrypt(enc_b)[0], 4)
                else:
                    bias = result_package.get("b", 0.0)

                return {
                    "status": "success",
                    "weights": weights,
                    "bias": bias,
                    "training_time": f"{result_package.get('training_time', 0):.4f}s"
                }
            else:
                return {"status": "error", "detail": f"PPML Server Error: {response.text}"}

        except Exception as e:
            return {"status": "error", "detail": f"Client Error: {str(e)}"}