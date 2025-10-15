from database import engine
from models import Base

print("Eliminando todas las tablas...")
Base.metadata.drop_all(bind=engine)
print("[OK] Base de datos limpiada")
