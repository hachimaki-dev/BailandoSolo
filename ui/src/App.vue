<template>
  <div class="container">
    <AppHeader :currentView="currentView" @navigate="currentView = $event" />

    <div class="main-grid">
      <div>
        <DownloaderView v-show="currentView === 'downloader'" @play-cartridge="playSong" @add-to-queue="addToQueue" />
        <LibraryView v-if="currentView === 'library'" @open-folder="openFolder" />
        <FolderView v-if="currentView === 'folder'" :folderName="currentFolder" @back="currentView = 'library'" @play-song="playSong" @add-to-queue="addToQueue" />
      </div>

      <AudioPlayer 
        :currentSong="currentSong"
        :isPlaying="isPlaying"
        :isShuffle="isShuffle"
        :isQueueOpen="isQueueOpen"
        :isEqOpen="isEqOpen"
        @play="isPlaying = true"
        @pause="isPlaying = false"
        @next="nextSong"
        @prev="prevSong"
        @toggle-queue="isQueueOpen = !isQueueOpen"
        @toggle-eq="isEqOpen = !isEqOpen"
        @toggle-shuffle="isShuffle = !isShuffle"
        @volume-change="setVolume"
        @ended="nextSong"
        @init-audio="initAudio"
        @time-update="updateSongTime"
      />
    </div>
  </div>

  <ParallaxManager 
    :isPlaying="isPlaying"
    :currentSongTime="currentSongTime"
    :songDuration="songDuration"
  />
  <QueuePanel :queue="queue" :isOpen="isQueueOpen" @close="isQueueOpen = false" @remove-item="removeFromQueue" @play-item="playQueueItem" />
  <EqualizerPanel :isOpen="isEqOpen" @change-band="updateEq" />
  <ThemeSelector @theme-change="currentTheme = $event" />
  <LyricsKaraoke 
    v-if="currentTheme === 'karaoke' && currentSong"
    :isPlaying="isPlaying"
    :currentSong="currentSong"
    :currentTime="currentSongTime"
    :duration="songDuration"
    :analyser="analyserNode"
  />
</template>

<script setup>
import { ref, provide, computed, onMounted } from 'vue'
import AppHeader from './components/AppHeader.vue'
import DownloaderView from './components/DownloaderView.vue'
import LibraryView from './components/LibraryView.vue'
import FolderView from './components/FolderView.vue'
import AudioPlayer from './components/AudioPlayer.vue'
import QueuePanel from './components/QueuePanel.vue'
import EqualizerPanel from './components/EqualizerPanel.vue'
import ThemeSelector from './components/ThemeSelector.vue'
import ParallaxManager from './components/ParallaxManager.vue'
import LyricsKaraoke from './components/LyricsKaraoke.vue'

const currentView = ref('downloader')
const currentFolder = ref('')
const currentSong = ref(null)
const isPlaying = ref(false)
const isShuffle = ref(false)
const isQueueOpen = ref(false)
const isEqOpen = ref(false)
const queue = ref([])
const currentPlaylist = ref([]) // List of songs currently playing from (folder or queue)
const currentIndex = ref(-1)

const currentSongTime = ref(0)
const songDuration = ref(0)
const audioElement = ref(null)
const analyserNode = ref(null)
const currentTheme = ref('wiiu')

const updateSongTime = ({ currentTime, duration }) => {
    currentSongTime.value = currentTime
    songDuration.value = duration
}

// Audio Context
let audioContext
let analyser
let source
let gainNode
let eqBands = []
let canvasCtx
let canvasEl

const initAudio = ({ audio, canvas }) => {
    if (audioContext) return
    audioElement.value = audio // Store audio element reference
    try {
        const AudioContext = window.AudioContext || window.webkitAudioContext
        audioContext = new AudioContext()
        analyser = audioContext.createAnalyser()
        analyser.fftSize = 128
        analyserNode.value = analyser // Store analyser for LyricsKaraoke

        gainNode = audioContext.createGain()
        
        source = audioContext.createMediaElementSource(audio)

        // Create EQ Bands
        const freqs = [60, 310, 1000, 6000, 16000]
        eqBands = freqs.map(f => {
            const filter = audioContext.createBiquadFilter()
            filter.type = 'peaking'
            filter.frequency.value = f
            filter.Q.value = 1
            filter.gain.value = 0
            return filter
        })

        // Connect Chain
        let currentNode = source
        eqBands.forEach(band => {
            currentNode.connect(band)
            currentNode = band
        })

        currentNode.connect(gainNode)
        gainNode.connect(analyser)
        analyser.connect(audioContext.destination)

        canvasEl = canvas
        canvasCtx = canvas.getContext('2d')
        canvas.width = 400
        canvas.height = 400
        drawVisualizer()
    } catch (e) {
        console.error("Web Audio API error:", e)
    }
}

const drawVisualizer = () => {
    requestAnimationFrame(drawVisualizer)
    if (!analyser || !canvasCtx) return

    const bufferLength = analyser.frequencyBinCount
    const dataArray = new Uint8Array(bufferLength)
    analyser.getByteFrequencyData(dataArray)

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
        // Use a dynamic color or fixed
        canvasCtx.strokeStyle = `rgba(0, 168, 225, ${dataArray[i] / 255})`
        canvasCtx.lineCap = 'round'
        canvasCtx.stroke()
    }
}

const openFolder = (folder) => {
    currentFolder.value = folder
    currentView.value = 'folder'
}

const playSong = ({ song, index, list }) => {
    currentPlaylist.value = list
    currentIndex.value = index
    currentSong.value = song
    isPlaying.value = true
    
    // Resume context if suspended
    if (audioContext && audioContext.state === 'suspended') {
        audioContext.resume()
    }
}

const nextSong = () => {
    if (queue.value.length > 0) {
        const next = queue.value.shift()
        currentSong.value = next
        isPlaying.value = true
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
}

const prevSong = () => {
    if (currentPlaylist.value.length === 0) return
    currentIndex.value = (currentIndex.value - 1 + currentPlaylist.value.length) % currentPlaylist.value.length
    currentSong.value = currentPlaylist.value[currentIndex.value]
    isPlaying.value = true
}

const setVolume = (val) => {
    if (gainNode) gainNode.gain.value = val
}

const updateEq = ({ index, value }) => {
    if (eqBands[index]) eqBands[index].gain.value = value
}

const removeFromQueue = (index) => {
    queue.value.splice(index, 1)
}

const playQueueItem = (index) => {
    const song = queue.value[index]
    queue.value.splice(index, 1)
    currentSong.value = song
    isPlaying.value = true
}

const addToQueue = (song) => {
    queue.value.push(song)
    isQueueOpen.value = true
    // Optional: Show a notification
    console.log('Added to queue:', song.title)
}

</script>
