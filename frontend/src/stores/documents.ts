import { defineStore } from 'pinia'

export interface Activity {
  message: string
  timestamp: string
}

const MAX_ACTIVITIES = 5

export const useDocumentsStore = defineStore('documents', {
  state: () => ({
    activities: [] as Activity[],
  }),
  actions: {
    addActivity(message: string) {
      this.activities.unshift({
        message,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      })
      if (this.activities.length > MAX_ACTIVITIES) this.activities.pop()
    },
  },
  persist: true,
})
