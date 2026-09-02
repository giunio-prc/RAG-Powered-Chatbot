<script setup lang="ts">
import AppSidebar from '@/components/AppSidebar.vue'
</script>

<template>
  <div class="flex h-screen bg-background text-foreground overflow-hidden">
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

    <AppSidebar />
    <main class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <RouterView />
    </main>
  </div>
</template>
