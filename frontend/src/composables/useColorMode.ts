import { ref, watch } from 'vue'

function getInitialDark() {
  const saved = localStorage.getItem('color-mode')
  if (saved) return saved === 'dark'
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

const isDark = ref(getInitialDark())

function applyClass(dark: boolean) {
  document.documentElement.classList.toggle('dark', dark)
  localStorage.setItem('color-mode', dark ? 'dark' : 'light')
}

watch(isDark, applyClass, { immediate: true })

export function useColorMode() {
  return {
    isDark,
    toggle: () => {
      isDark.value = !isDark.value
    },
  }
}
