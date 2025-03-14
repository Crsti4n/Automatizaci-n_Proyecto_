# Usar la imagen oficial de Node.js
FROM node:20

# Definir el directorio de trabajo
WORKDIR /app

# Copiar solo package.json y package-lock.json primero para optimizar cache
COPY package.json package-lock.json ./

# Instalar dependencias
RUN npm install
RUN npm install -g vite

# Copiar el resto del código
COPY . .

# Construir el frontend
RUN npm run build

# Exponer el puerto 5173
EXPOSE 5173

# Comando por defecto para iniciar el frontend
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
