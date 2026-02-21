# Guía de Creación de Temas para Bailando Solo

Esta guía define el estándar estricto para la creación de nuevos temas. El objetivo es garantizar que cualquier nuevo tema generado por IA o humanos se integre perfectamente sin romper la estructura ni la funcionalidad.

## Regla de Oro
**LOS TEMAS SOLO PUEDEN MODIFICAR VARIABLES CSS.**
Nunca deben escribir selectores CSS directos (como `.button { ... }`) ni modificar propiedades de layout (display, position, margin, padding) directamente. Todo el control visual se realiza sobrescribiendo las variables definidas en `:root` dentro del selector del tema.

## Estructura del Archivo de Tema
Todo archivo de tema debe seguir este formato:

```css
/* theme-nombre.css */

body[data-theme="nombre"] {
    /* --- COLORES --- */
    --bg-main: #ffffff;       /* Fondo principal */
    --bg-alt: #f3f4f6;        /* Fondo secundario (items, paneles) */
    --bg-panel: #ffffff;      /* Fondo de paneles flotantes */
    --bg-input: #ffffff;      /* Fondo de inputs */
    
    --text-main: #1f2937;     /* Texto principal */
    --text-muted: #6b7280;    /* Texto secundario/etiquetas */
    --text-inverse: #ffffff;  /* Texto sobre colores oscuros/primarios */

    --primary: #3b82f6;       /* Color principal de acción */
    --primary-hover: #2563eb; /* Estado hover del primario */
    --accent: #10b981;        /* Acentos (ej. barras de progreso) */
    
    --border-color: #e5e7eb;  /* Color de bordes */
    --shadow-color: rgba(0, 0, 0, 0.1); /* Color base de sombras */

    /* --- FORMAS Y BORDES --- */
    --radius-md: 12px;        /* Radio general de botones y tarjetas */
    --radius-lg: 24px;        /* Radio de paneles grandes */
    --border-width: 1px;      /* Grosor de bordes */
    --border-style: solid;    /* Estilo de borde */

    /* --- TIPOGRAFÍA --- */
    --font-main: 'Nombre Fuente', sans-serif; /* Fuente principal */

    /* --- EXTRAS --- */
    /* Puedes usar background-image aquí para patrones o degradados */
    background: var(--bg-main);
}

/* Opcional: Overrides específicos para efectos avanzados (solo si es estrictamente necesario) */
/* Ejemplo: Parallax o fondos complejos */
body[data-theme="nombre"]::before {
    /* ... */
}
```

## Variables Disponibles
Consulta `styles/base.css` para la lista completa. Las más críticas son:

### Colores
- `var(--bg-main)`: Fondo de la página.
- `var(--bg-alt)`: Fondo de elementos de lista y áreas secundarias.
- `var(--primary)`: Botones principales, sliders activos, iconos activos.
- `var(--text-main)`: Títulos y contenido principal.

### Dimensiones (No modificar layout, solo escala)
- `var(--control-size)`: Tamaño de botones de control.
- `var(--album-art-size)`: Tamaño del arte de álbum.

## Proceso de Generación (Prompt para IA)

> "Crea un nuevo archivo CSS para un tema llamado '[NOMBRE]' para Bailando Solo.
> El tema debe evocar [ESTILO/SENSACIÓN].
> REGLAS ESTRICTAS:
> 1. Usa el selector `body[data-theme='[NOMBRE]']`.
> 2. SOLO define variables CSS (Custom Properties) para sobrescribir los valores de `base.css`.
> 3. NO escribas selectores de clase (ej. no uses `.song-item {}`).
> 4. Define colores coherentes para `--bg-main`, `--text-main`, `--primary`, etc.
> 5. Si necesitas una fuente especial, asume que está disponible o usa una de sistema."

## Ejemplo de Validación
Antes de guardar un tema, verifica:
1. ¿El archivo contiene selectores de clase como `.panel` o `.btn`? -> **INCORRECTO**. Borralos.
2. ¿El archivo solo contiene `body[data-theme="..."] { --var: val; ... }`? -> **CORRECTO**.
