<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import MessageBubble from '@/components/MessageBubble.vue'
import { useChat } from '@/composables/useChat'

const { messages, isLoading, sendMessage, clearHistory } = useChat()
const inputText = ref('')
const chatContainer = ref<HTMLElement | null>(null)

async function scrollToBottom() {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

watch(() => messages.length, scrollToBottom)
watch(
  () => messages.at(-1)?.content,
  scrollToBottom,
)

async function onSend() {
  const question = inputText.value.trim()
  if (!question || isLoading.value) return
  inputText.value = ''
  await sendMessage(question)
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    onSend()
  }
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <!-- Header row -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-800">Chat with AI Assistant</h1>
      <button
        class="flex items-center gap-1 px-3 py-2 rounded-lg bg-red-500 text-white text-sm font-medium hover:bg-red-600 transition-colors"
        @click="clearHistory"
      >
        🗑 Clear Chat
      </button>
    </div>

    <!-- Chat window -->
    <div class="w-full bg-white rounded-xl shadow-lg border border-gray-200">
      <div
        ref="chatContainer"
        class="chat-container p-4 overflow-y-auto flex flex-col gap-4"
        style="height: 500px"
      >
        <template v-if="messages.length === 0">
          <p class="text-gray-400 text-sm text-center mt-8">
            No messages yet. Say hello!
          </p>
        </template>
        <MessageBubble v-for="(msg, i) in messages" :key="i" :message="msg" />
      </div>
    </div>

    <!-- Input area -->
    <div class="flex gap-2">
      <textarea
        v-model="inputText"
        placeholder="Type your message here…"
        rows="1"
        class="flex-grow resize-none rounded-lg border border-gray-300 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        :disabled="isLoading"
        @keydown="onKeydown"
      />
      <button
        class="flex items-center gap-1 px-4 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
        :disabled="isLoading || !inputText.trim()"
        @click="onSend"
      >
        <span v-if="isLoading" class="animate-spin">⏳</span>
        <span v-else>➤</span>
        Send
      </button>
    </div>

    <!-- Info banner -->
    <div class="w-full bg-blue-50 border border-blue-200 rounded-xl px-4 py-3 flex items-start gap-2">
      <span class="text-blue-600 shrink-0">ℹ️</span>
      <p class="text-sm text-blue-800">
        This chatbot uses RAG (Retrieval-Augmented Generation) technology. Upload documents in the
        Documents section to provide context for more accurate answers.
      </p>
    </div>
  </div>
</template>
