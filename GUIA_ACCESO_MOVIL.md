# 📱 Guía de Solución: Acceso Móvil a Bailando Solo

## 🔍 Diagnóstico Realizado

✅ **Servidor corriendo**: Puerto 5001  
✅ **IP Local**: 10.31.240.109  
✅ **Firewall macOS**: Desactivado  
✅ **URL correcta**: http://10.31.240.109:5001/mobile

## ⚠️ Problema Identificado

El servidor está configurado correctamente, pero **Python puede no tener permisos para aceptar conexiones entrantes** desde otros dispositivos en la red.

## 🛠️ Solución Paso a Paso

### Opción 1: Configurar Permisos del Firewall (RECOMENDADO)

Ejecuta estos comandos en la terminal (te pedirá tu contraseña):

```bash
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add $(which python3)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp $(which python3)
```

### Opción 2: Permitir Manualmente en Preferencias del Sistema

1. Abre **Preferencias del Sistema** → **Seguridad y Privacidad**
2. Ve a la pestaña **Firewall**
3. Haz clic en el candado para hacer cambios
4. Haz clic en **Opciones del Firewall**
5. Busca **Python** en la lista
6. Asegúrate de que esté configurado como **"Permitir conexiones entrantes"**

### Opción 3: Desactivar Temporalmente el Firewall

**ADVERTENCIA**: Solo para pruebas, no recomendado para uso prolongado.

1. Abre **Preferencias del Sistema** → **Seguridad y Privacidad**
2. Ve a la pestaña **Firewall**
3. Haz clic en el candado para hacer cambios
4. Haz clic en **Desactivar Firewall**

## 🧪 Verificación

### 1. Página de Diagnóstico

Desde tu móvil, abre:
```
http://10.31.240.109:5001/test-mobile
```

Esta página te mostrará:
- ✅ Estado de conexión al servidor
- ✅ Acceso a la API de biblioteca
- ✅ Acceso a canciones aleatorias
- ✅ Latencia de conexión

### 2. Interfaz Móvil

Si todo funciona correctamente, accede a:
```
http://10.31.240.109:5001/mobile
```

## 📋 Checklist de Solución

- [ ] Ambos dispositivos están en la **misma red WiFi**
- [ ] El servidor está corriendo (`npm run dev`)
- [ ] Python tiene permisos en el firewall
- [ ] No hay VPN o proxy activo en el móvil
- [ ] La IP no ha cambiado (ejecuta `./check-network.sh` para verificar)

## 🔧 Comandos Útiles

### Verificar configuración de red:
```bash
./check-network.sh
```

### Reiniciar el servidor:
```bash
# Detener el servidor actual (Ctrl+C)
# Luego ejecutar:
npm run dev
```

### Verificar qué está usando el puerto 5001:
```bash
lsof -i :5001
```

### Obtener tu IP actual:
```bash
ipconfig getifaddr en0
```

## 🎯 Solución Rápida

Si tienes prisa, ejecuta estos comandos en orden:

```bash
# 1. Verificar configuración
./check-network.sh

# 2. Configurar firewall (ingresa tu contraseña cuando te lo pida)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add $(which python3)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp $(which python3)

# 3. Desde tu móvil, abre:
# http://10.31.240.109:5001/test-mobile
```

## 🆘 Si Aún No Funciona

### Problema: "No se puede acceder a este sitio"

**Causas posibles:**
1. **Diferentes redes WiFi**: Verifica que ambos dispositivos estén en la misma red
2. **Red de invitados**: Algunas redes WiFi de invitados bloquean la comunicación entre dispositivos
3. **Router con aislamiento**: Algunos routers tienen "aislamiento de cliente" activado

**Solución:**
- Verifica el nombre de la red WiFi en ambos dispositivos
- Si estás en una red de invitados, conéctate a la red principal
- Accede a la configuración del router y desactiva "Client Isolation" o "AP Isolation"

### Problema: "Conexión rechazada"

**Causas posibles:**
1. El servidor no está corriendo
2. Python no tiene permisos

**Solución:**
```bash
# Verificar que el servidor esté corriendo
lsof -i :5001

# Si no aparece nada, reinicia el servidor
npm run dev
```

### Problema: La página carga pero no muestra canciones

**Causas posibles:**
1. No hay canciones descargadas
2. Problema con la API

**Solución:**
```bash
# Verifica que existan carpetas con música
ls -la downloads/
```

## 📞 Información de Contacto

Si necesitas más ayuda, proporciona:
- Resultado de `./check-network.sh`
- Resultado de la página `/test-mobile`
- Mensaje de error específico que ves en el móvil

---

**Última actualización**: 2025-12-05
