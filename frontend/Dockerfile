FROM node:20.20.2-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps
COPY . ./
RUN npm run build
CMD ["cp", "-r", "build/.", "result_build/"]
