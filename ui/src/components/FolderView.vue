<template>
  <div class="panel">
    <button class="back-btn" @click="$emit('back')">← Volver</button>
    <h2 style="margin-bottom: 16px;">{{ folderName }}</h2>
    <div class="song-list">
        <div v-for="(song, index) in songs" :key="index" class="song-item" @click="$emit('play-song', { song, index, list: songs })">
             <img :src="getThumbnail(song)" class="song-thumb">
             <div class="song-info">
                <div class="song-title">{{ song.title }}</div>
                <div class="song-artist">{{ song.uploader || 'Desconocido' }}</div>
             </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps(['folderName'])
const emit = defineEmits(['back', 'play-song'])
const songs = ref([])
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
</script>
