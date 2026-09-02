import { defineStore } from 'pinia'

export interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

function now(): string {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// sessionStorage is cleared when the tab closes, making it a reliable proxy for
// the lifetime of the SESSION cookie from the frontend's perspective.
function getOrCreateSessionStamp(): string {
  let stamp = sessionStorage.getItem('session_stamp')
  if (!stamp) {
    stamp = crypto.randomUUID()
    sessionStorage.setItem('session_stamp', stamp)
  }
  return stamp
}

interface PersistedChat {
  sessionStamp: string
  messages: Message[]
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
  persist: {
    serializer: {
      serialize(state) {
        const payload: PersistedChat = {
          sessionStamp: getOrCreateSessionStamp(),
          messages: (state as { messages: Message[] }).messages,
        }
        return JSON.stringify(payload)
      },
      deserialize(raw) {
        const parsed: PersistedChat = JSON.parse(raw)
        if (parsed.sessionStamp !== getOrCreateSessionStamp()) {
          return { messages: [] }
        }
        return { messages: parsed.messages }
      },
    },
  },
})
