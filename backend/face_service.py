from deepface import DeepFace
import cv2
import numpy as np
import os
import tempfile

# Caché global del modelo para evitar recargarlo
_model_cache = {}

def get_face_encoding(image_path):
    """Obtiene el embedding de una cara desde una imagen"""
    try:
        embedding = DeepFace.represent(
            img_path=image_path, 
            model_name="VGG-Face",
            detector_backend="skip",
            enforce_detection=False
        )
        return np.array(embedding[0]["embedding"]) if embedding else None
    except:
        return None

def get_face_encoding_from_bytes(image_bytes):
    """Obtiene embeddings de caras desde bytes de imagen - OPTIMIZADO"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name
    
    try:
        # Usar retinaface para mejor detección de múltiples caras
        result = DeepFace.represent(
            img_path=tmp_path,
            model_name="VGG-Face",
            detector_backend="retinaface",  # Mejor para fotos grupales
            enforce_detection=False,
            align=False
        )
        
        face_encodings = []
        face_locations = []
        
        for face_data in result:
            face_encodings.append(np.array(face_data["embedding"]))
            region = face_data.get('facial_area', {})
            if region:
                face_locations.append([
                    region.get('y', 0),
                    region.get('x', 0) + region.get('w', 0),
                    region.get('y', 0) + region.get('h', 0),
                    region.get('x', 0)
                ])
        
        os.unlink(tmp_path)
        return face_encodings, face_locations
    except Exception as e:
        # Fallback a opencv si retinaface falla
        try:
            result = DeepFace.represent(
                img_path=tmp_path,
                model_name="VGG-Face",
                detector_backend="opencv",
                enforce_detection=False,
                align=False
            )
            
            face_encodings = []
            face_locations = []
            
            for face_data in result:
                face_encodings.append(np.array(face_data["embedding"]))
                region = face_data.get('facial_area', {})
                if region:
                    face_locations.append([
                        region.get('y', 0),
                        region.get('x', 0) + region.get('w', 0),
                        region.get('y', 0) + region.get('h', 0),
                        region.get('x', 0)
                    ])
            
            os.unlink(tmp_path)
            return face_encodings, face_locations
        except:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return [], []

def compare_faces(known_encodings, face_encoding, tolerance=0.4):
    """Compara una cara con embeddings conocidos - OPTIMIZADO"""
    if not known_encodings or face_encoding is None:
        return None, 0.0
    
    # Similitud coseno (mejor para VGG-Face)
    similarities = []
    for known_enc in known_encodings:
        # Normalizar vectores
        known_norm = known_enc / (np.linalg.norm(known_enc) + 1e-10)
        face_norm = face_encoding / (np.linalg.norm(face_encoding) + 1e-10)
        # Similitud coseno (1 = idéntico, -1 = opuesto)
        similarity = np.dot(known_norm, face_norm)
        similarities.append(similarity)
    
    if len(similarities) == 0:
        return None, 0.0
    
    best_match_index = np.argmax(similarities)
    best_similarity = similarities[best_match_index]
    
    # Debug: imprimir las 3 mejores similitudes
    sorted_sims = sorted(enumerate(similarities), key=lambda x: x[1], reverse=True)[:3]
    print(f"[DEBUG] Top 3 similitudes: {[(i, round(s, 3)) for i, s in sorted_sims]}", flush=True)
    
    # Similitud coseno: > 0.6 = mismo (más permisivo)
    if best_similarity > tolerance:
        return best_match_index, best_similarity
    
    return None, 0.0
