#!/bin/bash

echo "🔍 Verificando configuración de red para acceso móvil..."
echo ""

# Obtener la IP local
echo "📱 Tu IP local es:"
ipconfig getifaddr en0 || ipconfig getifaddr en1
LOCAL_IP=$(ipconfig getifaddr en0 || ipconfig getifaddr en1)
echo ""

# Mostrar el puerto
PORT=5001
echo "🔌 Puerto del servidor: $PORT"
echo ""

# Verificar si el servidor está corriendo
echo "🖥️  Verificando si el servidor está activo..."
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Servidor corriendo en puerto $PORT"
else
    echo "❌ El servidor NO está corriendo en puerto $PORT"
    echo "   Ejecuta: python3 server.py"
fi
echo ""

# Mostrar la URL para móvil
echo "📲 URL para acceder desde tu móvil:"
echo "   http://$LOCAL_IP:$PORT/mobile"
echo ""

# Generar QR code si está disponible
echo "🔲 Generando QR code..."
if command -v qrencode &> /dev/null; then
    qrencode -t ANSIUTF8 "http://$LOCAL_IP:$PORT/mobile"
else
    echo "   (Instala qrencode para ver el QR: brew install qrencode)"
fi
echo ""

# Verificar firewall
echo "🔥 Verificando Firewall de macOS..."
if /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate | grep -q "enabled"; then
    echo "⚠️  El Firewall está ACTIVADO"
    echo "   Esto puede bloquear las conexiones desde tu móvil"
    echo ""
    echo "   Para permitir conexiones, ejecuta:"
    echo "   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add $(which python3)"
    echo "   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp $(which python3)"
else
    echo "✅ El Firewall está desactivado"
fi
echo ""

# Instrucciones finales
echo "📋 Pasos para conectar desde tu móvil:"
echo "   1. Asegúrate de que tu móvil esté en la MISMA red WiFi"
echo "   2. Abre el navegador en tu móvil"
echo "   3. Ingresa: http://$LOCAL_IP:$PORT/mobile"
echo ""
echo "   Si no funciona, ejecuta estos comandos:"
echo "   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add $(which python3)"
echo "   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp $(which python3)"
