import torch
import tenseal as ts
import pandas as pd
import random
from time import time

import numpy as np
import matplotlib.pyplot as plt

# Semilla aleatoria para mezclar datos
torch.random.manual_seed(73)
random.seed(73)

# x: Caracteristicas del dataset
# y: Datos a predecir
def split_train_test(x, y, test_ratio=0.3):
    idxs = [i for i in range(len(x))]
    # Desordena los indices
    random.shuffle(idxs)
    # Delimitador entre test y train data
    delim = int(len(x) * test_ratio)
    test_idxs, train_idxs = idxs[:delim], idxs[delim:]
    return x[train_idxs], y[train_idxs], x[test_idxs], y[test_idxs]

def heart_disease_data():
    data = pd.read_csv("./data/framingham.csv")
    # Elimina filas con valores perdidos
    data = data.dropna()
    # Elimina algunas columnas 
    data = data.drop(columns=["education", "currentSmoker", "BPMeds", "diabetes", "diaBP", "BMI"])
    # Balance de datos
    grouped = data.groupby("TenYearCHD")
    data = grouped.apply(lambda x: x.sample(grouped.size().min(), random_state=73).reset_index(drop=True))
    # Extraer etiquetas
    y = torch.tensor(data["TenYearCHD"].values).float().unsqueeze(1)
    data = data.drop(columns=["TenYearCHD"])
    # Estandarizar los datos
    # Convertir los datos a un tensor de entrada
    x = torch.tensor(data.values).float()
    return split_train_test(x, y)

def random_data(m=1024, n=2):
    # Datos separables por la linea y = x
    x_train = torch.rand(m, n)
    x_test = torch.randn(m // 2, n)
    y_train = (x_train[:, 0] >= x_train[:, 1]).float().unsqueeze(0).t()
    y_test = (x_test[:, 0] >= x_test[:, 1]).float().unsqueeze(0).t()
    return x_train, y_train, x_test, y_test

# Se puede utilizar cualquiera de los dos
# x_train, y_train, x_test, y_test = random_data()
x_train, y_train, x_test, y_test = heart_disease_data()

print("\n===================== DATA SUMMARY =====================")
print("1) Dimensiones del conjunto de entrenamiento:")
print(f"   - x_train: {x_train.shape} → características de los pacientes")
print(f"       * {x_train.shape[0]} pacientes para entrenar")
print(f"       * {x_train.shape[1]} características por paciente")
print(f"   - y_train: {y_train.shape} → etiquetas (0 = sano, 1 = riesgo)")

print("\n2) Dimensiones del conjunto de prueba:")
print(f"   - x_test: {x_test.shape} → características de pacientes nunca vistos")
print(f"   - y_test: {y_test.shape} → etiquetas reales para evaluar al modelo")
print("========================================================\n")

# Definicion del modelo
class LR(torch.nn.Module):
    def __init__(self, n_features):
        super(LR, self).__init__()
        self.lr = torch.nn.Linear(n_features, 1)
    
    # Aplica la funcion sigmoide
    def forward(self, x):
        out = torch.sigmoid(self.lr(x))
        return out
    
n_features = x_train.shape[1] # El modelo tendra 9 entradas
model = LR(n_features)
# Usar la gradiente descendiente con un radio de aprendizaje = 1
optim = torch.optim.SGD(model.parameters(), lr=1)
# Funcion de perdida (BCE calcula el error acumulado)
criterion = torch.nn.BCELoss()

# Definir el numero de epocas para ambos entrenamientos plano y encriptado
EPOCHS = 5

# Aprendizaje
def train(model, optim, criterion, x, y, epochs=EPOCHS):
    for e in range(1, epochs + 1):
        optim.zero_grad()
        out = model(x)
        loss = criterion(out, y)
        loss.backward()
        optim.step()
        print(f"Época {e}: pérdida (loss) = {loss.item():.6f}")
    return model

model = train(model, optim, criterion, x_train, y_train)

# Que tan bien predice el modelo
def accuracy(model, x, y):
    out = model(x)
    correct = torch.abs(y - out) < 0.5
    return correct.float().mean()

plain_accuracy = accuracy(model, x_test, y_test)
print(f"Exactitud (accuracy) en el conjunto de prueba: {plain_accuracy:.4f}")