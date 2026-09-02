<script setup lang="ts">
import { ref } from 'vue'
import { useDocuments } from '@/composables/useDocuments'

const {
  vectorsData,
  agentInfo,
  uploadProgress,
  isUploading,
  uploadStatus,
  isEmptyingDb,
  activities,
  uploadFile,
  emptyDatabase,
  refreshStats,
} = useDocuments()

const showConfirmModal = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

function onFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) {
    uploadFile(file)
    if (fileInput.value) fileInput.value.value = ''
  }
}

function onDrop(e: DragEvent) {
  e.preventDefault()
  const file = e.dataTransfer?.files[0]
  if (file) uploadFile(file)
}

async function confirmEmptyDatabase() {
  showConfirmModal.value = false
  await emptyDatabase()
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <h1 class="text-2xl font-bold text-gray-800">Document Management</h1>

    <div class="flex gap-6 flex-wrap lg:flex-nowrap">
      <!-- Left column: Upload -->
      <div class="flex-1 min-w-80">
        <div class="bg-white rounded-xl shadow border border-gray-200 p-4">
          <h2 class="text-lg font-semibold mb-4">Upload Documents</h2>

          <!-- Status / progress -->
          <p v-if="uploadStatus" class="text-sm text-gray-600 mb-2">{{ uploadStatus }}</p>
          <div v-if="isUploading" class="w-full bg-gray-200 rounded-full h-2 mb-3">
            <div
              class="bg-blue-500 h-2 rounded-full transition-all"
              :style="{ width: uploadProgress + '%' }"
            />
          </div>

          <!-- Drop zone -->
          <div
            class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-blue-400 transition-colors"
            :class="{ 'opacity-50 pointer-events-none': isUploading }"
            @click="fileInput?.click()"
            @dragover.prevent
            @drop="onDrop"
          >
            <p class="text-gray-500 text-sm">Drop files here or click to browse</p>
            <p class="text-gray-400 text-xs mt-1">.txt only · max 100 KB</p>
          </div>
          <input
            ref="fileInput"
            type="file"
            accept=".txt,text/plain"
            class="hidden"
            @change="onFileChange"
          />

          <!-- Requirements info -->
          <div class="mt-4 bg-gray-50 rounded-lg p-3">
            <p class="font-medium text-sm mb-1">File Requirements</p>
            <ul class="text-xs text-gray-600 space-y-1">
              <li>- Text files only (.txt)</li>
              <li>- Maximum file size: 100 KB (~500 lines)</li>
              <li>- UTF-8 encoding required</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Right column: Stats + Activity + Actions + Health -->
      <div class="flex-1 min-w-80 flex flex-col gap-4">

        <!-- Stats -->
        <div class="bg-white rounded-xl shadow border border-gray-200 p-4">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold">Database Statistics</h2>
            <button
              class="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-700 text-sm transition-colors"
              @click="refreshStats(true)"
            >
              🔄
            </button>
          </div>
          <div class="flex flex-col gap-3">
            <div class="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <div>
                <p class="text-sm text-gray-600">Total Vectors</p>
                <p class="text-2xl font-bold text-blue-600">{{ vectorsData.number_of_vectors }}</p>
              </div>
              <span class="text-3xl">🗄️</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <div>
                <p class="text-sm text-gray-600">Longest Vector</p>
                <p class="text-2xl font-bold text-green-600">{{ vectorsData.longest_vector }}</p>
              </div>
              <span class="text-3xl">📏</span>
            </div>
          </div>
        </div>

        <!-- Activity Feed -->
        <div class="bg-white rounded-xl shadow border border-gray-200 p-4">
          <h2 class="text-lg font-semibold mb-4">Recent Activity</h2>
          <div v-if="activities.length === 0" class="text-sm text-gray-400">No activity yet.</div>
          <ul class="flex flex-col gap-2">
            <li
              v-for="(act, i) in activities"
              :key="i"
              class="flex justify-between text-sm"
            >
              <span class="text-gray-700">{{ act.message }}</span>
              <span class="text-gray-400 shrink-0 ml-2">{{ act.timestamp }}</span>
            </li>
          </ul>
        </div>

        <!-- Database Actions -->
        <div class="bg-white rounded-xl shadow border border-gray-200 p-4">
          <h2 class="text-lg font-semibold mb-4">Database Actions</h2>
          <button
            class="flex items-center gap-1 px-4 py-2 rounded-lg bg-red-500 text-white font-medium hover:bg-red-600 transition-colors disabled:opacity-50"
            :disabled="isEmptyingDb"
            @click="showConfirmModal = true"
          >
            🗑 Empty Database
          </button>
        </div>

        <!-- Health -->
        <div class="bg-white rounded-xl shadow border border-gray-200 p-4">
          <h2 class="text-lg font-semibold mb-4">Database Health</h2>
          <div class="flex flex-col gap-3 text-sm">
            <div class="flex items-center gap-2">
              <span class="text-green-500">✅</span>
              <span>Connection: Active</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-blue-500">🧠</span>
              <span>Embedding Model: {{ agentInfo.embedding_model }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirm modal -->
    <Teleport to="body">
      <div
        v-if="showConfirmModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
        @click.self="showConfirmModal = false"
      >
        <div class="bg-white rounded-xl shadow-xl p-6 max-w-sm w-full mx-4">
          <h3 class="text-lg font-semibold mb-2">Are you sure?</h3>
          <p class="text-gray-600 mb-4">This will permanently delete all your uploaded documents.</p>
          <div class="flex justify-end gap-2">
            <button
              class="px-4 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
              @click="showConfirmModal = false"
            >
              Cancel
            </button>
            <button
              class="px-4 py-2 rounded-lg bg-red-500 text-white hover:bg-red-600 transition-colors"
              @click="confirmEmptyDatabase"
            >
              Delete All
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
