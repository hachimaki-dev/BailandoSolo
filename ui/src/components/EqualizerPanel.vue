<template>
  <div class="eq-panel" :class="{ open: isOpen }">
    <div v-for="(band, index) in bands" :key="index" class="eq-band">
        <input type="range" class="eq-slider" :min="-12" :max="12" :value="band.gain" step="1" @input="updateGain(index, $event.target.value)">
        <span class="eq-label">{{ band.label }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps(['isOpen'])
const emit = defineEmits(['change-band'])

const bands = ref([
    { freq: 60, label: '60Hz', gain: 0 },
    { freq: 310, label: '310Hz', gain: 0 },
    { freq: 1000, label: '1kHz', gain: 0 },
    { freq: 6000, label: '6kHz', gain: 0 },
    { freq: 16000, label: '16kHz', gain: 0 }
])

const updateGain = (index, value) => {
    bands.value[index].gain = parseFloat(value)
    emit('change-band', { index, value: parseFloat(value) })
}
</script>
