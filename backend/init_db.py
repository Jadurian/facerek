import pandas as pd
import os
from database import init_db, get_db
from models import Employee, EmployeePhoto
from face_service import get_face_encoding
import pickle
import unicodedata

def normalize_name(name):
    """Normaliza un nombre removiendo acentos y caracteres especiales"""
    # Remover acentos
    nfkd = unicodedata.normalize('NFKD', name)
    name_no_accents = ''.join([c for c in nfkd if not unicodedata.combining(c)])
    return name_no_accents.replace(' ', '_')

def find_photo_file(nombre, photos_dir):
    """Busca el archivo de foto correspondiente al nombre"""
    # Listar todos los archivos
    files = os.listdir(photos_dir)
    
    # Normalizar el nombre buscado
    normalized_search = normalize_name(nombre).lower()
    
    # Buscar coincidencia
    for file in files:
        if file.lower().endswith('.jpg'):
            file_normalized = file.replace('.jpg', '').lower()
            if file_normalized == normalized_search:
                return os.path.join(photos_dir, file)
    
    return None

def load_initial_data():
    """Carga datos iniciales desde el Excel y fotos individuales"""
    print("Inicializando base de datos...")
    init_db()
    
    db = get_db()
    
    # Verificar si ya hay datos
    if db.query(Employee).count() > 0:
        print("La base de datos ya tiene datos. Saltando carga inicial.")
        db.close()
        return
    
    # Leer Excel
    excel_path = '../data/Banco de Imágenes 2025 Neuquén FEBRERO.xlsx'
    df = pd.read_excel(excel_path)
    
    print(f"Cargando {len(df)} empleados desde Excel...")
    
    photos_dir = '../data/Fotos individuales'
    
    for _, row in df.iterrows():
        # Normalizar uso_imagen
        uso_imagen = row['Uso imagen']
        if uso_imagen == 'Si':
            uso_imagen = 'Firmado'
        
        # Crear empleado
        employee = Employee(
            nombre=row['Nombre'],
            activo=row['Activo'],
            uso_imagen=uso_imagen,
            sigue_trabajando=row['Sigue trabajando?'] == 'Si'
        )
        db.add(employee)
        db.flush()  # Para obtener el ID
        
        # Buscar foto correspondiente
        photo_path = find_photo_file(row['Nombre'], photos_dir)
        
        if photo_path:
            print(f"  Procesando foto de {row['Nombre']}...")
            encoding = get_face_encoding(photo_path)
            
            if encoding is not None:
                # Copiar foto a uploads
                filename = os.path.basename(photo_path)
                upload_path = f"../uploads/employee_photos/{employee.id}_{filename}"
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                
                import shutil
                shutil.copy(photo_path, upload_path)
                
                photo = EmployeePhoto(
                    employee_id=employee.id,
                    file_path=upload_path,
                    face_encoding=pickle.dumps(encoding),
                    is_primary=True
                )
                db.add(photo)
                print(f"    [OK] Foto procesada correctamente")
            else:
                print(f"    [!] No se detectó cara en la foto")
        else:
            print(f"  [!] No se encontró foto para {row['Nombre']}")
    
    db.commit()
    total_employees = db.query(Employee).count()
    total_photos = db.query(EmployeePhoto).count()
    print(f"\n[OK] Carga completada: {total_employees} empleados")
    print(f"[OK] Fotos procesadas: {total_photos}")
    print(f"[OK] Cobertura: {round(total_photos/total_employees*100, 1)}%")
    db.close()

if __name__ == '__main__':
    load_initial_data()
