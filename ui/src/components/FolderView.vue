<template>
  <div class="panel">
    <button class="back-btn" @click="$emit('back')">← Volver</button>
    <h2 style="margin-bottom: 16px;">{{ folderName }}</h2>
    <div class="song-list">
        <div v-for="(song, index) in songs" :key="index" class="song-item" @click="$emit('play-song', { song, index, list: songs })">
             <img :src="song.thumbnail || defaultThumb" class="song-thumb">
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
