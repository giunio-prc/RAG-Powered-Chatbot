<script setup lang="ts">
import { Bot, User } from '@lucide/vue'
import type { Message } from '@/stores/chat'

defineProps<{ message: Message }>()
</script>

<template>
  <div
    class="flex gap-3"
    :class="message.role === 'user' ? 'flex-row-reverse' : 'flex-row'"
  >
    <!-- Avatar -->
    <div
      class="w-7 h-7 rounded-lg flex items-center justify-center shrink-0 mt-0.5"
      :class="message.role === 'user'
        ? 'bg-secondary text-muted-foreground'
        : 'bg-primary/15 text-primary'"
    >
      <User v-if="message.role === 'user'" class="w-3.5 h-3.5" />
      <Bot v-else class="w-3.5 h-3.5" />
    </div>

    <!-- Content -->
    <div
      class="flex flex-col gap-1 max-w-[85%]"
      :class="{ 'items-end': message.role === 'user' }"
    >
      <div
        class="px-4 py-2.5 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap"
        :class="message.role === 'user'
          ? 'bg-primary text-primary-foreground rounded-tr-sm'
          : 'bg-card text-card-foreground border border-border rounded-tl-sm'"
      >
        <span v-if="message.content">{{ message.content }}</span>
        <span v-else class="flex items-center gap-2 text-muted-foreground italic text-xs">
          <span class="flex gap-1">
            <span class="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce" style="animation-delay: 0ms" />
            <span class="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce" style="animation-delay: 150ms" />
            <span class="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce" style="animation-delay: 300ms" />
          </span>
          Thinking
        </span>
      </div>
      <span class="text-xs text-muted-foreground px-1">{{ message.timestamp }}</span>
    </div>
  </div>
</template>
