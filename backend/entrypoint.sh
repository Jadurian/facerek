#!/bin/bash
set -e

echo "Esperando a que PostgreSQL esté listo..."
sleep 5

echo "Inicializando base de datos..."
python init_db.py

echo "Iniciando servidor Flask..."
exec python app.py
