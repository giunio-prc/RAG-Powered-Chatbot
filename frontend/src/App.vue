<script setup lang="ts">
import AppSidebar from '@/components/AppSidebar.vue'
import { useColorMode } from '@/composables/useColorMode'
import { useRoute } from 'vue-router'
import { MessageSquare, FileText, Sun, Moon } from '@lucide/vue'

const { isDark, toggle } = useColorMode()
const route = useRoute()
</script>

<template>
  <div class="flex flex-col md:flex-row h-screen bg-background text-foreground overflow-hidden">
    <!-- Ambient background layer -->
    <div class="fixed inset-0 -z-10 overflow-hidden pointer-events-none" aria-hidden="true">
      <div
        class="absolute -top-32 -right-16 w-[650px] h-[650px] rounded-full bg-primary/[0.22] blur-[90px]"
      />
      <div
        class="absolute -bottom-32 -left-16 w-[550px] h-[550px] rounded-full bg-violet-500/[0.18] blur-[80px]"
      />
      <div
        class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[300px] rounded-full bg-indigo-400/[0.06] blur-[80px]"
      />
      <div class="noise absolute inset-0" />
    </div>

    <!-- Desktop sidebar -->
    <AppSidebar class="hidden md:flex" />

    <!-- Mobile header -->
    <header
      class="md:hidden shrink-0 flex items-center justify-between px-4 bg-card/80 backdrop-blur-xl border-b border-border"
      style="padding-top: max(0.75rem, env(safe-area-inset-top)); padding-bottom: 0.75rem"
    >
      <div class="flex items-center gap-2">
        <svg height="28" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="avenueit-grad-mobile" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stop-color="#2d388a" />
              <stop offset="1" stop-color="#00aeef" />
            </linearGradient>
          </defs>
          <polygon points="2.83,0 29.17,9.123 2.83,18.247" fill="url(#avenueit-grad-mobile)" />
          <polygon points="2.83,22.877 29.17,13.753 29.17,32" fill="url(#avenueit-grad-mobile)" />
        </svg>
        <span class="font-semibold text-sm">RAG Chatbot</span>
      </div>
      <button
        class="p-2 rounded-lg text-muted-foreground hover:bg-secondary transition-colors"
        :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
        @click="toggle"
      >
        <Sun v-if="isDark" class="w-4 h-4" />
        <Moon v-else class="w-4 h-4" />
      </button>
    </header>

    <!-- Main content -->
    <main class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <RouterView />
    </main>

    <!-- Mobile bottom nav -->
    <nav
      class="md:hidden shrink-0 flex border-t border-border bg-card/80 backdrop-blur-xl"
      style="padding-bottom: env(safe-area-inset-bottom)"
    >
      <router-link
        to="/"
        class="mobile-nav-link"
        :class="{ 'mobile-nav-link--active': route.path === '/' }"
      >
        <MessageSquare class="w-5 h-5" />
        <span>Chat</span>
      </router-link>
      <router-link
        to="/documents"
        class="mobile-nav-link"
        :class="{ 'mobile-nav-link--active': route.path === '/documents' }"
      >
        <FileText class="w-5 h-5" />
        <span>Docs</span>
      </router-link>
    </nav>
  </div>
</template>

<style scoped>
.mobile-nav-link {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0.625rem 0;
  gap: 0.25rem;
  font-size: 0.7rem;
  color: hsl(var(--muted-foreground));
  text-decoration: none;
  transition: color 0.15s;
}

.mobile-nav-link:hover {
  color: hsl(var(--foreground));
}

.mobile-nav-link--active {
  color: hsl(var(--primary));
}
</style>
