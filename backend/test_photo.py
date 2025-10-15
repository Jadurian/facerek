from deepface import DeepFace
import cv2

# Probar con una foto
photo_path = "../data/Fotos individuales/Diego_Pomilio.jpg"

print(f"Probando: {photo_path}")

# Ver si la imagen se puede cargar
img = cv2.imread(photo_path)
if img is None:
    print("ERROR: No se pudo cargar la imagen")
else:
    print(f"Imagen cargada: {img.shape}")
    
    # Intentar detectar caras
    try:
        faces = DeepFace.extract_faces(
            img_path=photo_path,
            detector_backend="opencv",
            enforce_detection=False
        )
        print(f"Caras detectadas: {len(faces)}")
        
        # Intentar obtener embedding
        embedding = DeepFace.represent(
            img_path=photo_path,
            model_name="VGG-Face",
            detector_backend="opencv",
            enforce_detection=False
        )
        print(f"Embedding obtenido: {len(embedding[0]['embedding'])} dimensiones")
        print("SUCCESS!")
    except Exception as e:
        print(f"ERROR: {e}")
