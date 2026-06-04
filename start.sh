#!/bin/bash
# Instalamos las dependencias en el Python del runtime (Debian 3.11)
pip3 install --break-system-packages -r requirements.txt --quiet
# Ejecutamos el servidor
python3 servidor_ppal.py
