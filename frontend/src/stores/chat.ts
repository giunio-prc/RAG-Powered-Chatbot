import { defineStore } from 'pinia'

export interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

function now(): string {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [] as Message[],
  }),
  actions: {
    addMessage(msg: Message) {
      this.messages.push(msg)
    },
    updateLastAssistantMessage(content: string) {
      const last = this.messages.at(-1)
      if (last?.role === 'assistant') last.content = content
    },
    pushAssistantPlaceholder(): string {
      const timestamp = now()
      this.messages.push({ role: 'assistant', content: '', timestamp })
      return timestamp
    },
    addUserMessage(content: string): Message {
      const msg: Message = { role: 'user', content, timestamp: now() }
      this.messages.push(msg)
      return msg
    },
    clearHistory() {
      this.messages = []
    },
  },
  persist: true,
})
