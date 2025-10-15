"""Script para reprocesar todas las fotos con la configuración actual"""
from database import get_db
from models import Employee, EmployeePhoto
from face_service import get_face_encoding
import pickle

def reprocess_all_photos():
    db = get_db()
    
    photos = db.query(EmployeePhoto).all()
    print(f"Reprocesando {len(photos)} fotos...")
    
    success = 0
    failed = 0
    
    for photo in photos:
        try:
            print(f"Procesando: {photo.employee.nombre}...")
            encoding = get_face_encoding(photo.file_path)
            
            if encoding is not None:
                photo.face_encoding = pickle.dumps(encoding)
                success += 1
                print(f"  ✓ OK")
            else:
                failed += 1
                print(f"  ✗ FALLO")
        except Exception as e:
            failed += 1
            print(f"  ✗ ERROR: {e}")
    
    db.commit()
    db.close()
    
    print(f"\n✓ Exitosos: {success}")
    print(f"✗ Fallidos: {failed}")

if __name__ == '__main__':
    reprocess_all_photos()
