<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { api } from '../api'
import { t } from '../i18n'

const props = defineProps<{
  article: { title: string; url: string; summary: string }
  source: string
}>()
const emit = defineEmits<{ close: [] }>()
const size = defineModel<number>('fontSize', { required: true })
const dialog = ref<HTMLDialogElement>()
const sheet = ref<HTMLElement>()
const lines = ref<string[]>([])
const status = ref<'loading' | 'ready' | 'failed'>('loading')
const page = ref(1)
const total = ref(1)
const controller = new AbortController()
let observer: ResizeObserver | undefined

function turn(to: number) {
  page.value = Math.min(total.value, Math.max(1, to))
  if (sheet.value) sheet.value.scrollLeft = (page.value - 1) * sheet.value.clientWidth
}
function paginate() {
  const el = sheet.value
  if (!el?.clientWidth) return
  total.value = Math.max(1, Math.round(el.scrollWidth / el.clientWidth))
  turn(page.value)
}
function keydown(event: KeyboardEvent) {
  if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
    event.preventDefault()
    turn(page.value + (event.key === 'ArrowRight' ? 1 : -1))
  }
}
watch([lines, status, size], paginate, { flush: 'post' })
onMounted(async () => {
  dialog.value?.showModal()
  observer = new ResizeObserver(paginate)
  if (sheet.value) observer.observe(sheet.value)
  try {
    const { paragraphs } = await api<{ paragraphs: string[] }>('/article', {
      method: 'POST',
      json: { url: props.article.url },
      signal: controller.signal,
    })
    lines.value = paragraphs
    status.value = 'ready'
  } catch {
    if (controller.signal.aborted) return
    lines.value = props.article.summary ? [props.article.summary] : []
    status.value = 'failed'
  }
})
onUnmounted(() => {
  controller.abort()
  observer?.disconnect()
})
</script>
<template>
  <dialog ref="dialog" aria-labelledby="reader-title" class="reader bg-base-200 text-base-content" @keydown="keydown" @close="emit('close')">
    <div class="mx-auto grid h-full max-w-3xl grid-rows-[auto_minmax(0,1fr)_auto]">
      <header class="flex items-center justify-between gap-3 py-3">
        <button autofocus class="btn btn-ghost btn-sm" @click="dialog?.close()">‹ {{ t('reader.back') }}</button>
        <div class="join">
          <button class="btn btn-sm join-item" :aria-label="t('reader.smaller')" :disabled="size <= 16" @click="size -= 2">A−</button>
          <button class="btn btn-sm join-item" :aria-label="t('reader.larger')" :disabled="size >= 32" @click="size += 2">A+</button>
        </div>
      </header>
      <div class="paper min-h-0 rounded-box border border-base-300 bg-base-100 shadow-sm">
        <article ref="sheet" class="sheet h-full" :style="{ fontSize: size + 'px' }">
          <p class="font-display text-sm font-semibold text-base-content/65">{{ source }}</p>
          <h1 id="reader-title" class="mb-6 mt-2 text-[1.65em] leading-tight font-bold">{{ article.title }}</h1>
          <p v-if="status !== 'ready'" role="status" class="mb-4 text-sm font-sans text-base-content/70">{{ status === 'loading' ? t('feed.busy') : lines.length ? t('reader.summaryOnly') : t('reader.noBody') }}</p>
          <p v-for="(line, index) in lines" :key="index" class="mb-[0.9em]">{{ line }}</p>
        </article>
      </div>
      <footer class="flex items-center justify-between gap-2 py-3">
        <button class="btn btn-sm" :disabled="page === 1" @click="turn(page - 1)">‹ {{ t('reader.previous') }}</button>
        <span aria-live="polite" class="text-sm tabular-nums">{{ page }} / {{ total }}</span>
        <button class="btn btn-sm" :disabled="page === total" @click="turn(page + 1)">{{ t('reader.next') }} ›</button>
      </footer>
    </div>
  </dialog>
</template>
<style scoped>
.reader[open] { position: fixed; inset: 0; width: 100%; max-width: none; height: 100%; max-height: none; margin: 0; padding-inline: clamp(.5rem, 3vw, 2rem); }
.paper { padding: clamp(1rem, 4vw, 3rem); }
.sheet { column-count: 1; column-gap: 0; column-fill: auto; overflow: hidden; overflow-wrap: anywhere; font-family: Georgia, 'AppleMyungjo', 'Batang', serif; line-height: 1.8; }
</style>
