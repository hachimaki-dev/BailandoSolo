<template>
  <div class="panel player">
    <h3 style="margin-bottom: 16px;">Reproductor</h3>
    <div class="album-art" id="albumArt">
        <canvas ref="canvas" id="visualizer"></canvas>
        <img v-if="currentSong && getThumbnail(currentSong)" :src="getThumbnail(currentSong)" id="albumImage">
        <div v-else id="defaultArt">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="48" height="48">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
        </div>
    </div>
    <div class="player-info">
        <div class="player-title">{{ currentSong ? currentSong.title : 'Sin música' }}</div>
        <div class="player-artist">{{ currentSong ? (currentSong.uploader || 'Desconocido') : 'Selecciona una canción' }}</div>
    </div>

    <div class="progress-container" @click="seek" style="width: 100%; margin: 16px 0 8px;">
        <div class="progress-bar" style="width: 100%; height: 6px; background: rgba(0,0,0,0.1); border-radius: 3px; overflow: hidden;">
            <div class="progress-fill" :style="{ width: progress + '%' }" style="height: 100%; background: #00A8E1; border-radius: 3px; transition: width 0.1s linear;"></div>
        </div>
    </div>

    <div class="controls">
        <button class="control-btn" @click="$emit('prev')">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path d="M8.445 14.832A1 1 0 0010 14v-2.798l5.445 3.63A1 1 0 0017 14V6a1 1 0 00-1.555-.832L10 8.798V6a1 1 0 00-1.555-.832l-6 4a1 1 0 000 1.664l6 4z" />
            </svg>
        </button>
        <button class="control-btn play" @click="togglePlay">
            <svg v-if="!isPlaying" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
        </button>
        <button class="control-btn" @click="$emit('next')">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path d="M4.555 5.168A1 1 0 003 6v8a1 1 0 001.555.832L10 11.202V14a1 1 0 001.555.832l6-4a1 1 0 000-1.664l-6-4A1 1 0 0010 6v2.798l-5.445-3.63z" />
            </svg>
        </button>
    </div>

    <div class="controls-extra">
        <button class="control-icon-btn" @click="$emit('toggle-queue')" :class="{ active: isQueueOpen }" title="Cola de Reproducción">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="8" y1="6" x2="21" y2="6"></line>
                <line x1="8" y1="12" x2="21" y2="12"></line>
                <line x1="8" y1="18" x2="21" y2="18"></line>
                <line x1="3" y1="6" x2="3.01" y2="6"></line>
                <line x1="3" y1="12" x2="3.01" y2="12"></line>
                <line x1="3" y1="18" x2="3.01" y2="18"></line>
            </svg>
        </button>
        <button class="control-icon-btn" @click="$emit('toggle-shuffle')" :class="{ active: isShuffle }" title="Aleatorio">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="16 3 21 3 21 8"></polyline>
                <line x1="4" y1="20" x2="21" y2="3"></line>
                <polyline points="21 16 21 21 16 21"></polyline>
                <line x1="15" y1="15" x2="21" y2="21"></line>
                <line x1="4" y1="4" x2="9" y2="9"></line>
            </svg>
        </button>
        <button class="control-icon-btn" @click="$emit('toggle-eq')" :class="{ active: isEqOpen }" title="Ecualizador">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 20v-8a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v8"></path>
                <path d="M11 20V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v16"></path>
                <path d="M19 20v-5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v5"></path>
            </svg>
        </button>
        <div style="display: flex; align-items: center; gap: 5px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
            </svg>
            <input type="range" v-model="volume" min="0" max="1" step="0.05" @input="$emit('volume-change', volume)">
        </div>
    </div>

    <div class="time-info">
        <span>{{ formatTime(currentTime) }}</span>
        <span>{{ formatTime(duration) }}</span>
    </div>
    
    <audio ref="audio" crossorigin="anonymous" @timeupdate="updateTime" @ended="$emit('ended')"></audio>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps(['currentSong', 'isPlaying', 'isShuffle', 'isQueueOpen', 'isEqOpen'])
const emit = defineEmits(['play', 'pause', 'next', 'prev', 'seek', 'volume-change', 'toggle-queue', 'toggle-eq', 'toggle-shuffle', 'ended', 'init-audio', 'time-update'])

const audio = ref(null)
const canvas = ref(null)
const progress = ref(0)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(1)

const togglePlay = () => {
    if (props.isPlaying) {
        emit('pause')
        audio.value.pause()
    } else {
        emit('play')
        audio.value.play()
    }
}

const updateTime = () => {
    if (!audio.value) return
    currentTime.value = audio.value.currentTime
    duration.value = audio.value.duration || 0
    progress.value = (currentTime.value / duration.value) * 100 || 0
    emit('time-update', { currentTime: currentTime.value, duration: duration.value })
}

const seek = (e) => {
    if (!audio.value || !duration.value) return
    const rect = e.currentTarget.getBoundingClientRect()
    const pos = (e.clientX - rect.left) / rect.width
    audio.value.currentTime = pos * duration.value
}

const formatTime = (seconds) => {
    if (!seconds) return '0:00'
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`
}

const getThumbnail = (song) => {
    if (!song) return null
    
    // If thumbnail exists and starts with http, use it directly
    if (song.thumbnail && song.thumbnail.startsWith('http')) {
        return song.thumbnail
    }
    
    // If thumbnail exists and starts with /, prepend server URL
    if (song.thumbnail && song.thumbnail.startsWith('/')) {
        return 'http://localhost:5001' + song.thumbnail
    }
    
    // If thumbnail exists but is a relative path
    if (song.thumbnail) {
        return 'http://localhost:5001' + song.thumbnail
    }
    
    // Fallback to random cover based on title hash
    const hash = song.title.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
    const coverNum = (hash % 9) + 1
    return new URL(`../assets/styles/no_cover/${coverNum}.png`, import.meta.url).href
}

watch(() => props.currentSong, (newSong) => {
    if (newSong && audio.value) {
        if (newSong.url) {
             audio.value.src = newSong.url
             if (props.isPlaying) audio.value.play()
        } else if (newSong.path) {
             // Path already includes /api/stream/folder/filename
             audio.value.src = 'http://localhost:5001' + newSong.path
             if (props.isPlaying) audio.value.play()
        } else if (newSong.filename) {
             audio.value.src = `http://localhost:5001/api/stream/${encodeURIComponent(newSong.filename)}`
             if (props.isPlaying) audio.value.play()
        }
    }
})

watch(() => props.isPlaying, (playing) => {
    if (audio.value) {
        if (playing) audio.value.play()
        else audio.value.pause()
    }
})

onMounted(() => {
    emit('init-audio', { audio: audio.value, canvas: canvas.value })
})
</script>
