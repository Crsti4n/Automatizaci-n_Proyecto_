# Usar la imagen oficial de Python 3.11
FROM python:3.11

# Definir el directorio de trabajo
WORKDIR /backend

# Copiar solo los archivos necesarios para instalar dependencias primero (mejora la caché de Docker)
COPY requirements.txt .

# Instalar dependencias antes de copiar el código completo (mejora la velocidad de construcción)
RUN pip install --no-cache-dir -r requirements.txt

# Ahora copiamos todo el código del backend
COPY . .

# Exponer el puerto 8000
EXPOSE 8000

# Comando por defecto para iniciar el backend
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
