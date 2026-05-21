
const API_URL = '/api/stats';

export const StatsService = {
    async trackPlay(song) {
        try {
            await fetch(`${API_URL}/track`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'play',
                    song_id: song.filename, // Using filename as ID for now
                    title: song.title
                })
            });
        } catch (e) {
            console.error("Error tracking play:", e);
        }
    },

    async trackTime(song, duration) {
        try {
            await fetch(`${API_URL}/track`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'time_update',
                    song_id: song.filename,
                    duration: duration
                })
            });
        } catch (e) {
            console.error("Error tracking time:", e);
        }
    },

    async getStats() {
        try {
            const res = await fetch(API_URL);
            if (!res.ok) {
                console.error(`Stats API returned ${res.status}: ${res.statusText}`);
                const text = await res.text();
                console.error('Response body:', text);
                return null;
            }
            const data = await res.json();
            return data;
        } catch (e) {
            console.error("Error fetching stats:", e);
            return null;
        }
    }
};
