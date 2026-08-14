<template>
  <div v-show="isOpen" class="eq-embedded-rack">
    <div class="eq-rack-header">
      <span class="eq-rack-title">🎚 Ecualizador (5 Bandas)</span>
      <button class="btn-retro-secondary btn-mini" @click="resetEq" title="Restablecer EQ a 0dB">
        RESET
      </button>
    </div>

    <div class="eq-sliders-row">
      <div v-for="(band, index) in bands" :key="index" class="eq-band-column">
        <span class="eq-gain-val">{{ band.gain > 0 ? `+${band.gain}` : band.gain }}dB</span>
        <div class="eq-track-wrapper">
          <input 
            type="range" 
            class="eq-vertical-slider" 
            :min="-12" 
            :max="12" 
            :value="band.gain" 
            step="1" 
            @input="updateGain(index, $event.target.value)"
          />
        </div>
        <span class="eq-freq-label">{{ band.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['change-band'])

const bands = ref([
  { freq: 60, label: '60Hz', gain: 0 },
  { freq: 310, label: '310Hz', gain: 0 },
  { freq: 1000, label: '1kHz', gain: 0 },
  { freq: 6000, label: '6kHz', gain: 0 },
  { freq: 16000, label: '16kHz', gain: 0 }
])

const updateGain = (index, value) => {
  const numVal = parseFloat(value)
  bands.value[index].gain = numVal
  emit('change-band', { index, value: numVal })
}

const resetEq = () => {
  bands.value.forEach((b, i) => {
    b.gain = 0
    emit('change-band', { index: i, value: 0 })
  })
}
</script>

<style scoped>
.eq-embedded-rack {
  position: relative;
  z-index: 10000;
  background: #111111;
  border: 2px solid #000000;
  padding: 10px;
  margin-top: 10px;
  box-shadow: inset 2px 2px 4px rgba(0, 0, 0, 0.9), 2px 2px 0px rgba(255, 255, 255, 0.4);
  animation: slideDown 0.15s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.eq-rack-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 4px;
  border-bottom: 1px solid #333333;
}

.eq-rack-title {
  font-family: var(--font-pixel);
  font-size: 7px;
  color: #00f0ff;
  letter-spacing: 0.5px;
}

.btn-mini {
  padding: 2px 6px;
  font-size: 7px;
  height: auto;
}

.eq-sliders-row {
  display: flex;
  justify-content: space-around;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
}

.eq-band-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.eq-gain-val {
  font-family: var(--font-mono);
  font-size: 9px;
  color: #39ff14;
  font-weight: bold;
}

.eq-track-wrapper {
  height: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.eq-vertical-slider {
  writing-mode: bt-lr;
  -webkit-appearance: slider-vertical;
  appearance: slider-vertical;
  width: 14px;
  height: 80px;
  background: #222222;
  cursor: pointer;
  accent-color: #00A8E1;
}

.eq-freq-label {
  font-family: var(--font-pixel);
  font-size: 7px;
  color: #aaaaaa;
}
</style>
