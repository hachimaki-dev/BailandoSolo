<template>
  <div class="app-layout">
    <div class="container">
      <!-- Retro Console Master Header -->
      <AppHeader 
        :currentView="currentView" 
        @navigate="navigateView" 
        @open-search="showSearchModal = true"
        @open-stats="showStats = true"
        @open-profiles="showProfileModal = true"
        @open-qr="showQRModal = true"
      />

      <!-- Main Screen Grid (Console Deck + Permanent Player) -->
      <div class="main-grid">
        <!-- Main Workstation View Area -->
        <div class="main-content-zone">
          <!-- Downloader View (Primary Experience) -->
          <DownloaderView 
            v-if="currentView === 'downloader'" 
            :allSongs="allSongs"
            :initialUrl="plazaInitialData.url"
            :initialPlaylistData="plazaInitialData.playlist"
            @download-start="refreshLibraryData" 
            @play-cartridge="handlePlaySong" 
            @add-to-queue="addToQueue" 
            @context-menu="openContextMenu"
          />

          <!-- Library View / Cassette Collection -->
          <LibraryView 
            v-else-if="currentView === 'library'" 
            :folders="folders"
            :allSongs="allSongs"
            :statsData="rawStatsData"
            @open-folder="openFolder" 
            @play-song="handlePlaySong" 
            @add-to-queue="addToQueue"
            @context-menu="openContextMenu"
            @edit-metadata="openMetadataEditor"
          />

          <!-- Single Folder Detail View -->
          <FolderView 
            v-else-if="currentView === 'folder'" 
            :folderName="currentFolder" 
            @back="currentView = 'library'" 
            @play-song="handlePlaySong" 
            @add-to-queue="addToQueue" 
            @context-menu="openContextMenu"
            @edit-metadata="openMetadataEditor"
          />

          <!-- Playlists & Smart Crates -->
          <PlaylistsView
            v-else-if="currentView === 'playlists'"
            :allSongs="allSongs"
            :statsData="rawStatsData"
            @play-song="handlePlaySong"
            @add-to-queue="addToQueue"
            @context-menu="openContextMenu"
            @sync-playlist="handleSyncPlaylist"
          />

          <!-- Plaza View (P2P Community Hub) -->
          <PlazaView
            v-else-if="currentView === 'plaza'"
            @download-playlist="handlePlazaDownload"
            @navigate="navigateView"
          />
        </div>

        <!-- Permanent Right Player Dock with Integrated Equalizer -->
        <AudioPlayer 
          :currentSong="currentSong"
          :isPlaying="isPlaying"
          :isShuffle="isShuffle"
          :repeatMode="repeatMode"
          :isQueueOpen="isQueueOpen"
          :isEqOpen="isEqOpen"
          @play="handlePlay"
          @pause="isPlaying = false"
          @next="nextSong"
          @prev="prevSong"
          @seek="seekAudio"
          @toggle-queue="isQueueOpen = !isQueueOpen"
          @toggle-eq="isEqOpen = !isEqOpen"
          @toggle-shuffle="isShuffle = !isShuffle"
          @toggle-repeat="repeatMode = $event"
          @toggle-expand="showExpandedPlayer = true"
          @volume-change="setVolume"
          @ended="nextSong"
          @init-audio="initAudio"
          @time-update="updateSongTime"
          @change-band="updateEq"
        />
      </div>

      <!-- System Footer Dock (Theme Switcher & Hardware Specs) -->
      <footer class="system-footer-dock">
        <div class="footer-left">
          <span class="system-badge">BAILANDO SOLO V2.0</span>
          <span class="system-meta-text">{{ allSongs.length }} Pistas · {{ folders.length }} Casetes</span>
        </div>

        <div class="footer-right">
          <ThemeSelector 
            :showExperimental="true" 
            @theme-change="currentTheme = $event" 
            @open-stats="showStats = true" 
          />
        </div>
      </footer>
    </div>

    <!-- Global Modals & Overlays -->
    <ExpandedPlayerView 
      :isOpen="showExpandedPlayer"
      :currentSong="currentSong"
      :isPlaying="isPlaying"
      :currentTime="currentSongTime"
      :duration="songDuration"
      :isShuffle="isShuffle"
      :repeatMode="repeatMode"
      :isEqOpen="isEqOpen"
      :isQueueOpen="isQueueOpen"
      :queue="queue"
      :analyserNode="analyserNode"
      @close="showExpandedPlayer = false"
      @play="handlePlay"
      @pause="isPlaying = false"
      @prev="prevSong"
      @next="nextSong"
      @seek="seekAudio"
      @toggle-shuffle="isShuffle = !isShuffle"
      @toggle-repeat="repeatMode = $event"
      @toggle-eq="isEqOpen = !isEqOpen"
      @toggle-queue="isQueueOpen = !isQueueOpen"
      @volume-change="setVolume"
      @play-queue-item="playQueueItem"
      @remove-queue-item="removeFromQueue"
    />

    <GlobalSearchModal 
      :isOpen="showSearchModal"
      :allSongs="allSongs"
      :folders="folders"
      :playlists="playlists"
      @close="showSearchModal = false"
      @play-song="handlePlaySong"
      @open-folder="openFolder"
      @add-to-queue="addToQueue"
    />

    <MetadataEditorModal 
      :isOpen="showMetadataModal"
      :song="editingSong"
      @close="showMetadataModal = false"
      @saved="handleMetadataSaved"
    />

    <ContextMenu 
      :show="contextMenuState.show"
      :x="contextMenuState.x"
      :y="contextMenuState.y"
      :song="contextMenuState.song"
      @close="contextMenuState.show = false"
      @action="handleContextMenuAction"
    />

    <QueuePanel 
      :queue="queue" 
      :isOpen="isQueueOpen" 
      @close="isQueueOpen = false" 
      @remove-item="removeFromQueue" 
      @play-item="playQueueItem" 
      @move-item="moveQueueItem"
      @clear-queue="queue = []"
      @save-as-playlist="saveQueueAsPlaylist"
    />

    <StatisticsDashboard :isOpen="showStats" @close="showStats = false" />
    
    <MobileDownloadQR :isOpen="showQRModal" @close="showQRModal = false" />
    
    <ProfileManager :isOpen="showProfileModal" @close="showProfileModal = false" @profile-changed="handleProfileChange" />

    <ParallaxManager 
      :isPlaying="isPlaying"
      :currentSongTime="currentSongTime"
      :songDuration="songDuration"
      @toggle-experimental="showExperimental = $event"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import AppHeader from './components/AppHeader.vue'
import DownloaderView from './components/DownloaderView.vue'
import LibraryView from './components/LibraryView.vue'
import FolderView from './components/FolderView.vue'
import PlaylistsView from './components/PlaylistsView.vue'
import PlazaView from './components/PlazaView.vue'
import AudioPlayer from './components/AudioPlayer.vue'
import ExpandedPlayerView from './components/ExpandedPlayerView.vue'
import GlobalSearchModal from './components/GlobalSearchModal.vue'
import MetadataEditorModal from './components/MetadataEditorModal.vue'
import ContextMenu from './components/ContextMenu.vue'
import QueuePanel from './components/QueuePanel.vue'
import ThemeSelector from './components/ThemeSelector.vue'
import StatisticsDashboard from './components/StatisticsDashboard.vue'
import MobileDownloadQR from './components/MobileDownloadQR.vue'
import ProfileManager from './components/ProfileManager.vue'
import ParallaxManager from './components/ParallaxManager.vue'

import { LibraryService } from './services/LibraryService'
import { PlaylistService } from './services/PlaylistService'
import { StatsService } from './services/StatsService'
import { PlazaService } from './services/PlazaService'

// Navigation & View State (Default to downloader as primary console experience)
const currentView = ref('downloader')
const currentFolder = ref('')
const plazaInitialData = ref({ url: '', playlist: null })

// Library & Playlists Data
const folders = ref([])
const allSongs = ref([])
const playlists = ref([])
const rawStatsData = ref({})

// Player State
const currentSong = ref(null)
const isPlaying = ref(false)
const isShuffle = ref(false)
const repeatMode = ref('off')
const isQueueOpen = ref(false)
const isEqOpen = ref(false)
const queue = ref([])
const currentPlaylist = ref([])
const currentIndex = ref(-1)

// Time & Audio API State
const currentSongTime = ref(0)
const songDuration = ref(0)
const audioElement = ref(null)
const analyserNode = ref(null)
let audioContext = null
let gainNode = null
let eqBands = []
let canvasEl = null
let canvasCtx = null

// Modals State
const showExpandedPlayer = ref(false)
const showSearchModal = ref(false)
const showMetadataModal = ref(false)
const editingSong = ref(null)
const showStats = ref(false)
const showProfileModal = ref(false)
const showQRModal = ref(false)
const showExperimental = ref(true)
const currentTheme = ref('snes')

// Context Menu State
const contextMenuState = ref({
  show: false,
  x: 0,
  y: 0,
  song: null
})

// Stats Tracking
let lastTrackedTime = 0
const TRACK_INTERVAL = 5

watch(currentSong, (newSong) => {
  if (newSong) {
    StatsService.trackPlay(newSong)
    lastTrackedTime = 0
  }
})

// Broadcast real-time presence and "Now Playing" to decentralized Nostr network
watch([currentSong, isPlaying], ([newSong, playing]) => {
  if (newSong && playing) {
    PlazaService.publishNowPlaying({
      title: newSong.title,
      artist: newSong.artist || newSong.uploader || '',
      isPlaying: true
    })
  } else if (newSong && !playing) {
    PlazaService.publishNowPlaying({
      title: newSong.title,
      artist: newSong.artist || newSong.uploader || '',
      isPlaying: false
    })
  }
})

watch(currentSongTime, (newTime) => {
  if (!currentSong.value || !isPlaying.value) return
  if (newTime - lastTrackedTime >= TRACK_INTERVAL) {
    StatsService.trackTime(currentSong.value, newTime - lastTrackedTime)
    lastTrackedTime = newTime
  }
})

const handlePlazaDownload = (pl) => {
  if (!pl) return
  PlazaService.recordDownload(pl.id, pl.url)
  plazaInitialData.value = {
    url: pl.url,
    playlist: {
      title: pl.title,
      songs: (pl.songs || []).map(s => ({
        ...s,
        status: 'idle',
        percent: 0,
        speed: 0
      }))
    }
  }
  currentView.value = 'downloader'
}

const updateSongTime = ({ currentTime, duration }) => {
  currentSongTime.value = currentTime
  songDuration.value = duration
}

// ─── Data Fetching ─────────────────────────────────────────────────────────────

const refreshLibraryData = async (retries = 2) => {
  try {
    const [fList, sList, pList, stats] = await Promise.all([
      LibraryService.getFolders(),
      LibraryService.getAllSongs(),
      PlaylistService.getPlaylists(),
      StatsService.getStats()
    ])
    folders.value = fList || []
    allSongs.value = sList || []
    playlists.value = pList || []
    rawStatsData.value = stats || {}
  } catch (e) {
    console.error('Error loading library data:', e)
    if (retries > 0) {
      setTimeout(() => refreshLibraryData(retries - 1), 1000)
    }
  }
}

onMounted(() => {
  refreshLibraryData()
})

// ─── Web Audio API Initialization ─────────────────────────────────────────────

const initAudio = ({ audio, canvas }) => {
  if (audioContext) return
  audioElement.value = audio

  try {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext
    audioContext = new AudioContextClass()
    const analyser = audioContext.createAnalyser()
    analyser.fftSize = 128
    analyserNode.value = analyser

    gainNode = audioContext.createGain()
    const source = audioContext.createMediaElementSource(audio)

    const freqs = [60, 310, 1000, 6000, 16000]
    eqBands = freqs.map(f => {
      const filter = audioContext.createBiquadFilter()
      filter.type = 'peaking'
      filter.frequency.value = f
      filter.Q.value = 1
      filter.gain.value = 0
      return filter
    })

    let currentNode = source
    eqBands.forEach(band => {
      currentNode.connect(band)
      currentNode = band
    })

    currentNode.connect(gainNode)
    gainNode.connect(analyser)
    analyser.connect(audioContext.destination)

    canvasEl = canvas
    if (canvasEl) {
      canvasCtx = canvasEl.getContext('2d')
      canvasEl.width = 400
      canvasEl.height = 400
      drawVisualizer()
    }

    const unlockAudio = () => {
      if (audioContext && audioContext.state === 'suspended') {
        audioContext.resume().then(() => console.log('AudioContext resumed'))
      }
    }
    window.addEventListener('click', unlockAudio, { passive: true })
    window.addEventListener('keydown', unlockAudio, { passive: true })
  } catch (e) {
    console.error('Web Audio API error:', e)
  }
}

const drawVisualizer = () => {
  requestAnimationFrame(drawVisualizer)
  if (!analyserNode.value || !canvasCtx || !canvasEl) return

  const bufferLength = analyserNode.value.frequencyBinCount
  const dataArray = new Uint8Array(bufferLength)
  analyserNode.value.getByteFrequencyData(dataArray)

  canvasCtx.clearRect(0, 0, canvasEl.width, canvasEl.height)
  const centerX = canvasEl.width / 2
  const centerY = canvasEl.height / 2
  const radius = 130

  for (let i = 0; i < bufferLength; i++) {
    const barHeight = (dataArray[i] / 255) * 60
    const angle = (i / bufferLength) * 2 * Math.PI - Math.PI / 2

    const x1 = centerX + Math.cos(angle) * radius
    const y1 = centerY + Math.sin(angle) * radius
    const x2 = centerX + Math.cos(angle) * (radius + barHeight)
    const y2 = centerY + Math.sin(angle) * (radius + barHeight)

    canvasCtx.beginPath()
    canvasCtx.moveTo(x1, y1)
    canvasCtx.lineTo(x2, y2)
    canvasCtx.lineWidth = 4
    canvasCtx.strokeStyle = `rgba(0, 168, 225, ${Math.max(0.2, dataArray[i] / 255)})`
    canvasCtx.lineCap = 'round'
    canvasCtx.stroke()
  }
}

// ─── Playback Controls ─────────────────────────────────────────────────────────

const handlePlay = () => {
  if (!currentSong.value && allSongs.value.length > 0) {
    handlePlaySong({ song: allSongs.value[0], index: 0, list: allSongs.value })
    return
  }
  isPlaying.value = true
  if (audioContext && audioContext.state === 'suspended') {
    audioContext.resume()
  }
}

const handlePlaySong = ({ song, index, list }) => {
  currentPlaylist.value = list || allSongs.value
  currentIndex.value = index !== undefined ? index : currentPlaylist.value.findIndex(s => s.path === song.path)
  currentSong.value = song
  isPlaying.value = true

  if (audioContext && audioContext.state === 'suspended') {
    audioContext.resume()
  }
}

const nextSong = () => {
  if (queue.value.length > 0) {
    const next = queue.value.shift()
    currentSong.value = next
    isPlaying.value = true
    if (audioContext && audioContext.state === 'suspended') {
      audioContext.resume()
    }
    return
  }

  if (currentPlaylist.value.length === 0) return

  if (isShuffle.value) {
    currentIndex.value = Math.floor(Math.random() * currentPlaylist.value.length)
  } else {
    currentIndex.value = (currentIndex.value + 1) % currentPlaylist.value.length
  }
  currentSong.value = currentPlaylist.value[currentIndex.value]
  isPlaying.value = true
  if (audioContext && audioContext.state === 'suspended') {
    audioContext.resume()
  }
}

const prevSong = () => {
  if (currentPlaylist.value.length === 0) return
  currentIndex.value = (currentIndex.value - 1 + currentPlaylist.value.length) % currentPlaylist.value.length
  currentSong.value = currentPlaylist.value[currentIndex.value]
  isPlaying.value = true
  if (audioContext && audioContext.state === 'suspended') {
    audioContext.resume()
  }
}

const seekAudio = (time) => {
  if (audioElement.value) {
    audioElement.value.currentTime = time
  }
}

const setVolume = (val) => {
  if (gainNode) gainNode.gain.value = val
  if (audioElement.value) audioElement.value.volume = val
}

const updateEq = ({ index, value }) => {
  if (eqBands[index]) eqBands[index].gain.value = value
}

// ─── Queue Management ─────────────────────────────────────────────────────────

const addToQueue = (song) => {
  queue.value.push(song)
  isQueueOpen.value = true
}

const playQueueItem = (index) => {
  const song = queue.value[index]
  queue.value.splice(index, 1)
  currentSong.value = song
  isPlaying.value = true
  if (audioContext && audioContext.state === 'suspended') {
    audioContext.resume()
  }
}

const removeFromQueue = (index) => {
  queue.value.splice(index, 1)
}

const moveQueueItem = ({ from, to }) => {
  const item = queue.value.splice(from, 1)[0]
  queue.value.splice(to, 0, item)
}

const saveQueueAsPlaylist = async () => {
  if (queue.value.length === 0) return
  const name = prompt('Nombre para la nueva playlist:')
  if (!name) return

  try {
    await PlaylistService.createPlaylist({
      name: name.trim(),
      type: 'custom',
      songs: [...queue.value]
    })
    await refreshLibraryData()
    alert(`Playlist "${name}" guardada con éxito.`)
  } catch (e) {
    alert(e.message)
  }
}

// ─── Navigation & Views ───────────────────────────────────────────────────────

const scrollToTop = () => {
  if (typeof window !== 'undefined') {
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' })
  }
}

watch(currentView, () => {
  scrollToTop()
})

const navigateView = (view) => {
  currentView.value = view
  scrollToTop()
}

const openFolder = (folder) => {
  currentFolder.value = folder
  currentView.value = 'folder'
  scrollToTop()
}

const handleSyncPlaylist = (pl) => {
  currentView.value = 'downloader'
  scrollToTop()
}

// ─── Context Menu & Modals ────────────────────────────────────────────────────

const openContextMenu = ({ event, song }) => {
  contextMenuState.value = {
    show: true,
    x: event.clientX,
    y: event.clientY,
    song: song
  }
}

const handleContextMenuAction = async ({ action, song }) => {
  if (!song) return

  if (action === 'play-now') {
    handlePlaySong({ song, list: [song] })
  } else if (action === 'play-next') {
    queue.value.unshift(song)
    isQueueOpen.value = true
  } else if (action === 'add-queue') {
    addToQueue(song)
  } else if (action === 'add-playlist') {
    if (playlists.value.length === 0) {
      alert('No tienes playlists creadas. Ve a la sección de Playlists para crear una.')
      return
    }
    const plName = prompt(`Selecciona playlist para agregar:\n${playlists.value.map((p, i) => `${i + 1}. ${p.name}`).join('\n')}\nIngresa el número:`)
    const idx = parseInt(plName) - 1
    if (idx >= 0 && idx < playlists.value.length) {
      await PlaylistService.addSongToPlaylist(playlists.value[idx].id, song)
      alert(`Canción agregada a "${playlists.value[idx].name}".`)
    }
  } else if (action === 'open-folder') {
    if (song.folder) openFolder(song.folder)
  } else if (action === 'edit-metadata') {
    openMetadataEditor(song)
  } else if (action === 'copy-info') {
    navigator.clipboard.writeText(`${song.title} - ${song.uploader || 'Desconocido'}`)
    alert('Información copiada al portapapeles.')
  } else if (action === 'delete') {
    if (confirm(`¿Eliminar permanentemente "${song.title}" de tu disco?`)) {
      await LibraryService.deleteSong(song.folder, song.filename)
      await refreshLibraryData()
    }
  }
}

const openMetadataEditor = (song) => {
  editingSong.value = song
  showMetadataModal.value = true
}

const handleMetadataSaved = async () => {
  await refreshLibraryData()
}

const handleProfileChange = () => {
  window.location.reload()
}

// ─── Global Keyboard Shortcuts ────────────────────────────────────────────────

const handleGlobalShortcuts = (e) => {
  if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return

  if (e.code === 'Space') {
    e.preventDefault()
    isPlaying.value = !isPlaying.value
  } else if (e.key === 'n' || e.key === 'N') {
    nextSong()
  } else if (e.key === 'p' || e.key === 'P') {
    prevSong()
  } else if (e.key === 'Escape') {
    isQueueOpen.value = false
    showSearchModal.value = false
    showProfileModal.value = false
    showQRModal.value = false
    showStats.value = false
    showExpandedPlayer.value = false
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleGlobalShortcuts)
  PlazaService.init()
})
</script>

<style scoped>
.main-content-zone {
  min-width: 0;
  overflow-anchor: none;
  display: flex;
  flex-direction: column;
}

.system-footer-dock {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding: 8px 12px;
  background: #1e1e1e;
  border: 3px solid #000000;
  box-shadow: inset 1px 1px 0px #444444;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.system-badge {
  font-family: var(--font-pixel);
  font-size: 8px;
  color: #39ff14;
}

.system-meta-text {
  font-family: var(--font-mono);
  font-size: 10px;
  color: #888888;
}
</style>
