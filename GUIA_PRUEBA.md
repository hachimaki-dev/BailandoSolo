# Guía de Prueba - BailandoSolo

## Pasos para Probar la Aplicación

### 1. Iniciar el Servidor Python

Abre una terminal en la carpeta del proyecto y ejecuta:

```powershell
# Activar el entorno virtual
.\venv\Scripts\Activate.ps1

# Iniciar el servidor
python server.py
```

El servidor debería iniciar en `http://localhost:5001`

### 2. Iniciar la Aplicación Electron

Abre otra terminal y ejecuta:

```powershell
# Permitir ejecución de scripts (si es necesario)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Iniciar Electron
npm start
```

### 3. Verificar Funcionalidades

#### A. Reproducción desde "Juego Rápido"
1. En la vista principal (Downloader), deberías ver una sección "Juego Rápido (Biblioteca)"
2. Haz clic en cualquier cartucho de canción
3. **Verificar**:
   - ✅ La canción comienza a reproducirse
   - ✅ Se muestra la carátula en el reproductor (ya sea la descargada o una random)
   - ✅ El visualizador circular muestra las frecuencias de audio
   - ✅ La barra de progreso se actualiza

#### B. Reproducción desde Biblioteca
1. Ve a la vista "Biblioteca"
2. Selecciona una carpeta
3. Haz clic en una canción
4. **Verificar**:
   - ✅ La canción se reproduce correctamente
   - ✅ Se muestra la carátula correcta
   - ✅ El título y artista se muestran correctamente

#### C. Carátulas Random
1. Busca canciones que NO tengan carátula descargada
2. **Verificar**:
   - ✅ Se muestra una de las 9 carátulas random del proyecto
   - ✅ La misma canción siempre muestra la misma carátula (determinístico)

#### D. Controles del Reproductor
1. **Verificar**:
   - ✅ Play/Pause funciona
   - ✅ Siguiente canción funciona
   - ✅ Canción anterior funciona
   - ✅ Barra de progreso permite hacer seek
   - ✅ Control de volumen funciona
   - ✅ Modo aleatorio funciona
   - ✅ Ecualizador funciona

### 4. Verificar en la Consola del Navegador

Abre las DevTools (F12) y verifica:
- ✅ No hay errores de CORS
- ✅ No hay errores 404 al cargar archivos de audio
- ✅ No hay errores al cargar carátulas
- ✅ Las rutas de streaming son correctas (formato: `http://localhost:5001/api/stream/folder/filename.mp3`)

### 5. Problemas Comunes

#### La canción no suena
- Verifica que el servidor Python esté corriendo
- Verifica que haya archivos en la carpeta `downloads`
- Revisa la consola del navegador para errores de red
- Verifica que el volumen no esté en 0

#### Las carátulas no se muestran
- Verifica que las imágenes estén en `ui/src/assets/styles/no_cover/` (1.png a 9.png)
- Verifica que el build de Vite haya incluido las imágenes en `ui/dist/assets/`
- Revisa la consola para errores de carga de imágenes

#### Error de CORS
- Verifica que el servidor Python tenga `CORS(app)` habilitado
- Verifica que el elemento `<audio>` tenga `crossorigin="anonymous"`

### 6. Descargar Canciones de Prueba

Si no tienes canciones en la biblioteca:

1. Ve a la vista "Downloader"
2. Pega una URL de YouTube (video o playlist)
3. Haz clic en "Analizar Playlist"
4. Selecciona una carpeta de destino
5. Haz clic en "Descargar Todo"
6. Espera a que se descarguen las canciones
7. Ve a la vista "Biblioteca" para verlas

### 7. Logs Útiles

Revisa los logs en:
- **Terminal del servidor Python**: Errores de descarga, streaming, etc.
- **Terminal de Electron**: Errores de la aplicación Electron
- **DevTools del navegador**: Errores de JavaScript, red, etc.

## Cambios Implementados

Ver `FIXES_REPRODUCCION.md` para detalles completos de los cambios realizados.
