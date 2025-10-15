const API_URL = 'http://localhost:5000/api';

// Elementos del DOM
const uploadArea = document.getElementById('uploadArea');
const photoInput = document.getElementById('photoInput');
const validationResult = document.getElementById('validationResult');
const imagePreview = document.getElementById('imagePreview');
const imageCanvas = document.getElementById('imageCanvas');
const employeesBody = document.getElementById('employeesBody');
const employeeModal = document.getElementById('employeeModal');
const employeeForm = document.getElementById('employeeForm');
const addEmployeeBtn = document.getElementById('addEmployeeBtn');
const closeModal = document.querySelector('.close');
const cancelBtn = document.getElementById('cancelBtn');

// Drag & Drop
uploadArea.addEventListener('click', () => photoInput.click());
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.background = '#f0f4ff';
});
uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.background = '';
});
uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.background = '';
    const file = e.dataTransfer.files[0];
    if (file) validatePhoto(file);
});
photoInput.addEventListener('change', (e) => {
    if (e.target.files[0]) validatePhoto(e.target.files[0]);
});

// Validar foto
async function validatePhoto(file) {
    validationResult.innerHTML = '<p>⏳ Procesando...</p>';
    imagePreview.style.display = 'none';
    
    const formData = new FormData();
    formData.append('photo', file);
    
    try {
        const response = await fetch(`${API_URL}/validate-photo`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        displayValidationResult(data, file);
    } catch (error) {
        validationResult.innerHTML = '<p class="result-card result-rejected">❌ Error al procesar la foto</p>';
    }
}

function displayValidationResult(data, file) {
    const statusClass = `result-${data.status.toLowerCase()}`;
    const statusIcon = data.status === 'OK' ? '✅' : data.status === 'WARNING' ? '⚠️' : '❌';
    
    let html = `
        <div class="result-card ${statusClass}">
            <h3>${statusIcon} ${data.status}</h3>
            <p>${data.message}</p>
        </div>
    `;
    
    if (data.detected_faces && data.detected_faces.length > 0) {
        html += '<div style="margin-top: 20px;">';
        data.detected_faces.forEach(face => {
            const faceIcon = face.status === 'OK' ? '✅' : face.status === 'WARNING' ? '⚠️' : '❌';
            html += `
                <div class="face-item">
                    <strong>${faceIcon} ${face.name}</strong>
                    ${face.confidence ? `<span style="color: #666;"> (${Math.round(face.confidence * 100)}% confianza)</span>` : ''}
                    ${face.reason ? `<br><small>${face.reason}</small>` : ''}
                </div>
            `;
        });
        html += '</div>';
        
        // Dibujar imagen con caras detectadas
        drawImageWithFaces(file, data.detected_faces);
    }
    
    validationResult.innerHTML = html;
}

function drawImageWithFaces(file, faces) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
            const ctx = imageCanvas.getContext('2d');
            const maxWidth = 800;
            const scale = Math.min(1, maxWidth / img.width);
            
            imageCanvas.width = img.width * scale;
            imageCanvas.height = img.height * scale;
            
            ctx.drawImage(img, 0, 0, imageCanvas.width, imageCanvas.height);
            
            faces.forEach(face => {
                if (face.location) {
                    const [top, right, bottom, left] = face.location;
                    const x = left * scale;
                    const y = top * scale;
                    const width = (right - left) * scale;
                    const height = (bottom - top) * scale;
                    
                    // Color según estado
                    const color = face.status === 'OK' ? '#28a745' : 
                                  face.status === 'WARNING' ? '#ffc107' : '#dc3545';
                    
                    // Rectángulo
                    ctx.strokeStyle = color;
                    ctx.lineWidth = 3;
                    ctx.strokeRect(x, y, width, height);
                    
                    // Etiqueta
                    ctx.fillStyle = color;
                    ctx.fillRect(x, y - 30, width, 30);
                    ctx.fillStyle = 'white';
                    ctx.font = 'bold 16px Arial';
                    ctx.fillText(face.name, x + 5, y - 8);
                }
            });
            
            imagePreview.style.display = 'block';
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

// Cargar empleados
async function loadEmployees() {
    try {
        const response = await fetch(`${API_URL}/employees`);
        const employees = await response.json();
        
        employeesBody.innerHTML = '';
        employees.forEach(emp => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${emp.nombre}</td>
                <td>${emp.activo}</td>
                <td>${emp.uso_imagen}</td>
                <td>
                    <span class="status-badge ${emp.sigue_trabajando ? 'status-active' : 'status-inactive'}">
                        ${emp.sigue_trabajando ? 'Sí' : 'No'}
                    </span>
                </td>
                <td>${emp.has_photo ? '✅' : '❌'}</td>
                <td>
                    <button onclick="editEmployee(${emp.id})" class="btn-primary" style="padding: 5px 15px; margin-right: 5px;">Editar</button>
                    <button onclick="deleteEmployee(${emp.id})" class="btn-danger">Eliminar</button>
                </td>
            `;
            employeesBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error cargando empleados:', error);
    }
}

// Modal
addEmployeeBtn.addEventListener('click', () => {
    document.getElementById('modalTitle').textContent = 'Nuevo Empleado';
    employeeForm.reset();
    document.getElementById('employeeId').value = '';
    employeeModal.style.display = 'block';
});

closeModal.addEventListener('click', () => {
    employeeModal.style.display = 'none';
});

cancelBtn.addEventListener('click', () => {
    employeeModal.style.display = 'none';
});

// Guardar empleado
employeeForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('nombre', document.getElementById('employeeName').value);
    formData.append('activo', document.getElementById('employeeActivo').value);
    formData.append('uso_imagen', document.getElementById('employeeUsoImagen').value);
    formData.append('sigue_trabajando', document.getElementById('employeeSigueTrabajando').checked);
    
    const photoFile = document.getElementById('employeePhoto').files[0];
    if (photoFile) {
        formData.append('photo', photoFile);
    }
    
    const employeeId = document.getElementById('employeeId').value;
    const url = employeeId ? `${API_URL}/employees/${employeeId}` : `${API_URL}/employees`;
    const method = employeeId ? 'PUT' : 'POST';
    
    try {
        await fetch(url, {
            method: method,
            body: formData
        });
        
        employeeModal.style.display = 'none';
        loadEmployees();
    } catch (error) {
        alert('Error al guardar empleado');
    }
});

// Editar empleado
async function editEmployee(id) {
    try {
        const response = await fetch(`${API_URL}/employees`);
        const employees = await response.json();
        const employee = employees.find(e => e.id === id);
        
        if (employee) {
            document.getElementById('modalTitle').textContent = 'Editar Empleado';
            document.getElementById('employeeId').value = employee.id;
            document.getElementById('employeeName').value = employee.nombre;
            document.getElementById('employeeActivo').value = employee.activo;
            document.getElementById('employeeUsoImagen').value = employee.uso_imagen;
            document.getElementById('employeeSigueTrabajando').checked = employee.sigue_trabajando;
            employeeModal.style.display = 'block';
        }
    } catch (error) {
        alert('Error al cargar empleado');
    }
}

// Eliminar empleado
async function deleteEmployee(id) {
    if (confirm('¿Estás seguro de eliminar este empleado?')) {
        try {
            await fetch(`${API_URL}/employees/${id}`, {
                method: 'DELETE'
            });
            loadEmployees();
        } catch (error) {
            alert('Error al eliminar empleado');
        }
    }
}

// Cargar empleados al inicio
loadEmployees();
