# 📦 Especificación: Procesamiento de Lotes

## 🎯 Objetivo

Permitir validar múltiples fotos simultáneamente y generar un reporte consolidado indicando si cada foto es apta o no para uso en campañas.

---

## 📋 Casos de Uso

### **Caso 1: Marketing recibe 150 fotos de un evento**
```
Entrada: Carpeta con 150 fotos
Proceso: Validar todas automáticamente
Salida: Reporte Excel + Carpetas organizadas
```

### **Caso 2: Revisión mensual de fotos**
```
Entrada: Fotos del mes
Proceso: Validar y generar estadísticas
Salida: Dashboard + Reporte PDF
```

### **Caso 3: Validación pre-publicación**
```
Entrada: Fotos seleccionadas para campaña
Proceso: Validación rápida
Salida: Aprobación/Rechazo inmediato
```

---

## 🔧 Implementación Propuesta

### **Fase 1: MVP (1-2 semanas)**

#### Frontend
```javascript
// Subir múltiples archivos
<input type="file" multiple accept="image/*">

// O subir ZIP
<input type="file" accept=".zip">

// Mostrar progreso
<div class="progress-bar">
  Procesando: 45/150 fotos (30%)
</div>
```

#### Backend
```python
@app.route('/api/batch/validate', methods=['POST'])
def validate_batch():
    files = request.files.getlist('photos')
    batch_id = generate_batch_id()
    
    # Procesar en background
    process_batch_async(batch_id, files)
    
    return {
        'batch_id': batch_id,
        'total_photos': len(files),
        'status': 'processing'
    }

def process_batch_async(batch_id, files):
    results = []
    for file in files:
        result = validate_single_photo(file)
        results.append(result)
        update_progress(batch_id, len(results))
    
    generate_report(batch_id, results)
    send_notification(batch_id)
```

#### Reporte Excel
```python
import pandas as pd

def generate_report(batch_id, results):
    df = pd.DataFrame(results)
    
    # Columnas
    df['Foto'] = df['filename']
    df['Personas Detectadas'] = df['faces_count']
    df['Estado'] = df['status']  # OK, WARNING, REJECTED
    df['Razón'] = df['reason']
    df['Personas'] = df['detected_names']
    
    # Agregar resumen
    summary = {
        'Total': len(df),
        'Aprobadas': len(df[df['status'] == 'OK']),
        'Advertencias': len(df[df['status'] == 'WARNING']),
        'Rechazadas': len(df[df['status'] == 'REJECTED'])
    }
    
    # Guardar
    filename = f'reporte_lote_{batch_id}.xlsx'
    with pd.ExcelWriter(filename) as writer:
        df.to_excel(writer, sheet_name='Resultados', index=False)
        pd.DataFrame([summary]).to_excel(writer, sheet_name='Resumen', index=False)
    
    return filename
```

---

### **Fase 2: Optimizado (2-3 semanas)**

#### Procesamiento Paralelo
```python
from concurrent.futures import ThreadPoolExecutor
import asyncio

async def process_batch_parallel(batch_id, files):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(validate_single_photo, file)
            for file in files
        ]
        
        results = []
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            await update_progress_realtime(batch_id, len(results))
    
    return results
```

#### WebSocket para Progreso en Tiempo Real
```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app)

def update_progress_realtime(batch_id, processed):
    socketio.emit('batch_progress', {
        'batch_id': batch_id,
        'processed': processed,
        'percentage': (processed / total) * 100
    })
```

#### Organización Automática de Fotos
```python
def organize_photos(batch_id, results):
    base_path = f'output/{batch_id}'
    
    # Crear carpetas
    os.makedirs(f'{base_path}/aprobadas', exist_ok=True)
    os.makedirs(f'{base_path}/advertencias', exist_ok=True)
    os.makedirs(f'{base_path}/rechazadas', exist_ok=True)
    
    # Copiar fotos a carpetas según resultado
    for result in results:
        src = result['file_path']
        if result['status'] == 'OK':
            dst = f'{base_path}/aprobadas/{result["filename"]}'
        elif result['status'] == 'WARNING':
            dst = f'{base_path}/advertencias/{result["filename"]}'
        else:
            dst = f'{base_path}/rechazadas/{result["filename"]}'
        
        shutil.copy(src, dst)
```

---

### **Fase 3: Producción (3-4 semanas)**

#### Cola de Tareas con Celery
```python
from celery import Celery

celery = Celery('facerek', broker='redis://localhost:6379')

@celery.task
def process_batch_task(batch_id, file_paths):
    results = []
    for path in file_paths:
        result = validate_single_photo(path)
        results.append(result)
        
        # Actualizar progreso
        process_batch_task.update_state(
            state='PROGRESS',
            meta={'current': len(results), 'total': len(file_paths)}
        )
    
    # Generar reporte
    report_path = generate_report(batch_id, results)
    
    # Enviar email
    send_email_notification(batch_id, report_path)
    
    return {'status': 'completed', 'report': report_path}
```

#### Almacenamiento en S3
```python
import boto3

s3 = boto3.client('s3')

def upload_to_s3(file_path, bucket='facerek-reports'):
    key = f'reports/{batch_id}/{filename}'
    s3.upload_file(file_path, bucket, key)
    
    # Generar URL firmada (válida 7 días)
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=604800
    )
    
    return url
```

---

## 📊 Formato de Reporte

### **Excel - Hoja "Resultados"**
```
| Foto          | Personas | Estado    | Razón                    | Nombres Detectados        |
|---------------|----------|-----------|--------------------------|---------------------------|
| IMG_001.jpg   | 3        | ✅ OK     | Todos autorizados        | Juan, María, Pedro        |
| IMG_002.jpg   | 2        | ⚠️ WARNING| 1 sin firmar            | Ana, Desconocido          |
| IMG_003.jpg   | 4        | ❌ REJECTED| 1 no trabaja más        | Luis (NO TRABAJA), ...    |
| IMG_004.jpg   | 0        | ⚠️ WARNING| Sin personas detectadas  | -                         |
| IMG_005.jpg   | 5        | ✅ OK     | Todos autorizados        | Carlos, Sofia, ...        |
```

### **Excel - Hoja "Resumen"**
```
┌─────────────────────────────────────────┐
│ RESUMEN DEL LOTE                        │
├─────────────────────────────────────────┤
│ Lote ID: batch_20250121_143022          │
│ Fecha: 21/01/2025 14:30                 │
│ Usuario: marketing@empresa.com          │
├─────────────────────────────────────────┤
│ Total de fotos: 150                     │
│ Aprobadas: 120 (80.0%)                  │
│ Con advertencias: 15 (10.0%)            │
│ Rechazadas: 15 (10.0%)                  │
├─────────────────────────────────────────┤
│ Personas únicas detectadas: 45          │
│ Fotos sin personas: 3                   │
│ Tiempo de procesamiento: 8 min 23 seg   │
└─────────────────────────────────────────┘
```

### **Excel - Hoja "Personas"**
```
| Nombre          | Veces Detectado | Estado Laboral | Uso Imagen |
|-----------------|-----------------|----------------|------------|
| Juan Pérez      | 23              | Activo         | Firmado    |
| María García    | 18              | Activo         | Firmado    |
| Pedro López     | 15              | Activo         | No firmado |
| Luis Martínez   | 8               | NO TRABAJA     | Firmado    |
```

---

## 🎨 UI/UX Propuesta

### **Pantalla: Nuevo Lote**
```
┌─────────────────────────────────────────────────────────┐
│  📦 Validar Lote de Fotos                                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Nombre del lote:                                        │
│  [Campaña Verano 2025________________]                  │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  📸 Arrastra fotos aquí o haz clic             │    │
│  │                                                 │    │
│  │  Formatos: JPG, PNG                            │    │
│  │  Máximo: 500 fotos por lote                    │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  O subir archivo ZIP:                                    │
│  [Seleccionar ZIP]                                       │
│                                                          │
│  Notificar por email al completar:                       │
│  ☑ marketing@empresa.com                                │
│                                                          │
│  [Cancelar]  [Procesar Lote]                            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### **Pantalla: Procesando**
```
┌─────────────────────────────────────────────────────────┐
│  🔄 Procesando Lote: Campaña Verano 2025                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Progreso: 45 / 150 fotos (30%)                         │
│  ████████░░░░░░░░░░░░░░░░░░░░                          │
│                                                          │
│  Tiempo transcurrido: 2 min 15 seg                      │
│  Tiempo estimado restante: 5 min 10 seg                 │
│                                                          │
│  Resultados parciales:                                   │
│  ✅ Aprobadas: 32                                        │
│  ⚠️ Advertencias: 8                                      │
│  ❌ Rechazadas: 5                                        │
│                                                          │
│  [Cancelar Proceso]                                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### **Pantalla: Resultados**
```
┌─────────────────────────────────────────────────────────┐
│  ✅ Lote Completado: Campaña Verano 2025                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📊 Resumen:                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ ✅ Aprobadas │  │ ⚠️ Advertencias│  │ ❌ Rechazadas│ │
│  │     120      │  │      15       │  │      15      │ │
│  │    (80%)     │  │    (10%)      │  │    (10%)     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  📥 Descargas:                                           │
│  [📊 Reporte Excel]  [📁 Fotos Organizadas (ZIP)]       │
│                                                          │
│  📋 Detalles:                                            │
│  - Personas únicas: 45                                   │
│  - Tiempo total: 8 min 23 seg                           │
│  - Procesado: 21/01/2025 14:38                          │
│                                                          │
│  [Ver Detalles]  [Nuevo Lote]                           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Plan de Implementación

### **Sprint 1 (1 semana): MVP**
- [ ] Subir múltiples archivos
- [ ] Procesar secuencialmente
- [ ] Generar Excel básico
- [ ] Mostrar resultados

### **Sprint 2 (1 semana): Mejoras**
- [ ] Procesamiento paralelo
- [ ] Progreso en tiempo real
- [ ] Organizar fotos en carpetas
- [ ] Mejorar reporte Excel

### **Sprint 3 (1 semana): Producción**
- [ ] Cola de tareas (Celery)
- [ ] Notificaciones por email
- [ ] Historial de lotes
- [ ] API para integración

---

## 💰 Estimación de Costos

| Ítem | Tiempo | Costo |
|------|--------|-------|
| Desarrollo MVP | 1 semana | $3-5K |
| Mejoras | 1 semana | $3-5K |
| Producción | 1 semana | $3-5K |
| Testing | 2 días | $1-2K |
| **TOTAL** | **3 semanas** | **$10-17K** |

---

## ✅ Criterios de Aceptación

1. ✅ Subir hasta 500 fotos simultáneamente
2. ✅ Procesar en menos de 10 minutos (500 fotos)
3. ✅ Generar reporte Excel con todas las columnas
4. ✅ Organizar fotos en carpetas según resultado
5. ✅ Mostrar progreso en tiempo real
6. ✅ Enviar notificación al completar
7. ✅ Permitir descargar resultados
8. ✅ Mantener historial de lotes

---

**¿Procedemos con la implementación?**
