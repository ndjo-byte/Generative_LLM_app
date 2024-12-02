# Utilizar una imagen de Python
FROM python:3.12-slim

# Establecer el directorio del contendor
WORKDIR /app

# Copiamos los archivos al directorio del contenedor
COPY . /app

# Instalar las dependecias
RUN pip install -r requirements.txt

# Exponer el puerto en el que la aplicación está corriendo en el contenedor
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]