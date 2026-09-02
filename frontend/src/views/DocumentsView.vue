<script setup lang="ts">
import { ref } from 'vue'
import { useDocuments } from '@/composables/useDocuments'
import {
  UploadCloud,
  RefreshCw,
  Trash2,
  Database,
  Ruler,
  CheckCircle2,
  Brain,
  Activity,
  X,
  FileText,
} from '@lucide/vue'

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
const isDragging = ref(false)

function onFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) {
    uploadFile(file)
    if (fileInput.value) fileInput.value.value = ''
  }
}

function onDrop(e: DragEvent) {
  e.preventDefault()
  isDragging.value = false
  const file = e.dataTransfer?.files[0]
  if (file) uploadFile(file)
}

async function confirmEmptyDatabase() {
  showConfirmModal.value = false
  await emptyDatabase()
}
</script>

<template>
  <div class="flex-1 overflow-y-auto px-3 sm:px-6 py-4 sm:py-6">
    <div class="max-w-5xl mx-auto">
      <h1 class="text-xl font-semibold text-foreground mb-4 sm:mb-6">Documents</h1>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- Upload card -->
        <div class="bg-card border border-border rounded-xl p-5 flex flex-col gap-4">
          <h2 class="text-sm font-medium text-foreground">Upload</h2>

          <!-- Progress -->
          <div v-if="isUploading || uploadStatus" class="flex flex-col gap-1.5">
            <p class="text-xs text-muted-foreground">{{ uploadStatus }}</p>
            <div v-if="isUploading" class="w-full bg-secondary rounded-full h-1.5">
              <div
                class="bg-primary h-1.5 rounded-full transition-all duration-300"
                :style="{ width: uploadProgress + '%' }"
              />
            </div>
          </div>

          <!-- Drop zone -->
          <button
            type="button"
            class="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 flex flex-col items-center gap-3 w-full"
            :class="[
              isDragging
                ? 'border-primary bg-primary/5'
                : 'border-border hover:border-primary/50 hover:bg-secondary/40',
              isUploading ? 'opacity-50 pointer-events-none' : '',
            ]"
            :disabled="isUploading"
            @click="fileInput?.click()"
            @dragover.prevent="isDragging = true"
            @dragleave="isDragging = false"
            @drop="onDrop"
          >
            <div class="w-10 h-10 rounded-xl bg-secondary flex items-center justify-center">
              <UploadCloud class="w-5 h-5 text-muted-foreground" />
            </div>
            <div>
              <p class="text-sm text-foreground font-medium">Drop a file or click to browse</p>
              <p class="text-xs text-muted-foreground mt-1">.txt · max 100 KB · UTF-8</p>
            </div>
          </button>
          <input
            ref="fileInput"
            type="file"
            accept=".txt,text/plain"
            class="hidden"
            @change="onFileChange"
          />

          <!-- Requirements -->
          <div class="bg-secondary/50 rounded-lg px-4 py-3 flex flex-col gap-1">
            <div class="flex items-center gap-2 text-xs text-muted-foreground">
              <FileText class="w-3 h-3 shrink-0" />
              Text files only (.txt)
            </div>
            <div class="flex items-center gap-2 text-xs text-muted-foreground">
              <Ruler class="w-3 h-3 shrink-0" />
              Maximum 100 KB (~500 lines)
            </div>
          </div>
        </div>

        <!-- Right column -->
        <div class="flex flex-col gap-4">
          <!-- Stats -->
          <div class="bg-card border border-border rounded-xl p-5">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-sm font-medium text-foreground">Statistics</h2>
              <button
                class="p-1.5 rounded-lg text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
                @click="refreshStats(true)"
              >
                <RefreshCw class="w-3.5 h-3.5" />
              </button>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div class="bg-secondary/50 rounded-lg p-3">
                <div class="flex items-center gap-2 mb-1">
                  <Database class="w-3.5 h-3.5 text-primary" />
                  <span class="text-xs text-muted-foreground">Vectors</span>
                </div>
                <p class="text-2xl font-bold text-foreground">
                  {{ vectorsData.number_of_vectors }}
                </p>
              </div>
              <div class="bg-secondary/50 rounded-lg p-3">
                <div class="flex items-center gap-2 mb-1">
                  <Ruler class="w-3.5 h-3.5 text-primary" />
                  <span class="text-xs text-muted-foreground">Longest</span>
                </div>
                <p class="text-2xl font-bold text-foreground">{{ vectorsData.longest_vector }}</p>
              </div>
            </div>
          </div>

          <!-- Activity -->
          <div class="bg-card border border-border rounded-xl p-5">
            <div class="flex items-center gap-2 mb-4">
              <Activity class="w-3.5 h-3.5 text-muted-foreground" />
              <h2 class="text-sm font-medium text-foreground">Recent Activity</h2>
            </div>
            <div v-if="activities.length === 0" class="text-xs text-muted-foreground">
              No activity yet.
            </div>
            <ul class="flex flex-col gap-2">
              <li
                v-for="(act, i) in activities"
                :key="i"
                class="flex justify-between items-baseline gap-2"
              >
                <span class="text-sm text-foreground truncate">{{ act.message }}</span>
                <span class="text-xs text-muted-foreground shrink-0">{{ act.timestamp }}</span>
              </li>
            </ul>
          </div>

          <!-- Health + Actions row -->
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-card border border-border rounded-xl p-5">
              <h2 class="text-sm font-medium text-foreground mb-3">Health</h2>
              <div class="flex flex-col gap-2 text-xs">
                <div class="flex items-center gap-2">
                  <CheckCircle2 class="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                  <span class="text-muted-foreground">Connected</span>
                </div>
                <div class="flex items-center gap-2">
                  <Brain class="w-3.5 h-3.5 text-primary shrink-0" />
                  <span class="text-muted-foreground truncate">{{
                    agentInfo.embedding_model
                  }}</span>
                </div>
              </div>
            </div>

            <div class="bg-card border border-border rounded-xl p-5">
              <h2 class="text-sm font-medium text-foreground mb-3">Actions</h2>
              <button
                class="flex items-center gap-2 text-xs px-3 py-2 rounded-lg border border-destructive/40 text-destructive hover:bg-destructive/10 transition-colors disabled:opacity-50"
                :disabled="isEmptyingDb"
                @click="showConfirmModal = true"
              >
                <Trash2 class="w-3.5 h-3.5" />
                Empty database
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Confirm modal -->
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="showConfirmModal"
        class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50"
        @click.self="showConfirmModal = false"
      >
        <div class="bg-card border border-border rounded-2xl shadow-2xl p-6 max-w-sm w-full mx-4">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-base font-semibold text-foreground">Empty database?</h3>
            <button
              class="p-1 rounded-lg text-muted-foreground hover:bg-secondary transition-colors"
              @click="showConfirmModal = false"
            >
              <X class="w-4 h-4" />
            </button>
          </div>
          <p class="text-sm text-muted-foreground mb-6">
            This will permanently delete all uploaded documents and their embeddings. This action
            cannot be undone.
          </p>
          <div class="flex justify-end gap-2">
            <button
              class="px-4 py-2 rounded-lg text-sm text-muted-foreground hover:bg-secondary transition-colors"
              @click="showConfirmModal = false"
            >
              Cancel
            </button>
            <button
              class="px-4 py-2 rounded-lg text-sm bg-destructive text-destructive-foreground hover:bg-destructive/90 transition-colors"
              @click="confirmEmptyDatabase"
            >
              Delete all
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.15s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-active > div,
.modal-leave-active > div {
  transition:
    transform 0.15s ease,
    opacity 0.15s ease;
}
.modal-enter-from > div,
.modal-leave-to > div {
  transform: scale(0.96);
  opacity: 0;
}
</style>
