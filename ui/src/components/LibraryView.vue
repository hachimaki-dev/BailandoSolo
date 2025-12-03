<template>
  <div class="panel">
    <h2 style="margin-bottom: 16px;">Mis Carpetas</h2>
    <div class="folder-grid">
      <div v-for="folder in folders" :key="folder" class="folder-item" @click="$emit('open-folder', folder)">
        <svg class="folder-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
        </svg>
        <div class="folder-name">{{ folder }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const folders = ref([])
const emit = defineEmits(['open-folder'])

const loadLibrary = async () => {
    try {
        const response = await fetch('http://localhost:5001/api/library');
        folders.value = await response.json();
    } catch (error) {
        console.error(error);
    }
}

onMounted(() => {
    loadLibrary()
})
</script>
