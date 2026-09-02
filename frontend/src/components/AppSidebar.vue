<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api/client'
import { Bot, MessageSquare, FileText, ExternalLink } from '@lucide/vue'

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
</script>

<template>
  <aside class="w-56 shrink-0 flex flex-col bg-card border-r border-border h-full">
    <!-- Brand -->
    <div class="px-4 py-5 border-b border-border">
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-lg bg-primary/15 flex items-center justify-center shrink-0">
          <Bot class="w-4 h-4 text-primary" />
        </div>
        <span class="font-semibold text-sm truncate">{{ agentInfo.label }}</span>
      </div>
    </div>

    <!-- Nav -->
    <nav class="flex-1 px-2 py-3 space-y-0.5">
      <router-link
        to="/"
        class="nav-link"
        :class="{ 'nav-link--active': route.path === '/' }"
      >
        <MessageSquare class="w-4 h-4 shrink-0" />
        Chat
      </router-link>
      <router-link
        to="/documents"
        class="nav-link"
        :class="{ 'nav-link--active': route.path === '/documents' }"
      >
        <FileText class="w-4 h-4 shrink-0" />
        Documents
      </router-link>
    </nav>

    <!-- Footer -->
    <div class="px-2 py-3 border-t border-border">
      <a
        href="https://github.com/giunio-prc/rag-powered-chatbot"
        target="_blank"
        rel="noopener"
        class="nav-link"
      >
        <ExternalLink class="w-4 h-4 shrink-0" />
        GitHub
      </a>
    </div>
  </aside>
</template>

<style scoped>
.nav-link {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: hsl(var(--muted-foreground));
  text-decoration: none;
  transition: background-color 0.15s, color 0.15s;
}

.nav-link:hover {
  background-color: hsl(var(--secondary));
  color: hsl(var(--foreground));
}

.nav-link--active {
  background-color: hsl(var(--primary) / 0.12);
  color: hsl(var(--primary));
  font-weight: 500;
}

.nav-link--active:hover {
  background-color: hsl(var(--primary) / 0.18);
  color: hsl(var(--primary));
}
</style>
