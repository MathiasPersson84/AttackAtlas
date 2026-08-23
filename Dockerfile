FROM node:22-alpine AS frontend
WORKDIR /src
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 ATTACKATLAS_DATA_DIR=/data ATTACKATLAS_STATIC_DIR=/app/static
WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
COPY --from=frontend /src/dist ./static
RUN mkdir -p /data
EXPOSE 7843
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","7843","--workers","1"]
