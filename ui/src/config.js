/**
 * Bailando Solo — Global Client Configuration
 * Handles API and streaming URL resolution for both Dev (Vite proxy) and Production (Electron file://).
 */

// Detect if we are running inside Electron with file:// protocol (production build)
const isElectronProd = typeof window !== 'undefined' &&
  (window.location.protocol === 'file:' || !window.location.hostname || window.location.hostname === '')

// Dynamic API host — starts with a reasonable default, gets updated on init
let API_HOST = isElectronProd ? 'http://127.0.0.1:5001' : ''
let API_BASE = `${API_HOST}/api`

/**
 * Initialize the API configuration by fetching the dynamic port from Electron.
 * Must be called once at app startup before any API requests.
 */
export async function initConfig() {
  if (isElectronProd && window.electronAPI) {
    try {
      const port = await window.electronAPI.getServerPort()
      API_HOST = `http://127.0.0.1:${port}`
      API_BASE = `${API_HOST}/api`
      console.log(`[config] API configured at: ${API_HOST}`)
    } catch (e) {
      console.warn('[config] Could not get server port, using default 5001:', e)
    }
  }
}

export { API_HOST, API_BASE }

export function apiUrl(endpoint) {
  if (!endpoint) return API_BASE
  if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) return endpoint
  const clean = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
  if (clean.startsWith('/api')) {
    return `${API_HOST}${clean}`
  }
  return `${API_BASE}${clean}`
}

export function streamUrl(pathOrUrl) {
  if (!pathOrUrl) return ''
  if (pathOrUrl.startsWith('http://') || pathOrUrl.startsWith('https://') || pathOrUrl.startsWith('data:')) {
    return pathOrUrl
  }
  const clean = pathOrUrl.startsWith('/') ? pathOrUrl : `/${pathOrUrl}`
  return `${API_HOST}${clean}`
}
