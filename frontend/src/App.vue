<script setup lang="ts">
import AppSidebar from '@/components/AppSidebar.vue'
</script>

<template>
  <div class="flex h-screen bg-background text-foreground overflow-hidden">
    <AppSidebar />
    <main class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <RouterView />
    </main>
  </div>
</template>
