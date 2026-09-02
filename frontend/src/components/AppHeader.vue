<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api/client'

interface AgentInfo {
  icon: string
  label: string
}

const route = useRoute()
const agentInfo = ref<AgentInfo>({ icon: 'smart_toy', label: 'RAG Chatbot' })

onMounted(async () => {
  try {
    const res = await api.get('/agent-info')
    if (res.ok) agentInfo.value = await res.json()
  } catch {
    // keep defaults
  }
})

const iconMap: Record<string, string> = {
  smart_toy: '🤖',
  pets: '🦜',
}

function agentEmoji(icon: string) {
  return iconMap[icon] ?? '🤖'
}
</script>

<template>
  <header class="bg-blue-600 text-white">
    <div class="w-full max-w-6xl mx-auto flex items-center justify-between px-4 py-3">
      <div class="flex items-center gap-2">
        <span class="text-2xl">{{ agentEmoji(agentInfo.icon) }}</span>
        <span class="text-xl font-semibold">{{ agentInfo.label }}</span>
      </div>
      <nav class="flex gap-1">
        <router-link
          to="/"
          class="px-4 py-2 rounded-lg font-medium transition-colors hover:bg-blue-500"
          :class="{ 'bg-blue-700': route.path === '/' }"
        >
          Chat
        </router-link>
        <router-link
          to="/documents"
          class="px-4 py-2 rounded-lg font-medium transition-colors hover:bg-blue-500"
          :class="{ 'bg-blue-700': route.path === '/documents' }"
        >
          Documents
        </router-link>
      </nav>
    </div>
  </header>
</template>

<style scoped>
a {
  color: #ffffff;
  text-decoration: none;
}
</style>
