# 🚀 Quick Start - FaceRek

## ✅ La aplicación ya está corriendo!

Todos los servicios están activos:

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:5000
- **PostgreSQL**: localhost:5432

## 📝 Próximos pasos:

### 1. Abrir la aplicación
Abre tu navegador y ve a: **http://localhost:8080**

### 2. Probar el validador
- Arrastra una foto de `data/Fotos grupales/` a la zona de carga
- El sistema detectará las caras y mostrará el resultado

### 3. Gestionar empleados
- Scroll hacia abajo para ver la tabla de empleados
- Click en "+ Nuevo Empleado" para agregar
- Click en "Editar" para modificar
- Click en "Eliminar" para borrar

## 🔧 Comandos útiles:

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs solo del backend
docker-compose logs -f backend

# Reiniciar un servicio
docker-compose restart backend

# Detener todo
docker-compose down

# Reiniciar desde cero (borra la BD)
docker-compose down -v
docker-compose up --build -d
```

## 📊 Estado actual:

- ✅ 23 empleados cargados
- ✅ 21 fotos procesadas (91.3% cobertura)
- ✅ Base de datos PostgreSQL
- ✅ Reconocimiento facial con DeepFace
- ✅ Interfaz web funcional

## 🐛 Troubleshooting:

### La página no carga
```bash
# Verificar que los contenedores estén corriendo
docker-compose ps

# Ver logs para errores
docker-compose logs
```

### Error de conexión a la BD
```bash
# Reiniciar PostgreSQL
docker-compose restart postgres

# Esperar 5 segundos y reiniciar backend
docker-compose restart backend
```

### Resetear todo
```bash
docker-compose down -v
docker-compose up --build -d
```

## 📞 ¿Necesitás ayuda?

Revisá los logs con `docker-compose logs -f` para ver qué está pasando.
