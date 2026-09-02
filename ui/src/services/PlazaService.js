/**
 * Bailando Solo — PlazaService
 * 
 * Decentralized P2P community hub powered by the Nostr protocol.
 * Requires ZERO backend servers, zero hosting costs, and zero maintenance.
 * Relies on open, distributed public Nostr relays.
 */

import { SimplePool, generateSecretKey, getPublicKey, finalizeEvent } from 'nostr-tools'

// Default public high-availability relays
const DEFAULT_RELAYS = [
  'wss://relay.damus.io',
  'wss://nos.lol',
  'wss://relay.primal.net',
  'wss://public.relays.sh'
]

const STORAGE_KEYS = {
  SK: 'bailandosolo_plaza_sk',
  ALIAS: 'bailandosolo_plaza_alias',
  AUTO_SHARE: 'bailandosolo_plaza_auto_share',
  CACHE: 'bailandosolo_plaza_cache_v1',
  DOWNLOADS: 'bailandosolo_plaza_downloads_v1'
}

class PlazaServiceClass {
  constructor() {
    this.pool = null
    this.relays = [...DEFAULT_RELAYS]
    this.sk = null
    this.pk = null
    this.alias = 'BailandoDJ'
    this.avatarColor = '#00f0ff'
    
    this.playlistsMap = new Map()
    this.downloadsMap = new Map()
    this.activeUsersMap = new Map()
    
    this.playlistListeners = new Set()
    this.presenceListeners = new Set()
    this.relayStatusListeners = new Set()
    
    this.connectedRelays = new Set()
    this.presenceHeartbeatInterval = null
    this.cleanStaleUsersInterval = null
    this.currentPlayingInfo = null
    
    this.isInitialized = false
  }

  /**
   * Helper: Hex converters for Nostr keys
   */
  bytesToHex(bytes) {
    return Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('')
  }

  hexToBytes(hex) {
    const bytes = new Uint8Array(hex.length / 2)
    for (let i = 0; i < bytes.length; i++) {
      bytes[i] = parseInt(hex.substr(i * 2, 2), 16)
    }
    return bytes
  }

  /**
   * Deterministic avatar color from a public key string
   */
  generateColor(str) {
    const colors = ['#00f0ff', '#ff007f', '#ffe600', '#00ff66', '#a855f7', '#ff5722', '#38bdf8']
    let hash = 0
    for (let i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash)
    }
    return colors[Math.abs(hash) % colors.length]
  }

  /**
   * Initialize local keys and connect to Nostr relays
   */
  _getStorage(key) {
    try {
      if (typeof localStorage !== 'undefined') {
        return localStorage.getItem(key)
      }
    } catch (e) {}
    if (!this._memStorage) this._memStorage = new Map()
    return this._memStorage.get(key) || null
  }

  _setStorage(key, val) {
    try {
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(key, val)
        return
      }
    } catch (e) {}
    if (!this._memStorage) this._memStorage = new Map()
    this._memStorage.set(key, val)
  }

  /**
   * Initialize local keys and connect to Nostr relays
   */
  async init() {
    if (this.isInitialized) return
    this.isInitialized = true

    // 1. Load or generate Nostr Secret Key
    try {
      const savedSkHex = this._getStorage(STORAGE_KEYS.SK)
      if (savedSkHex && savedSkHex.length === 64) {
        this.sk = this.hexToBytes(savedSkHex)
      } else {
        this.sk = generateSecretKey()
        this._setStorage(STORAGE_KEYS.SK, this.bytesToHex(this.sk))
      }
      this.pk = getPublicKey(this.sk)
      this.avatarColor = this.generateColor(this.pk)
    } catch (e) {
      console.warn('[Plaza] Error initializing cryptographic keys:', e)
      this.sk = generateSecretKey()
      this.pk = getPublicKey(this.sk)
    }

    // 2. Load alias
    const savedAlias = this._getStorage(STORAGE_KEYS.ALIAS)
    if (savedAlias) {
      this.alias = savedAlias
    } else {
      this.alias = `BailandoDJ_${this.pk.slice(0, 4).toUpperCase()}`
      this._setStorage(STORAGE_KEYS.ALIAS, this.alias)
    }

    // 3. Load cached user playlists
    this._loadCache()

    // 4. Initialize active community peers with local user
    this.activeUsersMap.set(this.pk, {
      pubkey: this.pk,
      alias: this.alias,
      avatarColor: this.avatarColor,
      isPlaying: false,
      currentSong: null,
      lastSeen: Date.now(),
      isMe: true
    })

    // 5. Initialize Nostr Pool
    try {
      this.pool = new SimplePool()
      this._startNostrSubscriptions()
    } catch (e) {
      console.warn('[Plaza] Error starting Nostr pool:', e)
    }

    // 6. Start background pruning for active users (remove offline after 2.5 min)
    this.cleanStaleUsersInterval = setInterval(() => {
      this._pruneStaleUsers()
    }, 15000)

    // 7. Broadcast local presence periodically
    this.presenceHeartbeatInterval = setInterval(() => {
      if (this.currentPlayingInfo) {
        this.publishNowPlaying(this.currentPlayingInfo)
      }
    }, 45000)
  }

  /**
   * Load cached playlists and download counters from localStorage
   */
  _loadCache() {
    try {
      const cached = this._getStorage(STORAGE_KEYS.CACHE)
      if (cached) {
        const parsed = JSON.parse(cached)
        for (const pl of parsed) {
          // Reject any legacy hardcoded seed playlists
          if (pl && pl.id && !pl.id.startsWith('seed-')) {
            this.playlistsMap.set(pl.id, pl)
          }
        }
      }

      const cachedDownloads = this._getStorage(STORAGE_KEYS.DOWNLOADS)
      if (cachedDownloads) {
        const parsedDl = JSON.parse(cachedDownloads)
        for (const [k, v] of Object.entries(parsedDl)) {
          if (!k.startsWith('seed-')) {
            this.downloadsMap.set(k, v)
          }
        }
      }
    } catch (e) {
      console.warn('[Plaza] Error loading cache:', e)
    }
  }

  _saveCache() {
    try {
      const list = Array.from(this.playlistsMap.values())
      this._setStorage(STORAGE_KEYS.CACHE, JSON.stringify(list))

      const dlObj = Object.fromEntries(this.downloadsMap)
      this._setStorage(STORAGE_KEYS.DOWNLOADS, JSON.stringify(dlObj))
    } catch (e) {
      console.warn('[Plaza] Error saving cache:', e)
    }
  }

  /**
   * Connect to relays and subscribe to:
   * - Playlist events (kind 30078)
   * - Download counters (kind 7)
   * - Realtime User Status / Now Playing (kind 30315)
   */
  _startNostrSubscriptions() {
    if (!this.pool) return

    // Track relay connection success
    this.relays.forEach(url => {
      try {
        const ws = new WebSocket(url)
        ws.onopen = () => {
          this.connectedRelays.add(url)
          this._notifyRelayStatus()
          ws.close()
        }
      } catch (err) {
        // Soft fail
      }
    })

    // 1. Subscribe to Playlists
    try {
      this.pool.subscribeMany(
        this.relays,
        [{
          kinds: [30078],
          '#t': ['bailandosolo'],
          limit: 60
        }],
        {
          onevent: (event) => {
            this._handlePlaylistEvent(event)
          },
          oneose: () => {
            this._notifyPlaylists()
          }
        }
      )
    } catch (err) {
      console.warn('[Plaza] Playlist subscription error:', err)
    }

    // 2. Subscribe to Download reactions
    try {
      this.pool.subscribeMany(
        this.relays,
        [{
          kinds: [7],
          '#t': ['bailandosolo'],
          '#action': ['download'],
          limit: 500
        }],
        {
          onevent: (event) => {
            this._handleDownloadReaction(event)
          }
        }
      )
    } catch (err) {
      console.warn('[Plaza] Reaction subscription error:', err)
    }

    // 3. Subscribe to Real-time Presence & Now Playing
    try {
      const now = Math.floor(Date.now() / 1000)
      this.pool.subscribeMany(
        this.relays,
        [{
          kinds: [30315],
          '#t': ['bailandosolo'],
          since: now - 180
        }],
        {
          onevent: (event) => {
            this._handlePresenceEvent(event)
          }
        }
      )
    } catch (err) {
      console.warn('[Plaza] Presence subscription error:', err)
    }
  }

  /**
   * Process incoming Nostr Playlist Event (kind 30078)
   */
  _handlePlaylistEvent(event) {
    try {
      const dTag = event.tags.find(t => t[0] === 'd')?.[1]
      const playlistId = dTag ? dTag.replace('bailandosolo:playlist:', '') : event.id
      const data = JSON.parse(event.content)

      if (!data.title || !data.url) return

      const existing = this.playlistsMap.get(playlistId) || {}
      const item = {
        id: playlistId,
        eventId: event.id,
        pubkey: event.pubkey,
        title: data.title,
        url: data.url,
        author: data.author || 'BailandoSolo_User',
        avatarColor: this.generateColor(event.pubkey),
        createdAt: event.created_at * 1000,
        downloads: Math.max(existing.downloads || 0, this.downloadsMap.get(playlistId) || 0, data.downloads || 0),
        songs: Array.isArray(data.songs) ? data.songs : []
      }

      this.playlistsMap.set(playlistId, item)
      this._saveCache()
      this._notifyPlaylists()
    } catch (e) {
      // Ignored malformed content
    }
  }

  /**
   * Process incoming download reaction
   */
  _handleDownloadReaction(event) {
    try {
      const targetPlId = event.tags.find(t => t[0] === 'playlist_id')?.[1]
      const targetUrl = event.tags.find(t => t[0] === 'url')?.[1]
      const targetKey = targetPlId || targetUrl

      if (targetKey) {
        const current = this.downloadsMap.get(targetKey) || 0
        this.downloadsMap.set(targetKey, current + 1)

        // Update playlist record if present
        for (const [id, pl] of this.playlistsMap.entries()) {
          if (id === targetKey || pl.url === targetKey) {
            pl.downloads = (pl.downloads || 0) + 1
            break
          }
        }
        this._notifyPlaylists()
      }
    } catch (e) {}
  }

  /**
   * Process incoming presence heartbeat
   */
  _handlePresenceEvent(event) {
    try {
      const parsed = JSON.parse(event.content)
      const userKey = event.pubkey
      
      this.activeUsersMap.set(userKey, {
        pubkey: userKey,
        alias: parsed.alias || event.tags.find(t => t[0] === 'author')?.[1] || 'Anónimo',
        avatarColor: this.generateColor(userKey),
        isPlaying: !!parsed.isPlaying,
        currentSong: parsed.title ? { title: parsed.title, artist: parsed.artist || '' } : null,
        lastSeen: Date.now()
      })

      this._notifyPresence()
    } catch (e) {}
  }

  /**
   * Remove users inactive for > 2.5 minutes
   */
  _pruneStaleUsers() {
    const cutoff = Date.now() - 150000
    let changed = false
    for (const [key, user] of this.activeUsersMap.entries()) {
      if (user.lastSeen < cutoff && user.pubkey !== this.pk) {
        this.activeUsersMap.delete(key)
        changed = true
      }
    }
    if (changed) {
      this._notifyPresence()
    }
  }

  /**
   * Publish a playlist with full song metadata to the decentralized network
   */
  async publishPlaylist({ title, url, songs, author }) {
    await this.init()

    const cleanId = this._generatePlaylistId(url)
    const authorName = author || this.alias

    const songsData = (songs || []).map(s => ({
      id: s.id || '',
      title: s.title || 'Sin título',
      uploader: s.uploader || '',
      duration: s.duration || 0,
      thumbnail: s.thumbnail || null
    }))

    const payload = {
      title,
      url,
      author: authorName,
      count: songsData.length,
      songs: songsData,
      downloads: 0
    }

    const now = Math.floor(Date.now() / 1000)
    const eventTemplate = {
      kind: 30078,
      created_at: now,
      tags: [
        ['d', `bailandosolo:playlist:${cleanId}`],
        ['t', 'bailandosolo'],
        ['type', 'playlist'],
        ['title', title],
        ['url', url],
        ['count', String(songsData.length)],
        ['author', authorName],
        ['client', 'BailandoSolo']
      ],
      content: JSON.stringify(payload)
    }

    const signedEvent = finalizeEvent(eventTemplate, this.sk)

    // Save locally first
    const item = {
      id: cleanId,
      eventId: signedEvent.id,
      pubkey: this.pk,
      title,
      url,
      author: authorName,
      avatarColor: this.avatarColor,
      createdAt: Date.now(),
      downloads: 0,
      songs: songsData
    }
    this.playlistsMap.set(cleanId, item)
    this._saveCache()
    this._notifyPlaylists()

    // Broadcast to relays
    if (this.pool) {
      try {
        await Promise.any(this.pool.publish(this.relays, signedEvent))
      } catch (e) {
        console.warn('[Plaza] Relay publish notice:', e)
      }
    }

    return item
  }

  /**
   * Broadcast real-time "Now Playing" and presence
   */
  async publishNowPlaying({ title, artist, isPlaying }) {
    await this.init()

    this.currentPlayingInfo = { title, artist, isPlaying }

    // Update local presence immediately
    this.activeUsersMap.set(this.pk, {
      pubkey: this.pk,
      alias: this.alias,
      avatarColor: this.avatarColor,
      isPlaying: !!isPlaying,
      currentSong: title ? { title, artist } : null,
      lastSeen: Date.now()
    })
    this._notifyPresence()

    const now = Math.floor(Date.now() / 1000)
    const eventTemplate = {
      kind: 30315,
      created_at: now,
      tags: [
        ['d', 'music'],
        ['t', 'bailandosolo'],
        ['author', this.alias],
        ['expiration', String(now + 180)]
      ],
      content: JSON.stringify({
        title: title || '',
        artist: artist || '',
        isPlaying: !!isPlaying,
        alias: this.alias,
        timestamp: Date.now()
      })
    }

    try {
      const signedEvent = finalizeEvent(eventTemplate, this.sk)
      if (this.pool) {
        this.pool.publish(this.relays, signedEvent)
      }
    } catch (e) {
      // Ignored
    }
  }

  /**
   * Record a download interaction to increase popularity
   */
  async recordDownload(playlistId, playlistUrl) {
    await this.init()

    // Local increment
    const current = this.downloadsMap.get(playlistId) || 0
    this.downloadsMap.set(playlistId, current + 1)

    const pl = this.playlistsMap.get(playlistId)
    if (pl) {
      pl.downloads = (pl.downloads || 0) + 1
      this._notifyPlaylists()
      this._saveCache()
    }

    // Emit Nostr reaction
    const now = Math.floor(Date.now() / 1000)
    const eventTemplate = {
      kind: 7,
      created_at: now,
      tags: [
        ['t', 'bailandosolo'],
        ['action', 'download'],
        ['playlist_id', playlistId],
        ['url', playlistUrl || '']
      ],
      content: '📥'
    }

    try {
      const signedEvent = finalizeEvent(eventTemplate, this.sk)
      if (this.pool) {
        this.pool.publish(this.relays, signedEvent)
      }
    } catch (e) {}
  }

  /**
   * Deterministic ID for URLs
   */
  _generatePlaylistId(url) {
    try {
      const parsed = new URL(url)
      const listId = parsed.searchParams.get('list')
      if (listId) return `yt-${listId}`
    } catch (e) {}
    // Fallback simple hash
    let hash = 0
    for (let i = 0; i < url.length; i++) {
      hash = (hash << 5) - hash + url.charCodeAt(i)
      hash |= 0
    }
    return `pl-${Math.abs(hash).toString(16)}`
  }

  // ─── Settings & Identity ─────────────────────────────────────────────────────

  getIdentity() {
    return {
      pubkey: this.pk,
      alias: this.alias,
      avatarColor: this.avatarColor,
      isAutoShareEnabled: this._getStorage(STORAGE_KEYS.AUTO_SHARE) === 'true'
    }
  }

  setAlias(newAlias) {
    if (!newAlias || !newAlias.trim()) return
    this.alias = newAlias.trim()
    this._setStorage(STORAGE_KEYS.ALIAS, this.alias)
    if (this.currentPlayingInfo) {
      this.publishNowPlaying(this.currentPlayingInfo)
    }
  }

  setAutoShare(val) {
    this._setStorage(STORAGE_KEYS.AUTO_SHARE, val ? 'true' : 'false')
  }

  isAutoShareEnabled() {
    return this._getStorage(STORAGE_KEYS.AUTO_SHARE) === 'true'
  }

  // ─── Subscription Listeners ──────────────────────────────────────────────────

  onPlaylists(fn) {
    this.playlistListeners.add(fn)
    // Fire immediately with current data
    fn(Array.from(this.playlistsMap.values()))
    return () => this.playlistListeners.delete(fn)
  }

  onPresence(fn) {
    this.presenceListeners.add(fn)
    fn(Array.from(this.activeUsersMap.values()))
    return () => this.presenceListeners.delete(fn)
  }

  onRelayStatus(fn) {
    this.relayStatusListeners.add(fn)
    fn({ connected: this.connectedRelays.size, total: this.relays.length })
    return () => this.relayStatusListeners.delete(fn)
  }

  _notifyPlaylists() {
    const list = Array.from(this.playlistsMap.values())
    for (const fn of this.playlistListeners) {
      try { fn(list) } catch (e) {}
    }
  }

  _notifyPresence() {
    const users = Array.from(this.activeUsersMap.values())
    for (const fn of this.presenceListeners) {
      try { fn(users) } catch (e) {}
    }
  }

  _notifyRelayStatus() {
    const status = { connected: this.connectedRelays.size, total: this.relays.length }
    for (const fn of this.relayStatusListeners) {
      try { fn(status) } catch (e) {}
    }
  }

  destroy() {
    if (this.presenceHeartbeatInterval) clearInterval(this.presenceHeartbeatInterval)
    if (this.cleanStaleUsersInterval) clearInterval(this.cleanStaleUsersInterval)
    if (this.pool) {
      try { this.pool.destroy() } catch (e) {}
    }
  }
}

export const PlazaService = new PlazaServiceClass()
