# 🎯 FaceRek - Sistema de Validación de Fotos para Campañas

Sistema de reconocimiento facial para validar si las personas en fotos de campañas de marketing están autorizadas para su uso según su estado laboral y consentimiento de uso de imagen.

## 🚀 Características

- ✅ **Validación automática** de fotos grupales e individuales
- 👥 **Gestión de empleados** con información de estado laboral y consentimiento
- 🔍 **Reconocimiento facial** usando face_recognition (dlib)
- 📊 **Base de datos PostgreSQL** escalable
- 🐳 **Docker Compose** para deployment simple
- 🎨 **Interfaz web intuitiva** con drag & drop

## 📋 Requisitos Previos

- Python 3.8+
- Docker y Docker Compose
- CMake (para compilar dlib/face_recognition)

### Instalación de CMake en Windows

```bash
# Opción 1: Con Chocolatey
choco install cmake

# Opción 2: Descargar desde https://cmake.org/download/
```

## 🛠️ Instalación

### Opción 1: Docker (Recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/facerek.git
cd facerek

# 2. Iniciar todos los servicios
docker-compose up --build

# 3. Acceder a la aplicación
# Frontend: http://localhost:8080
# Backend API: http://localhost:5000
```

¡Listo! La aplicación cargará automáticamente los 23 empleados y sus fotos.

### Opción 2: Instalación Local

Ver [INSTALL.md](INSTALL.md) para instalación sin Docker.

## 📖 Uso

### Validar Foto de Campaña

1. Arrastra una foto a la zona de carga o haz clic para seleccionar
2. El sistema detectará automáticamente las caras
3. Recibirás un resultado:
   - **✅ OK**: Todas las personas están autorizadas
   - **⚠️ WARNING**: Hay personas sin firmar o en espera
   - **❌ REJECTED**: Hay personas que ya no trabajan o no autorizan

### Gestionar Empleados

- **Agregar**: Click en "+ Nuevo Empleado"
- **Editar**: Click en "Editar" en la fila del empleado
- **Eliminar**: Click en "Eliminar" (requiere confirmación)
- **Subir foto**: Al crear/editar, selecciona una foto de referencia

## 🏗️ Arquitectura

```
facerek/
├── backend/
│   ├── app.py              # API Flask
│   ├── models.py           # Modelos SQLAlchemy
│   ├── database.py         # Configuración DB
│   ├── face_service.py     # Lógica de reconocimiento facial
│   ├── init_db.py          # Script de inicialización
│   └── requirements.txt
├── frontend/
│   ├── index.html          # Interfaz principal
│   ├── app.js              # Lógica del cliente
│   └── styles.css          # Estilos
├── data/
│   ├── Fotos individuales/ # Fotos de referencia
│   ├── Fotos grupales/     # Fotos de prueba
│   └── *.xlsx              # Excel con datos iniciales
├── uploads/                # Fotos subidas (generado)
├── docker-compose.yml      # PostgreSQL
└── .env                    # Variables de entorno
```

## 🔧 API Endpoints

### Empleados

- `GET /api/employees` - Lista todos los empleados
- `POST /api/employees` - Crea un nuevo empleado
- `PUT /api/employees/{id}` - Actualiza un empleado
- `DELETE /api/employees/{id}` - Elimina un empleado
- `POST /api/employees/{id}/photo` - Sube foto de referencia

### Validación

- `POST /api/validate-photo` - Valida una foto de campaña

## 📊 Modelo de Datos

### Employees
- nombre, activo (ubicación), uso_imagen, sigue_trabajando

### Employee Photos
- Foto de referencia + face_encoding (vector facial)

### Campaign Photos
- Fotos validadas + resultado + detalles

### Photo Detections
- Relación entre fotos de campaña y empleados detectados

## 🚀 Escalabilidad Futura

### Migración a AWS

1. **Base de datos**: PostgreSQL → AWS RDS
2. **Reconocimiento facial**: face_recognition → AWS Rekognition
3. **Storage**: Local → S3
4. **Backend**: Local → ECS/Lambda
5. **Frontend**: Local → S3 + CloudFront

### Mejoras Planificadas

- [ ] Autenticación de usuarios
- [ ] Historial de validaciones
- [ ] Dashboard con métricas
- [ ] Exportar reportes
- [ ] API para integración con otras herramientas
- [ ] Notificaciones por email
- [ ] Búsqueda y filtros avanzados

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es privado y de uso interno.

## 👨‍💻 Autor

Desarrollado para el equipo de Marketing - 2025

## 🐛 Troubleshooting

### Error al instalar face_recognition

```bash
# Instalar dlib primero
pip install cmake
pip install dlib
pip install face-recognition
```

### PostgreSQL no inicia

```bash
# Verificar que el puerto 5432 esté libre
docker-compose down
docker-compose up -d
```

### No se detectan caras

- Verifica que la foto tenga buena iluminación
- La cara debe estar visible y frontal
- Tamaño mínimo recomendado: 200x200px por cara

## 📞 Soporte

Para problemas o consultas, contacta al equipo de desarrollo.
