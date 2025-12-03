<template>
  <div class="panel">
    <div class="input-group">
      <label>YouTube URL</label>
      <input type="text" v-model="url" placeholder="https://youtube.com/...">
    </div>
    <div class="input-group">
      <label>Carpeta</label>
      <input type="text" v-model="folder" placeholder="Mi Música">
    </div>
    <button class="primary" @click="analyze" :disabled="isAnalyzing">
      {{ isAnalyzing ? 'Analizando...' : 'Analizar Playlist' }}
    </button>

    <div v-if="playlist" class="results-container" style="margin-top: 24px;">
      <h3 style="margin-bottom: 8px;">{{ playlist.title }} ({{ playlist.count }} canciones)</h3>
      <button class="primary" @click="download" style="margin-bottom: 16px;">Descargar Todo</button>
      <div class="song-list">
        <div v-for="song in playlist.songs" :key="song.id" class="song-item" :class="{ downloading: song.status === 'downloading', finished: song.status === 'finished' }">
          <img :src="song.thumbnail || defaultThumb" class="song-thumb">
          <div class="song-info">
            <div class="song-title">{{ song.title }}</div>
            <div class="song-artist">{{ song.uploader || 'Desconocido' }}</div>
          </div>
          <div class="song-progress-bar" :style="{ width: song.percent + '%' }"></div>
          <div class="song-status">{{ song.statusText || 'Esperando...' }}</div>
        </div>
      </div>
    </div>
    
    <!-- Quick Play Section -->
     <div style="margin-top: 40px;">
        <h3 style="margin-bottom: 16px; opacity: 0.8;">Juego Rápido (Biblioteca)</h3>
        <div class="cartridge-grid">
            <div v-for="(song, index) in quickPlaySongs" :key="index" class="cartridge-item" @click="playCartridge(song, index)">
                <div class="cartridge-label">
                    <img :src="getThumbnail(song)" :alt="song.title">
                    <div class="cartridge-overlay">
                        <div class="cartridge-play-btn">▶</div>
                    </div>
                </div>
                <div style="font-size: 10px; margin-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-align: center; font-weight: bold; opacity: 0.7;">
                    {{ song.title }}
                </div>
            </div>
             <div v-if="quickPlaySongs.length === 0" style="padding: 20px; text-align: center; color: #999;">
                {{ loadingQuickPlay ? 'Cargando...' : 'No hay canciones en la biblioteca aún' }}
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted, onMounted } from 'vue'

const url = ref('')
const folder = ref('')
const isAnalyzing = ref(false)
const playlist = ref(null)
const defaultThumb = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='48'%3E%3Crect fill='%23e5e7eb' width='48' height='48'/%3E%3C/svg%3E"
let pollInterval = null

const quickPlaySongs = ref([])
const loadingQuickPlay = ref(false)
const emit = defineEmits(['download-start', 'play-cartridge'])

const loadQuickPlay = async () => {
    loadingQuickPlay.value = true
    try {
        const response = await fetch('http://localhost:5001/api/library/random');
        if (response.ok) {
            quickPlaySongs.value = await response.json();
        }
    } catch (e) {
        console.error("Error loading quick play:", e);
    } finally {
        loadingQuickPlay.value = false
    }
}

const getThumbnail = (song) => {
    if (song.thumbnail) return 'http://localhost:5001' + song.thumbnail
    // Deterministic random cover
    const hash = song.title.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const coverNum = (hash % 7) + 1;
    return new URL(`../assets/styles/no_cover/${coverNum}.png`, import.meta.url).href
}

const playCartridge = (song, index) => {
    emit('play-cartridge', { song, index, list: quickPlaySongs.value })
}

onMounted(() => {
    loadQuickPlay()
})


const analyze = async () => {
  if (!url.value) return
  isAnalyzing.value = true
  try {
    const response = await fetch('http://localhost:5001/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.value })
    });
    const data = await response.json();
    // Add status fields to songs
    data.songs = data.songs.map(s => ({ ...s, status: 'waiting', percent: 0, statusText: 'Esperando...' }))
    playlist.value = data
    if (!folder.value && data.title) {
        folder.value = data.title.replace(/[^a-z0-9]/gi, '_').toLowerCase();
    }
  } catch (e) {
    alert('Error: ' + e.message)
  } finally {
    isAnalyzing.value = false
  }
}

const download = async () => {
    if (!playlist.value) return;
    try {
        await fetch('http://localhost:5001/api/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: url.value,
                folder_name: folder.value,
                selected_ids: playlist.value.songs.map(s => s.id)
            })
        });
        
        // Start polling
        if (pollInterval) clearInterval(pollInterval);
        pollInterval = setInterval(updateDownloadProgress, 1000);
        
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

const updateDownloadProgress = async () => {
    try {
        const res = await fetch('http://localhost:5001/api/status');
        const statusMap = await res.json();
        
        if (playlist.value && playlist.value.songs) {
            playlist.value.songs.forEach(song => {
                const status = statusMap[song.id];
                if (status) {
                    if (status.status === 'downloading') {
                        song.percent = status.percent;
                        song.statusText = Math.round(status.percent) + '%';
                        song.status = 'downloading';
                    } else if (status.status === 'finished') {
                        song.percent = 100;
                        song.statusText = '✓ Listo';
                        song.status = 'finished';
                    }
                }
            });
        }
    } catch (e) {
        console.error("Polling error:", e);
    }
}

onUnmounted(() => {
    if (pollInterval) clearInterval(pollInterval)
})
</script>
