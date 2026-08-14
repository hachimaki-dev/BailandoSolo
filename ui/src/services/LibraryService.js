/**
 * Bailando Solo — Library Service
 * API client for browsing, searching, and managing the local audio library.
 */

const API_BASE = '/api'

export const LibraryService = {
  async getFolders() {
    try {
      const res = await fetch(`${API_BASE}/library`)
      if (!res.ok) throw new Error('Error al cargar carpetas')
      return await res.json()
    } catch (e) {
      console.error('LibraryService.getFolders error:', e)
      return []
    }
  },

  async getFolderSongs(folder) {
    try {
      const res = await fetch(`${API_BASE}/library/${encodeURIComponent(folder)}`)
      if (!res.ok) throw new Error(`Error al cargar canciones de ${folder}`)
      return await res.json()
    } catch (e) {
      console.error('LibraryService.getFolderSongs error:', e)
      return []
    }
  },

  async getAllSongs() {
    try {
      const res = await fetch(`${API_BASE}/library/all`)
      if (!res.ok) throw new Error('Error al cargar el catálogo completo')
      return await res.json()
    } catch (e) {
      console.error('LibraryService.getAllSongs error:', e)
      return []
    }
  },

  async getRandomSongs() {
    try {
      const res = await fetch(`${API_BASE}/library/random`)
      if (!res.ok) throw new Error('Error al cargar canciones aleatorias')
      return await res.json()
    } catch (e) {
      console.error('LibraryService.getRandomSongs error:', e)
      return []
    }
  },

  async checkDuplicates(items) {
    try {
      const res = await fetch(`${API_BASE}/library/check-duplicates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items })
      })
      if (!res.ok) throw new Error('Error al verificar duplicados')
      return await res.json()
    } catch (e) {
      console.error('LibraryService.checkDuplicates error:', e)
      return { duplicates: [] }
    }
  },

  async editMetadata({ folder, old_filename, title, artist, new_folder }) {
    try {
      const res = await fetch(`${API_BASE}/library/edit-metadata`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          folder,
          old_filename,
          title,
          artist,
          new_folder
        })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Error al guardar metadatos')
      return data
    } catch (e) {
      console.error('LibraryService.editMetadata error:', e)
      throw e
    }
  },

  async deleteSong(folder, filename) {
    try {
      const res = await fetch(`${API_BASE}/library/delete-song`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder, filename })
      })
      if (!res.ok) throw new Error('Error al eliminar canción')
      return await res.json()
    } catch (e) {
      console.error('LibraryService.deleteSong error:', e)
      throw e
    }
  },

  getThumbnailUrl(path) {
    if (!path) return null
    if (path.startsWith('http')) return path
    if (path.startsWith('/')) return path
    return `/${path}`
  }
}
