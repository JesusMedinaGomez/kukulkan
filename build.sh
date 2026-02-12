#!/usr/bin/env bash
# Salir si hay error
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario automáticamente
python create_superuser.py