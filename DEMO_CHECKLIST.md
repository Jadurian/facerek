# ✅ Checklist para Demo - FaceRek

## 🚀 Pre-Demo (5 minutos antes)

### 1. Verificar Docker
```bash
docker ps
```
✅ Deberías ver 3 contenedores corriendo:
- facerek_frontend
- facerek_backend  
- facerek_db

### 2. Abrir aplicación
- Frontend: http://localhost:8080
- Verificar que carga correctamente

### 3. Preparar fotos de prueba
Tener listas 2-3 fotos de `data/Fotos grupales/` para mostrar diferentes resultados

---

## 🎬 Guión de Demo (5 minutos)

### **Introducción** (30 seg)
"FaceRek es un sistema de validación automática de fotos para campañas de marketing. Verifica que las personas en las fotos estén autorizadas según su estado laboral y consentimiento de uso de imagen."

### **Demo en vivo** (3 min)

#### 1. Mostrar interfaz (20 seg)
- Zona de carga de fotos
- Tabla de empleados (scroll hacia abajo)
- Mostrar: "Tenemos 21 empleados con fotos cargadas"

#### 2. Validar primera foto (60 seg)
- Arrastrar foto grupal
- Mostrar proceso:
  - ⏳ "Procesando..."
  - 📸 Imagen con rectángulos de colores
  - 🏷️ Nombres sobre cada cara
  - 📋 Lista de personas detectadas

#### 3. Explicar resultados (40 seg)
- 🟢 **Verde**: Autorizado (firmó consentimiento + trabaja actualmente)
- 🟡 **Amarillo**: Advertencia (sin firmar o desconocido)
- 🔴 **Rojo**: Rechazado (ya no trabaja o no autoriza)

#### 4. Validar segunda foto (40 seg)
- Mostrar otro caso (idealmente con resultado diferente)
- Destacar velocidad (caché funcionando)

#### 5. Gestión de empleados (20 seg)
- Mostrar tabla
- Mencionar: "Se pueden agregar, editar y eliminar empleados"
- Mostrar columna "Fotos" con cantidad

### **Tecnología** (1 min)
- 🐍 **Backend**: Python + Flask + DeepFace (VGG-Face)
- 🐘 **Base de datos**: PostgreSQL con índices optimizados
- 🚀 **Performance**: Sistema de caché para validaciones rápidas
- 🐳 **Deployment**: Docker Compose
- 🎨 **Frontend**: HTML5 + JavaScript + Canvas API

### **Próximos pasos** (30 seg)
- ✅ Piloto funcionando
- 🔄 Mejora: Múltiples fotos por empleado (diferentes ángulos + con EPP)
- ☁️ Migración a AWS (RDS + Rekognition + S3)
- 📊 Dashboard con métricas y reportes

---

## 📊 Datos actuales del sistema

- **Empleados**: 23 cargados
- **Fotos procesadas**: 21 (91.3% cobertura)
- **Modelo**: VGG-Face (DeepFace)
- **Precisión**: ~85-90% en condiciones óptimas
- **Tiempo de validación**: 2-5 segundos por foto

---

## 🎯 Puntos clave a destacar

✅ **Automatización**: Valida fotos en segundos vs. revisión manual  
✅ **Visual**: Muestra claramente quién está en cada foto  
✅ **Compliance**: Verifica consentimiento de uso de imagen  
✅ **Escalable**: Arquitectura lista para producción  
✅ **Optimizado**: Caché + índices para mejor performance  

---

## 🐛 Troubleshooting durante la demo

### Si la página no carga:
```bash
docker-compose restart frontend
```

### Si el backend no responde:
```bash
docker-compose restart backend
```

### Si todo falla:
```bash
docker-compose down
docker-compose up -d
# Esperar 30 segundos
```

---

## 💡 Preguntas frecuentes esperadas

**P: ¿Qué pasa si alguien no está en la base de datos?**  
R: Aparece como "Desconocido" con estado WARNING

**P: ¿Funciona con fotos de campo (con casco/EPP)?**  
R: Depende de la foto de entrenamiento. Próxima mejora: múltiples fotos por persona

**P: ¿Cuántas personas puede detectar en una foto?**  
R: Sin límite teórico, probado con hasta 10 personas

**P: ¿Qué tan preciso es?**  
R: 85-90% con buena iluminación y ángulo frontal

**P: ¿Se puede usar en producción?**  
R: Sí, con migración a AWS para mayor escalabilidad

---

## ✨ Cierre

"Este es un piloto funcional que demuestra la viabilidad técnica. El siguiente paso es recolectar múltiples fotos por empleado para mejorar la precisión, especialmente para personal de campo con EPP."
