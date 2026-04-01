import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

df = pd.read_csv("./data/framingham.csv")
df = df.dropna()

# Eliminar las columnas inecesarias
df = df.drop(columns=["education", "currentSmoker", "BPMeds", "diabetes", "diaBP", "BMI"])

# Variable objetivo
y = df["TenYearCHD"].values

# Variables predictoras
X = df.drop(columns=["TenYearCHD"]).values

# Separar en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=73
)

# Estandarizar los datos
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Crear el modelo de regresion logistica
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
matriz = confusion_matrix(y_test, y_pred)

print("\n=========== RESULTADOS REGRESIÓN LOGÍSTICA ===========")
print(f"Exactitud (accuracy): {accuracy:.4f}\n")
print("Matriz de confusión:")
print(matriz)
# Verdaderos Negativos: Predijo 0 y era 0
# Falsos positivos: Predijo 1 pero era 0
# Falsos negativos: Predijo 0 pero era 1
# Verdaderos positivos: Predijo 1 y era 1
print("\nReporte de clasificación:")
# Precision: Porcentaje de precision
# recall: verdaderos positivos
# suport: cantidad de ejemplos por clase
print(classification_report(y_test, y_pred))

print("\nPesos aprendidos (coeficientes):")
print(model.coef_)
print("\nBias (intercepto):")
print(model.intercept_)
print("=======================================================\n")