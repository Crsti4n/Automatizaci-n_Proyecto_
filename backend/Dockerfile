# Usar la imagen de Python 3.11
FROM python:3.11

# Definir el directorio de trabajo
WORKDIR /backend

# Copiar archivos del backend al contenedor
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 8000
EXPOSE 8000

# Comando por defecto para iniciar el backend
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
