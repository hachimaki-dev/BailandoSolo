/**
 * Bailando Solo — Playlist & Smart Crates Service
 * Handles user playlists, dynamic rule evaluation for Smart Crates, and playlist sync.
 */

import { API_BASE } from '../config'

export const PlaylistService = {
  async getPlaylists() {
    try {
      const res = await fetch(`${API_BASE}/playlists`)
      if (!res.ok) throw new Error('Error al cargar playlists')
      return await res.json()
    } catch (e) {
      console.error('PlaylistService.getPlaylists error:', e)
      return []
    }
  },

  async createPlaylist(payload) {
    try {
      const res = await fetch(`${API_BASE}/playlists`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Error al crear playlist')
      return data
    } catch (e) {
      console.error('PlaylistService.createPlaylist error:', e)
      throw e
    }
  },

  async updatePlaylist(id, payload) {
    try {
      const res = await fetch(`${API_BASE}/playlists/${encodeURIComponent(id)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Error al actualizar playlist')
      return data
    } catch (e) {
      console.error('PlaylistService.updatePlaylist error:', e)
      throw e
    }
  },

  async deletePlaylist(id) {
    try {
      const res = await fetch(`${API_BASE}/playlists/${encodeURIComponent(id)}`, {
        method: 'DELETE'
      })
      if (!res.ok) throw new Error('Error al eliminar playlist')
      return await res.json()
    } catch (e) {
      console.error('PlaylistService.deletePlaylist error:', e)
      throw e
    }
  },

  async addSongToPlaylist(id, song) {
    try {
      const res = await fetch(`${API_BASE}/playlists/${encodeURIComponent(id)}/add-song`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ song })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Error al agregar canción a playlist')
      return data
    } catch (e) {
      console.error('PlaylistService.addSongToPlaylist error:', e)
      throw e
    }
  },

  async removeSongFromPlaylist(id, songPath, index) {
    try {
      const res = await fetch(`${API_BASE}/playlists/${encodeURIComponent(id)}/remove-song`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: songPath, index })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Error al remover canción de playlist')
      return data
    } catch (e) {
      console.error('PlaylistService.removeSongFromPlaylist error:', e)
      throw e
    }
  },

  /**
   * Evaluates a Smart Crate rule dynamically against the current library and stats.
   * @param {Object} rule - { field, operator, value }
   * @param {Array} allSongs - list of all library songs
   * @param {Object} statsData - raw stats map from StatsService
   * @returns {Array} matching songs
   */
  evaluateSmartCrate(rule, allSongs = [], statsData = {}) {
    if (!rule || !rule.field) return allSongs

    const field = rule.field
    const op = rule.operator
    const val = rule.value

    let filtered = [...allSongs]

    if (field === 'plays') {
      if (op === 'top') {
        const limit = Number(val) || 25
        filtered.sort((a, b) => {
          const playsA = (statsData[a.filename]?.play_count) || 0
          const playsB = (statsData[b.filename]?.play_count) || 0
          return playsB - playsA
        })
        return filtered.slice(0, limit)
      } else if (op === 'eq' && val === 0) {
        // Vault / Never played
        return filtered.filter(s => !(statsData[s.filename]?.play_count > 0))
      } else if (op === 'gt') {
        return filtered.filter(s => ((statsData[s.filename]?.play_count) || 0) > Number(val))
      }
    } else if (field === 'mtime') {
      if (op === 'days_ago') {
        const threshold = (Date.now() / 1000) - (Number(val) * 86400)
        return filtered.filter(s => (s.mtime || 0) >= threshold)
      }
    } else if (field === 'artist') {
      const query = String(val).toLowerCase()
      return filtered.filter(s => (s.uploader || '').toLowerCase().includes(query))
    } else if (field === 'folder') {
      return filtered.filter(s => (s.folder || '').toLowerCase() === String(val).toLowerCase())
    }

    return filtered
  }
}
