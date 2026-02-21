/**
 * LyricsTranscriptionService
 * 
 * Este servicio maneja la transcripción y sincronización de letras en tiempo real.
 * 
 * IMPLEMENTACIÓN ACTUAL:
 * - Usa letras pre-sincronizadas (LRC format o JSON)
 * - Análisis de beat/tempo en tiempo real con Web Audio API
 * 
 * FUTURAS MEJORAS:
 * - WebGPU para procesamiento acelerado
 * - Web Speech API para transcripción en vivo
 * - Machine Learning para detección automática de palabras
 * - Sincronización automática basada en análisis espectral
 */

export class LyricsTranscriptionService {
    constructor() {
        this.audioContext = null
        this.analyser = null
        this.beatDetector = null
        this.lyricsData = []
        this.onBeatCallback = null
        this.onLyricChangeCallback = null
    }

    /**
   * Inicializa el servicio con un analyser existente
   * NOTA: No creamos un nuevo AudioContext porque App.vue ya tiene uno
   * Solo necesitamos acceso al analyser para obtener los datos de frecuencia
   */
    async initialize(existingAnalyser) {
        if (this.analyser) {
            return true
        }

        try {
            if (!existingAnalyser) {
                console.warn('No se proporcionó un analyser. Funcionalidad limitada.')
                return false
            }

            this.analyser = existingAnalyser
            console.log('✅ LyricsTranscriptionService inicializado con analyser existente')

            return true
        } catch (error) {
            console.error('Error initializing transcription service:', error)
            return false
        }
    }

    /**
     * Carga letras desde diferentes formatos
     */
    loadLyrics(lyrics, format = 'json') {
        if (format === 'json') {
            this.lyricsData = lyrics
        } else if (format === 'lrc') {
            this.lyricsData = this.parseLRC(lyrics)
        }
    }

    /**
     * Parser para formato LRC (Lyric file format)
     * Ejemplo: [00:12.00]Line of lyrics
     */
    parseLRC(lrcString) {
        const lines = lrcString.split('\n')
        const lyrics = []

        for (const line of lines) {
            const match = line.match(/\[(\d{2}):(\d{2})\.(\d{2})\](.+)/)
            if (match) {
                const minutes = parseInt(match[1])
                const seconds = parseInt(match[2])
                const centiseconds = parseInt(match[3])
                const text = match[4].trim()

                const timeInSeconds = minutes * 60 + seconds + centiseconds / 100

                lyrics.push({
                    start: timeInSeconds,
                    end: timeInSeconds + 3, // Default duration
                    text: text
                })
            }
        }

        // Ajustar end times
        for (let i = 0; i < lyrics.length - 1; i++) {
            lyrics[i].end = lyrics[i + 1].start
        }

        return lyrics
    }

    /**
     * Obtiene la línea de letra correspondiente al tiempo actual
     */
    getCurrentLyric(currentTime) {
        if (!this.lyricsData || this.lyricsData.length === 0) {
            return null
        }

        const index = this.lyricsData.findIndex(
            line => currentTime >= line.start && currentTime < line.end
        )

        if (index === -1) return null

        return {
            current: this.lyricsData[index],
            previous: index > 0 ? this.lyricsData[index - 1] : null,
            next: index < this.lyricsData.length - 1 ? this.lyricsData[index + 1] : null,
            progress: (currentTime - this.lyricsData[index].start) /
                (this.lyricsData[index].end - this.lyricsData[index].start)
        }
    }

    /**
     * Detecta beats en tiempo real
     */
    detectBeat() {
        if (!this.analyser) return { isBeat: false, intensity: 0 }

        const bufferLength = this.analyser.frequencyBinCount
        const dataArray = new Uint8Array(bufferLength)
        this.analyser.getByteFrequencyData(dataArray)

        // Analizar frecuencias bajas (bass) para detección de beat
        const bassRange = dataArray.slice(0, Math.floor(bufferLength * 0.1))
        const bassSum = bassRange.reduce((a, b) => a + b, 0)
        const bassAvg = bassSum / bassRange.length

        // Analizar frecuencias medias
        const midRange = dataArray.slice(
            Math.floor(bufferLength * 0.1),
            Math.floor(bufferLength * 0.5)
        )
        const midSum = midRange.reduce((a, b) => a + b, 0)
        const midAvg = midSum / midRange.length

        const isBeat = bassAvg > 180 || midAvg > 160
        const intensity = Math.max(bassAvg, midAvg) / 255

        return { isBeat, intensity, bassAvg, midAvg }
    }

    /**
     * Obtiene datos del espectro para visualización
     */
    getSpectrumData() {
        if (!this.analyser) return new Uint8Array(0)

        const bufferLength = this.analyser.frequencyBinCount
        const dataArray = new Uint8Array(bufferLength)
        this.analyser.getByteFrequencyData(dataArray)

        return dataArray
    }

    /**
     * Calcula el tempo/BPM estimado
     */
    estimateTempo() {
        // Implementación básica - puede mejorarse con algoritmos más avanzados
        const beat = this.detectBeat()

        if (!this.lastBeatTime) {
            this.lastBeatTime = Date.now()
            this.beatIntervals = []
            return 120 // BPM default
        }

        if (beat.isBeat) {
            const now = Date.now()
            const interval = now - this.lastBeatTime

            if (interval > 200 && interval < 2000) { // Filtrar beats falsos
                this.beatIntervals.push(interval)

                if (this.beatIntervals.length > 10) {
                    this.beatIntervals.shift()
                }

                this.lastBeatTime = now
            }
        }

        if (this.beatIntervals.length > 0) {
            const avgInterval = this.beatIntervals.reduce((a, b) => a + b) / this.beatIntervals.length
            return Math.round(60000 / avgInterval)
        }

        return 120
    }

    /**
     * Limpia recursos
     */
    cleanup() {
        if (this.audioContext) {
            this.audioContext.close()
            this.audioContext = null
        }
        this.analyser = null
        this.lyricsData = []
    }
}

// Instancia singleton
export const lyricsService = new LyricsTranscriptionService()

/**
 * EJEMPLO DE DATOS DE LETRAS
 * Este formato puede ser reemplazado por datos de una API o transcripción en vivo
 */
export const sampleLyrics = [
    { start: 0, end: 3.5, text: "Bailando bajo las estrellas" },
    { start: 3.5, end: 7, text: "Siento el ritmo llegar" },
    { start: 7, end: 10.5, text: "La música me llama" },
    { start: 10.5, end: 14, text: "No puedo parar de bailar" },
    { start: 14, end: 17.5, text: "Esta noche es perfecta" },
    { start: 17.5, end: 21, text: "Para perderme en tu mirada" },
    { start: 21, end: 24.5, text: "Cada paso una aventura" },
    { start: 24.5, end: 28, text: "Cada beat una emoción" },
    { start: 28, end: 31.5, text: "El mundo se detiene" },
    { start: 31.5, end: 35, text: "Cuando bailas junto a mí" },
    { start: 35, end: 38.5, text: "Las luces que nos rodean" },
    { start: 38.5, end: 42, text: "Son testigos de este amor" },
    { start: 42, end: 45.5, text: "Que late al compás" },
    { start: 45.5, end: 49, text: "De nuestra canción" },
    { start: 49, end: 52.5, text: "Bailando hasta el amanecer" },
    { start: 52.5, end: 56, text: "Sin miedo a nada más" }
]

/**
 * FORMATO LRC DE EJEMPLO
 */
export const sampleLRC = `
[00:00.00]Bailando bajo las estrellas
[00:03.50]Siento el ritmo llegar
[00:07.00]La música me llama
[00:10.50]No puedo parar de bailar
[00:14.00]Esta noche es perfecta
[00:17.50]Para perderme en tu mirada
[00:21.00]Cada paso una aventura
[00:24.50]Cada beat una emoción
[00:28.00]El mundo se detiene
[00:31.50]Cuando bailas junto a mí
[00:35.00]Las luces que nos rodean
[00:38.50]Son testigos de este amor
[00:42.00]Que late al compás
[00:45.50]De nuestra canción
[00:49.00]Bailando hasta el amanecer
[00:52.50]Sin miedo a nada más
`
