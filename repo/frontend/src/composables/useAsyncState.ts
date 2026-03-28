import { ref } from 'vue'

export function useAsyncState() {
  const loading = ref(false)
  const error = ref('')

  async function run<T>(work: () => Promise<T>): Promise<T> {
    loading.value = true
    error.value = ''
    try {
      return await work()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Request failed.'
      throw err
    } finally {
      loading.value = false
    }
  }

  return { loading, error, run }
}
