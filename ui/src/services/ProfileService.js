const API_BASE = '/api'

export const ProfileService = {
    async getProfiles() {
        const response = await fetch(`${API_BASE}/profiles`)
        return response.json()
    },

    async createProfile(name) {
        const response = await fetch(`${API_BASE}/profiles`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        })
        return response.json()
    },

    async deleteProfile(name) {
        const response = await fetch(`${API_BASE}/profiles/${encodeURIComponent(name)}`, {
            method: 'DELETE'
        })
        return response.json()
    },

    async renameProfile(oldName, newName) {
        const response = await fetch(`${API_BASE}/profiles/${encodeURIComponent(oldName)}/rename`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_name: newName })
        })
        return response.json()
    },

    async setActiveProfile(name) {
        const response = await fetch(`${API_BASE}/profiles/active`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ profile: name })
        })
        return response.json()
    }
}
