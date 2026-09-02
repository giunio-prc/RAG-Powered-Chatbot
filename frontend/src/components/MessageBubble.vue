<script setup lang="ts">
import type { Message } from '@/stores/chat'

defineProps<{ message: Message }>()
</script>

<template>
  <div class="w-full flex" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
    <div
      class="flex items-end gap-2 max-w-3xl"
      :class="{ 'flex-row-reverse': message.role === 'user' }"
    >
      <!-- Avatar -->
      <div
        class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm"
        :class="
          message.role === 'user'
            ? 'bg-blue-100 text-blue-600'
            : 'bg-green-100 text-green-600'
        "
      >
        {{ message.role === 'user' ? '👤' : '🤖' }}
      </div>

      <!-- Bubble -->
      <div class="flex flex-col gap-1" :class="{ 'items-end': message.role === 'user' }">
        <div
          class="px-4 py-2 rounded-2xl whitespace-pre-wrap"
          :class="
            message.role === 'user'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-800'
          "
        >
          <span v-if="message.content">{{ message.content }}</span>
          <span v-else class="italic text-gray-400 text-sm">Thinking…</span>
        </div>
        <span class="text-xs text-gray-400 px-2">{{ message.timestamp }}</span>
      </div>
    </div>
  </div>
</template>
