<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import MessageBubble from '@/components/MessageBubble.vue'
import { useChat } from '@/composables/useChat'
import { Send, Trash2, Loader2 } from '@lucide/vue'

const { messages, isLoading, sendMessage, clearHistory } = useChat()
const inputText = ref('')
const chatContainer = ref<HTMLElement | null>(null)
const textarea = ref<HTMLTextAreaElement | null>(null)

async function scrollToBottom() {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

watch(() => messages.value.length, scrollToBottom)
watch(() => messages.value.at(-1)?.content, scrollToBottom)

function autoResize() {
  const el = textarea.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}

async function onSend() {
  const question = inputText.value.trim()
  if (!question || isLoading.value) return
  inputText.value = ''
  await nextTick()
  autoResize()
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
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div class="shrink-0 flex items-center justify-between px-6 py-3 border-b border-border">
      <span class="text-sm font-medium text-foreground">Chat</span>
      <button
        class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
        @click="clearHistory"
      >
        <Trash2 class="w-4 h-4" />
        Clear chat
      </button>
    </div>

    <!-- Messages -->
    <div
      ref="chatContainer"
      class="flex-1 overflow-y-auto px-6 py-6 min-h-0"
    >
      <div class="max-w-3xl mx-auto flex flex-col gap-5">
        <template v-if="messages.length === 0">
          <div class="flex flex-col items-center justify-center h-64 gap-3 select-none">
            <div class="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center">
              <span class="text-3xl">✦</span>
            </div>
            <p class="text-muted-foreground text-sm">Ask anything — your documents are ready.</p>
          </div>
        </template>
        <TransitionGroup name="message" tag="div" class="flex flex-col gap-5">
          <MessageBubble v-for="(msg, i) in messages" :key="i" :message="msg" />
        </TransitionGroup>
      </div>
    </div>

    <!-- Input bar -->
    <div class="shrink-0 border-t border-border bg-background px-6 py-4">
      <div class="max-w-3xl mx-auto flex flex-col gap-2">
        <div class="flex gap-2 items-end">
          <div class="flex-1 relative">
            <textarea
              ref="textarea"
              v-model="inputText"
              placeholder="Message your AI assistant…"
              rows="1"
              class="w-full resize-none rounded-xl border border-border bg-card px-4 py-3 pr-12 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring transition-colors disabled:opacity-50"
              style="min-height: 48px; max-height: 160px;"
              :disabled="isLoading"
              @keydown="onKeydown"
              @input="autoResize"
            />
          </div>
          <button
            class="flex items-center justify-center w-10 h-10 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
            :disabled="isLoading || !inputText.trim()"
            @click="onSend"
          >
            <Loader2 v-if="isLoading" class="w-4 h-4 animate-spin" />
            <Send v-else class="w-4 h-4" />
          </button>
        </div>

        <p class="text-xs text-muted-foreground px-1">Enter to send · Shift+Enter for newline</p>
      </div>
    </div>
  </div>
</template>
