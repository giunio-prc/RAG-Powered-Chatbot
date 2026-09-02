import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useToast } from 'vue-toastification'
import { api, parseErrorDetail } from '@/api/client'
import { useChatStore } from '@/stores/chat'

export function useChat() {
  const store = useChatStore()
  const { messages } = storeToRefs(store)
  const toast = useToast()
  const isLoading = ref(false)

  async function sendMessage(question: string) {
    if (!question.trim() || isLoading.value) return

    isLoading.value = true
    store.addUserMessage(question)
    store.pushAssistantPlaceholder()

    let fullResponse = ''
    try {
      // POST body is Annotated[str, Body()] — must be a JSON-encoded string
      const res = await api.post('/query-stream', question)
      if (!res.ok || !res.body) {
        const detail = await parseErrorDetail(res)
        throw new Error(detail)
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const raw = line.slice(6)
          try {
            fullResponse += JSON.parse(raw)
          } catch {
            fullResponse += raw
          }
          store.updateLastAssistantMessage(fullResponse)
        }
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err)
      store.updateLastAssistantMessage(`Error: ${msg}`)
      toast.error(msg)
    } finally {
      isLoading.value = false
    }
  }

  return { isLoading, sendMessage, messages, clearHistory: () => store.clearHistory() }
}
