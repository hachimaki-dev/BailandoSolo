# Sistema de Perfiles - SonicStream

## Descripción General

El sistema de perfiles permite a los usuarios organizar su música en diferentes contextos o categorías. Cada perfil tiene su propia biblioteca de música completamente independiente.

## Características

### ✨ Funcionalidades Principales

1. **Perfiles Independientes**: Cada perfil tiene su propia carpeta de música y estadísticas
2. **Perfil Default**: Se crea automáticamente al iniciar la aplicación
3. **Persistencia**: Los perfiles se guardan en `profiles.json` y persisten entre sesiones
4. **Migración Automática**: La música existente se mueve automáticamente al perfil Default

### 🎯 Operaciones Disponibles

- **Crear Perfil**: Añade un nuevo perfil con nombre personalizado
- **Cambiar Perfil**: Cambia entre perfiles existentes (recarga la aplicación)
- **Renombrar Perfil**: Modifica el nombre de un perfil (excepto Default)
- **Eliminar Perfil**: Borra un perfil y su contenido (excepto Default y el activo)

## Estructura de Carpetas

```
downloads/
├── Default/           # Perfil por defecto
│   ├── Carpeta1/
│   │   ├── cancion1.mp3
│   │   └── cancion1.jpg
│   └── Carpeta2/
├── Fiesta/           # Perfil personalizado
│   └── ...
└── Trabajo/          # Otro perfil
    └── ...
```

## Uso de la Interfaz

### Acceder al Gestor de Perfiles

1. Busca el **FAB (botón flotante)** en la esquina superior derecha
2. El botón tiene un ícono de usuario (👤)
3. Haz clic para abrir el menú de perfiles

### Crear un Nuevo Perfil

1. Abre el menú de perfiles
2. Haz clic en **"+ Nuevo Perfil"**
3. Ingresa el nombre del perfil
4. Presiona **Enter** o el botón **✓** para confirmar
5. Presiona **Esc** o el botón **✕** para cancelar

### Cambiar de Perfil

1. Abre el menú de perfiles
2. Haz clic en el nombre del perfil que deseas activar
3. La aplicación se recargará automáticamente con el nuevo perfil

### Renombrar un Perfil

1. Abre el menú de perfiles
2. Haz clic en el ícono de lápiz **✎** junto al perfil
3. Ingresa el nuevo nombre
4. Presiona **Enter** o **✓** para confirmar

**Nota**: No se puede renombrar el perfil "Default"

### Eliminar un Perfil

1. Abre el menú de perfiles
2. Haz clic en el ícono de papelera **🗑** junto al perfil
3. Confirma la eliminación en el diálogo

**Restricciones**:
- No se puede eliminar el perfil "Default"
- No se puede eliminar el perfil actualmente activo

## API Backend

### Endpoints Disponibles

#### GET `/api/profiles`
Obtiene todos los perfiles y el perfil activo.

**Respuesta**:
```json
{
  "active": "Default",
  "profiles": ["Default", "Fiesta", "Trabajo"]
}
```

#### POST `/api/profiles`
Crea un nuevo perfil.

**Body**:
```json
{
  "name": "Mi Perfil"
}
```

#### DELETE `/api/profiles/<profile_name>`
Elimina un perfil.

#### POST `/api/profiles/<profile_name>/rename`
Renombra un perfil.

**Body**:
```json
{
  "new_name": "Nuevo Nombre"
}
```

#### POST `/api/profiles/active`
Establece el perfil activo.

**Body**:
```json
{
  "profile": "Fiesta"
}
```

## Comportamiento del Sistema

### Al Iniciar el Servidor

1. Se carga o crea `profiles.json`
2. Se crea el perfil "Default" si no existe
3. Se migra la música existente en `downloads/` al perfil Default
4. Se crean las carpetas necesarias

### Al Cambiar de Perfil

1. Se actualiza el perfil activo en `profiles.json`
2. La aplicación se recarga automáticamente
3. Todas las operaciones (descargas, reproducción, estadísticas) usan el nuevo perfil

### Persistencia de Datos

- **Perfiles**: `profiles.json` en la raíz del proyecto
- **Música**: `downloads/<perfil>/` para cada perfil
- **Estadísticas**: `stats.json` (compartido entre todos los perfiles)

## Casos de Uso

### Ejemplo 1: Música Personal vs Fiesta
```
Default/          # Música personal
  ├── Relax/
  └── Favoritos/

Fiesta/          # Música para fiestas
  ├── Reggaeton/
  └── Electrónica/
```

### Ejemplo 2: Por Idioma
```
Default/         # Música en español
Inglés/          # Música en inglés
Francés/         # Música en francés
```

### Ejemplo 3: Por Contexto
```
Default/         # General
Trabajo/         # Música para trabajar
Gimnasio/        # Música para entrenar
Estudio/         # Música para estudiar
```

## Notas Técnicas

### Frontend
- Componente: `ProfileManager.vue`
- Servicio: `ProfileService.js`
- Ubicación: FAB en esquina superior derecha
- Animaciones: Transiciones suaves con CSS

### Backend
- Archivo de configuración: `profiles.json`
- Función de inicialización: `ensure_default_profile()`
- Todas las rutas de API usan el perfil activo automáticamente

### Seguridad
- Validación de nombres de perfil
- Protección contra eliminación de perfiles críticos
- Sanitización de rutas para evitar path traversal

## Solución de Problemas

### El perfil no cambia
- Verifica que el servidor esté corriendo
- Revisa la consola del navegador para errores
- Asegúrate de que `profiles.json` tenga permisos de escritura

### La música no aparece después de cambiar perfil
- Verifica que la carpeta del perfil exista en `downloads/`
- Recarga la página manualmente si no se recargó automáticamente
- Revisa que las canciones estén en subcarpetas dentro del perfil

### Error al crear perfil
- Verifica que el nombre no contenga caracteres especiales
- Asegúrate de que no exista un perfil con ese nombre
- Revisa los permisos de la carpeta `downloads/`

## Mejoras Futuras

- [ ] Exportar/Importar perfiles
- [ ] Compartir perfiles entre dispositivos
- [ ] Estadísticas por perfil
- [ ] Temas personalizados por perfil
- [ ] Sincronización en la nube
