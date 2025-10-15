# 🚀 Instalación Rápida

## Requisitos
- Docker Desktop instalado y corriendo
- Git (opcional)

## Iniciar la aplicación

```bash
# 1. Clonar o descargar el proyecto
cd c:\Proyectos\facerek

# 2. Iniciar todos los servicios
docker-compose up --build

# 3. Esperar a que todo esté listo (2-3 minutos la primera vez)
```

## Acceder a la aplicación

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:5000
- **PostgreSQL**: localhost:5432

## Detener la aplicación

```bash
docker-compose down
```

## Reiniciar desde cero

```bash
docker-compose down -v
docker-compose up --build
```

## Troubleshooting

### Error de puerto ocupado
Si el puerto 5432, 5000 u 8080 está ocupado:
```bash
# Ver qué está usando el puerto
netstat -ano | findstr :5432
# Matar el proceso o cambiar el puerto en docker-compose.yml
```

### La BD no se inicializa
```bash
# Entrar al contenedor del backend
docker exec -it facerek_backend bash
# Ejecutar manualmente
python init_db.py
```
