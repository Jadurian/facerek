# 📁 Directorio de Datos

Este directorio contiene las fotos de referencia y prueba del sistema.

## 📂 Estructura

```
data/
├── Fotos individuales/     # Fotos de referencia de empleados
├── Fotos grupales/         # Fotos de prueba para validación
└── *.xlsx                  # Excel con datos iniciales
```

## 🚨 Importante

Las fotos **NO están incluidas en el repositorio** por privacidad y tamaño.

### Para configurar el sistema:

1. **Fotos individuales**: Coloca las fotos de referencia de cada empleado en `Fotos individuales/`
   - Formato: `Nombre_Apellido.jpg`
   - Ejemplo: `Juan_Perez.jpg`

2. **Fotos grupales**: (Opcional) Coloca fotos de prueba en `Fotos grupales/`
   - Para testing del sistema de validación

3. **Excel**: El archivo Excel con los datos de empleados debe estar en este directorio

## 🔄 Carga Inicial

Al ejecutar `docker-compose up`, el sistema:
- Cargará automáticamente los empleados desde el Excel
- Procesará las fotos de `Fotos individuales/` y generará los encodings faciales
- Las fotos se copiarán a `uploads/employee_photos/` para uso del sistema

## 📝 Nota

Si no tienes las fotos, puedes:
- Agregar empleados manualmente desde la interfaz web
- Subir fotos individuales al crear/editar empleados
