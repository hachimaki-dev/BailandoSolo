/**
 * Bailando Solo — Global Client Configuration
 * Handles API and streaming URL resolution for both Dev (Vite proxy) and Production (Electron file://).
 */

const isElectronFileProtocol = typeof window !== 'undefined' && 
  (window.location.protocol === 'file:' || !window.location.hostname || window.location.hostname === '')

export const API_HOST = isElectronFileProtocol ? 'http://127.0.0.1:5001' : ''
export const API_BASE = `${API_HOST}/api`

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
