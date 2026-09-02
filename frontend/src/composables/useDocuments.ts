import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { api, parseErrorDetail } from '@/api/client'
import { useDocumentsStore } from '@/stores/documents'

export interface VectorsData {
  number_of_vectors: number
  longest_vector: number
}

export interface AgentInfo {
  is_fake: boolean
  icon: string
  label: string
  embedding_model: string
}

export function useDocuments() {
  const store = useDocumentsStore()
  const toast = useToast()

  const vectorsData = ref<VectorsData>({ number_of_vectors: 0, longest_vector: 0 })
  const agentInfo = ref<AgentInfo>({ is_fake: false, icon: 'smart_toy', label: 'RAG Chatbot', embedding_model: 'Cohere' })
  const uploadProgress = ref(0)
  const isUploading = ref(false)
  const uploadStatus = ref('')
  const isEmptyingDb = ref(false)

  async function refreshStats(showToast = false) {
    try {
      const res = await api.get('/get-vectors-data')
      if (!res.ok) throw new Error(await parseErrorDetail(res))
      vectorsData.value = await res.json()
      if (showToast) toast.info('Stats refreshed')
    } catch (err) {
      toast.error(`Failed to load stats: ${err instanceof Error ? err.message : err}`)
    }
  }

  async function fetchAgentInfo() {
    try {
      const res = await api.get('/agent-info')
      if (res.ok) agentInfo.value = await res.json()
    } catch {
      // keep defaults
    }
  }

  async function uploadFile(file: File) {
    if (file.size > 100 * 1024) {
      toast.warning('File too large. Maximum size is 100KB.')
      return
    }
    if (file.type !== 'text/plain' && !file.name.endsWith('.txt')) {
      toast.warning('Only .txt files are supported.')
      return
    }

    const formData = new FormData()
    formData.append('file', file)

    isUploading.value = true
    uploadProgress.value = 0
    uploadStatus.value = 'Uploading…'

    try {
      const res = await api.postForm('/add-document', formData)

      if (!res.ok || !res.body) {
        const detail = await parseErrorDetail(res)
        throw new Error(detail)
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let apiLimitHit = false

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''
        for (const line of lines) {
          const t = line.trim()
          if (!t) continue
          if (t === 'API_LIMIT_EXCEEDED') {
            apiLimitHit = true
            toast.warning('API limit reached. Document partially uploaded.')
          } else {
            uploadProgress.value = parseFloat(t)
          }
        }
      }

      if (!apiLimitHit) {
        uploadStatus.value = 'Upload complete!'
        toast.success(`"${file.name}" uploaded successfully.`)
        store.addActivity(`Uploaded "${file.name}"`)
        await refreshStats()
      } else {
        uploadStatus.value = 'Partial upload (API limit)'
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err)
      uploadStatus.value = `Error: ${msg}`
      toast.error(msg)
    } finally {
      isUploading.value = false
      setTimeout(() => {
        uploadProgress.value = 0
        uploadStatus.value = ''
      }, 3000)
    }
  }

  async function emptyDatabase() {
    isEmptyingDb.value = true
    try {
      const res = await api.delete('/empty-database')
      if (!res.ok) throw new Error(await parseErrorDetail(res))
      store.addActivity('Database emptied')
      toast.success('Database emptied successfully.')
      await refreshStats()
    } catch (err) {
      toast.error(`Failed to empty database: ${err instanceof Error ? err.message : err}`)
    } finally {
      isEmptyingDb.value = false
    }
  }

  onMounted(async () => {
    await Promise.all([refreshStats(), fetchAgentInfo()])
  })

  return {
    vectorsData,
    agentInfo,
    uploadProgress,
    isUploading,
    uploadStatus,
    isEmptyingDb,
    activities: store.activities,
    uploadFile,
    emptyDatabase,
    refreshStats,
  }
}
