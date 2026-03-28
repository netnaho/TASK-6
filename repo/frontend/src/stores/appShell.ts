import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

export const useAppShellStore = defineStore('app-shell', () => {
  const mobileDrawerOpen = ref(false)
  const globalLoading = ref(false)

  const drawerMode = computed(() => (mobileDrawerOpen.value ? 'open' : 'closed'))

  function toggleDrawer() {
    mobileDrawerOpen.value = !mobileDrawerOpen.value
  }

  function closeDrawer() {
    mobileDrawerOpen.value = false
  }

  return { mobileDrawerOpen, globalLoading, drawerMode, toggleDrawer, closeDrawer }
})
