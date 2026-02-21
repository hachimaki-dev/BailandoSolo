<template>
  <div class="panel">
    <button class="back-btn" @click="$emit('back')">← Volver</button>
    <h2 style="margin-bottom: 16px;">{{ folderName }}</h2>
    <div class="song-list">
        <div v-for="(song, index) in songs" 
             :key="index" 
             class="song-item" 
             @click="$emit('play-song', { song, index, list: songs })"
             @mouseenter="startPreview(song)"
             @mouseleave="stopPreview"
             @contextmenu.prevent="showContextMenu($event, song)">
             <img :src="getThumbnail(song)" class="song-thumb">
             <div class="song-info">
                <div class="song-title">{{ song.title }}</div>
                <div class="song-artist">{{ song.uploader || 'Desconocido' }}</div>
             </div>
             <button class="queue-btn" @click.stop="addToQueue(song)" title="Agregar a la cola">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
             </button>
             <div v-if="previewingSong === song" class="preview-indicator">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
                </svg>
             </div>
        </div>
    </div>

    
    <!-- Context Menu -->
    <div v-if="contextMenu.show" 
         class="context-menu" 
         :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
         @click="hideContextMenu">
        <div class="context-menu-item" @click="addToQueue(contextMenu.song)">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            Agregar a la cola
        </div>
    </div>

    <audio ref="previewAudio" crossorigin="anonymous" style="display: none;"></audio>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps(['folderName'])
const emit = defineEmits(['back', 'play-song', 'add-to-queue'])
const songs = ref([])
const previewAudio = ref(null)
const previewingSong = ref(null)
const previewTimeout = ref(null)
const contextMenu = ref({ show: false, x: 0, y: 0, song: null })
const defaultThumb = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='48'%3E%3Crect fill='%23e5e7eb' width='48' height='48'/%3E%3C/svg%3E"

const getThumbnail = (song) => {
    if (!song) return defaultThumb
    
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

const startPreview = (song) => {
    if (!previewAudio.value || !song) return
    
    // Clear any existing timeout
    if (previewTimeout.value) {
        clearTimeout(previewTimeout.value)
    }
    
    // Set a small delay before starting preview (200ms)
    previewTimeout.value = setTimeout(() => {
        try {
            // Determine the audio source URL
            let audioUrl = ''
            if (song.url) {
                audioUrl = song.url
            } else if (song.path) {
                audioUrl = 'http://localhost:5001' + song.path
            } else if (song.filename) {
                audioUrl = `http://localhost:5001/api/stream/${encodeURIComponent(song.filename)}`
            }
            
            console.log('Starting preview for:', song.title, 'URL:', audioUrl)
            
            if (audioUrl) {
                const audio = previewAudio.value
                
                // Clean up any previous event listeners
                audio.onloadedmetadata = null
                audio.onerror = null
                
                // Set up event listener for when metadata is ready (to get duration)
                audio.onloadedmetadata = () => {
                    if (!audio.duration) return
                    
                    // Start from the middle
                    const startTime = audio.duration / 2
                    audio.currentTime = startTime
                    audio.volume = 0.3 // Start volume
                    
                    console.log('Audio loaded, starting playback at', startTime)
                    
                    audio.play().then(() => {
                        // Schedule fade out after 4 seconds (total 5s preview)
                        setTimeout(() => {
                            if (previewingSong.value === song) {
                                fadeOutAndStop()
                            }
                        }, 4000)
                    }).catch(err => {
                        console.error('Preview playback error:', err)
                    })
                }
                
                audio.onerror = (e) => {
                    console.error('Audio loading error:', e)
                }
                
                audio.src = audioUrl
                audio.load()
                
                previewingSong.value = song
            }
        } catch (error) {
            console.error('Error starting preview:', error)
        }
    }, 200)
}

const fadeOutAndStop = () => {
    const audio = previewAudio.value
    if (!audio) return
    
    const fadeInterval = setInterval(() => {
        if (audio.volume > 0.05) {
            audio.volume -= 0.05
        } else {
            clearInterval(fadeInterval)
            stopPreview()
        }
    }, 100) // Fade out over ~0.6s
}

const stopPreview = () => {
    if (previewTimeout.value) {
        clearTimeout(previewTimeout.value)
        previewTimeout.value = null
    }
    
    if (previewAudio.value) {
        previewAudio.value.pause()
        previewAudio.value.currentTime = 0
    }
    previewingSong.value = null
}

const loadFolder = async () => {
    if (!props.folderName) return
    try {
        const response = await fetch(`http://localhost:5001/api/library/${encodeURIComponent(props.folderName)}`);
        songs.value = await response.json();
    } catch (error) {
        console.error(error);
    }
}

watch(() => props.folderName, loadFolder)
onMounted(loadFolder)
onUnmounted(() => {
    stopPreview()
})

const showContextMenu = (event, song) => {
    contextMenu.value = {
        show: true,
        x: event.clientX,
        y: event.clientY,
        song: song
    }
}

const hideContextMenu = () => {
    contextMenu.value.show = false
}

const addToQueue = (song) => {
    emit('add-to-queue', song)
    hideContextMenu()
}
</script>

<style scoped>
.song-item {
    position: relative;
}

.preview-indicator {
    position: absolute;
    right: 16px;
    top: 50%;
    transform: translateY(-50%);
    color: #00A8E1;
    animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

.context-menu {
    position: fixed;
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    min-width: 180px;
    padding: 4px 0;
}

.context-menu-item {
    padding: 10px 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
    transition: background 0.2s;
}

.context-menu-item:hover {
    background: #f5f5f5;
}

.context-menu-item svg {
    color: #00A8E1;
}

.queue-btn {
    background: transparent;
    border: none;
    color: #00A8E1;
    cursor: pointer;
    padding: 8px;
    border-radius: 50%;
    opacity: 0;
    transition: all 0.2s;
    margin-right: 8px;
}

.song-item:hover .queue-btn {
    opacity: 1;
}

.queue-btn:hover {
    background: rgba(0, 168, 225, 0.1);
    transform: scale(1.1);
}
</style>
