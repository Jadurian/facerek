from flask import Flask, request, jsonify
from flask_cors import CORS
from database import init_db, get_db
from models import Employee, EmployeePhoto, CampaignPhoto, PhotoDetection
from face_service import get_face_encoding, get_face_encoding_from_bytes, compare_faces
import os
import json
from datetime import datetime
import pickle

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')

@app.route('/api/employees', methods=['GET'])
def get_employees():
    db = get_db()
    employees = db.query(Employee).all()
    result = [{
        'id': e.id,
        'nombre': e.nombre,
        'activo': e.activo,
        'uso_imagen': e.uso_imagen,
        'sigue_trabajando': e.sigue_trabajando,
        'has_photo': len(e.photos) > 0
    } for e in employees]
    db.close()
    return jsonify(result)

@app.route('/api/employees', methods=['POST'])
def create_employee():
    db = get_db()
    data = request.form
    
    employee = Employee(
        nombre=data.get('nombre'),
        activo=data.get('activo'),
        uso_imagen=data.get('uso_imagen'),
        sigue_trabajando=data.get('sigue_trabajando', 'true').lower() == 'true'
    )
    db.add(employee)
    db.commit()
    
    # Procesar foto si existe
    if 'photo' in request.files:
        file = request.files['photo']
        if file.filename:
            filename = f"{employee.id}_{file.filename}"
            filepath = os.path.join(UPLOAD_FOLDER, 'employee_photos', filename)
            file.save(filepath)
            
            encoding = get_face_encoding(filepath)
            if encoding is not None:
                photo = EmployeePhoto(
                    employee_id=employee.id,
                    file_path=filepath,
                    face_encoding=pickle.dumps(encoding)
                )
                db.add(photo)
                db.commit()
    
    db.close()
    return jsonify({'message': 'Empleado creado', 'id': employee.id}), 201

@app.route('/api/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    db = get_db()
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    
    if not employee:
        db.close()
        return jsonify({'error': 'Empleado no encontrado'}), 404
    
    data = request.form
    employee.nombre = data.get('nombre', employee.nombre)
    employee.activo = data.get('activo', employee.activo)
    employee.uso_imagen = data.get('uso_imagen', employee.uso_imagen)
    employee.sigue_trabajando = data.get('sigue_trabajando', str(employee.sigue_trabajando)).lower() == 'true'
    employee.updated_at = datetime.utcnow()
    
    db.commit()
    db.close()
    return jsonify({'message': 'Empleado actualizado'})

@app.route('/api/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    db = get_db()
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    
    if not employee:
        db.close()
        return jsonify({'error': 'Empleado no encontrado'}), 404
    
    db.delete(employee)
    db.commit()
    db.close()
    return jsonify({'message': 'Empleado eliminado'})

@app.route('/api/employees/<int:employee_id>/photo', methods=['POST'])
def upload_employee_photo(employee_id):
    db = get_db()
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    
    if not employee:
        db.close()
        return jsonify({'error': 'Empleado no encontrado'}), 404
    
    if 'photo' not in request.files:
        db.close()
        return jsonify({'error': 'No se envió foto'}), 400
    
    file = request.files['photo']
    filename = f"{employee_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, 'employee_photos', filename)
    file.save(filepath)
    
    encoding = get_face_encoding(filepath)
    if encoding is None:
        db.close()
        return jsonify({'error': 'No se detectó cara en la imagen'}), 400
    
    # Eliminar foto anterior
    for photo in employee.photos:
        db.delete(photo)
    
    photo = EmployeePhoto(
        employee_id=employee_id,
        file_path=filepath,
        face_encoding=pickle.dumps(encoding)
    )
    db.add(photo)
    db.commit()
    db.close()
    
    return jsonify({'message': 'Foto actualizada'})

@app.route('/api/validate-photo', methods=['POST'])
def validate_photo():
    if 'photo' not in request.files:
        return jsonify({'error': 'No se envió foto'}), 400
    
    file = request.files['photo']
    image_bytes = file.read()
    
    print(f"[INFO] Procesando foto: {file.filename}", flush=True)
    
    db = get_db()
    
    try:
        # Obtener todos los encodings de empleados
        employees = db.query(Employee).all()
        known_encodings = []
        employee_map = []
        
        for emp in employees:
            for photo in emp.photos:
                if photo.face_encoding:
                    known_encodings.append(pickle.loads(photo.face_encoding))
                    employee_map.append(emp)
        
        print(f"[INFO] Empleados en BD: {len(known_encodings)}", flush=True)
        
        # Detectar caras en la foto subida
        print("[INFO] Detectando caras...", flush=True)
        face_encodings, face_locations = get_face_encoding_from_bytes(image_bytes)
        print(f"[INFO] Caras detectadas: {len(face_encodings)}", flush=True)
        
        if len(face_encodings) == 0:
            db.close()
            return jsonify({
                'status': 'WARNING',
                'message': 'No se detectaron caras en la imagen',
                'detected_faces': []
            })
        
        detected_faces = []
        overall_status = "OK"
        
        for idx, (encoding, location) in enumerate(zip(face_encodings, face_locations)):
            print(f"[INFO] Comparando cara {idx+1}...", flush=True)
            match_index, confidence = compare_faces(known_encodings, encoding)
            
            if match_index is not None:
                employee = employee_map[match_index]
                print(f"[INFO] Match encontrado: {employee.nombre} (confianza: {confidence:.2f})", flush=True)
                status = "OK"
                reason = None
                
                if not employee.sigue_trabajando:
                    status = "REJECTED"
                    reason = "Ya no trabaja en la compañía"
                    overall_status = "REJECTED"
                elif employee.uso_imagen in ["No firmado", "Espera"]:
                    status = "WARNING"
                    reason = f"Uso de imagen: {employee.uso_imagen}"
                    if overall_status != "REJECTED":
                        overall_status = "WARNING"
                elif employee.uso_imagen == "No autoriza":
                    status = "REJECTED"
                    reason = "No autoriza uso de imagen"
                    overall_status = "REJECTED"
                
                detected_faces.append({
                    'name': employee.nombre,
                    'status': status,
                    'reason': reason,
                    'confidence': round(confidence, 2),
                    'location': location
                })
            else:
                print(f"[WARNING] Cara {idx+1} no reconocida", flush=True)
                detected_faces.append({
                    'name': 'Desconocido',
                    'status': 'WARNING',
                    'reason': 'No está en la base de datos',
                    'confidence': None,
                    'location': location
                })
                if overall_status != "REJECTED":
                    overall_status = "WARNING"
        
        # Guardar validación
        filename = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, 'campaign_photos', filename)
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        campaign_photo = CampaignPhoto(
            file_path=filepath,
            validation_status=overall_status,
            validation_details=json.dumps(detected_faces)
        )
        db.add(campaign_photo)
        db.commit()
        
        rejected_count = sum(1 for f in detected_faces if f['status'] == 'REJECTED')
        warning_count = sum(1 for f in detected_faces if f['status'] == 'WARNING')
        
        message = f"Se detectaron {len(detected_faces)} persona(s)"
        if rejected_count > 0:
            message += f" - {rejected_count} rechazada(s)"
        if warning_count > 0:
            message += f" - {warning_count} con advertencia(s)"
        
        print(f"[INFO] Validación completada: {overall_status}", flush=True)
        
        return jsonify({
            'status': overall_status,
            'message': message,
            'detected_faces': detected_faces
        })
        
    except Exception as e:
        print(f"[ERROR] Error en validación: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error procesando imagen: {str(e)}'}), 500
    finally:
        db.close()

@app.route('/api/debug/employees-with-photos', methods=['GET'])
def debug_employees():
    db = get_db()
    employees = db.query(Employee).all()
    result = []
    for emp in employees:
        result.append({
            'id': emp.id,
            'nombre': emp.nombre,
            'photos_count': len(emp.photos),
            'has_encoding': any(p.face_encoding is not None for p in emp.photos)
        })
    db.close()
    return jsonify(result)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
