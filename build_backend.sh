#!/bin/bash

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Construyendo binario del servidor con PyInstaller...${NC}"

# 1. Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Creando entorno virtual seguro (venv)...${NC}"
    python3 -m venv venv
fi

# 2. Activar entorno virtual
source venv/bin/activate

# 3. Instalar dependencias incluyendo pyinstaller
echo -e "${BLUE}⬇️  Instalando dependencias...${NC}"
pip install -r requirements.txt
pip install pyinstaller

# 4. Limpiar builds anteriores
echo -e "${BLUE}🧹 Limpiando builds anteriores...${NC}"
rm -rf build/ dist/ server.spec

# 5. Ejecutar PyInstaller
echo -e "${BLUE}🔨 Ejecutando PyInstaller...${NC}"
pyinstaller --name bailandosolo-server --onefile --hidden-import flask_cors --hidden-import yt_dlp server.py

# Verificar si fue exitoso
if [ -f "dist/bailandosolo-server" ]; then
    echo -e "${GREEN}✅ Binario construido exitosamente en dist/bailandosolo-server${NC}"
else
    echo -e "${RED}❌ Hubo un error al construir el binario.${NC}"
    exit 1
fi
