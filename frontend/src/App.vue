<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <AppHeader />
    <main class="flex-grow w-full max-w-6xl mx-auto px-4 py-6">
      <RouterView />
    </main>
    <AppFooter />
  </div>
</template>
