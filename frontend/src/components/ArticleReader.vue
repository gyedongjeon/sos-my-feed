<script setup lang="ts">
// Reads one article like a book, after the Re:Leaf reader: pages instead of scrolling, turned
// by a tap on either side or the arrow keys, on paper of a chosen colour, one or two at a time.
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { api } from '../api'
import { t } from '../i18n'
import { articleMarkdown, markdownFileName } from '../markdown'
import { isTap, PAGE_GAP, pageCount, type Press, READER_THEMES, SPREAD_MIN_WIDTH, tapZone } from '../reader'
import { useSettingsStore } from '../stores/settings'
import type { Block, ReaderSettings, ReaderTheme } from '../types'
import ReaderIcon from './ReaderIcon.vue'
import ReaderTutorial from './ReaderTutorial.vue'

const props = defineProps<{
  article: { title: string; url: string; summary: string }
  source: string
}>()
const emit = defineEmits<{ close: [] }>()

const settings = useSettingsStore()
const dialog = ref<HTMLDialogElement>()
// What is seen of the pages, and all of them laid out side by side behind it.
const view = ref<HTMLElement>()
const sheet = ref<HTMLElement>()
const blocks = ref<Block[]>([])
const status = ref<'loading' | 'ready' | 'failed'>('loading')
const page = ref(1)
const total = ref(1)
const width = ref(0)
const menuShown = ref(true)
const settingsShown = ref(false)
const controller = new AbortController()
let observer: ResizeObserver | undefined
let hideMenu: ReturnType<typeof setTimeout> | undefined
let pressed: Press | undefined

const THEMES = Object.keys(READER_THEMES) as ReaderTheme[]
// The menu is in sight for this long when an article opens, so that it is known to be there.
const MENU_GLIMPSE_MS = 3000

const colours = computed(() => READER_THEMES[settings.reader.theme])
// Two pages side by side need room; a narrow window shows one whatever was chosen.
const spread = computed(() => settings.reader.pages === 2 && width.value >= SPREAD_MIN_WIDTH)

function turn(to: number) {
  page.value = Math.min(total.value, Math.max(1, to))
}

function paginate() {
  if (!view.value?.clientWidth || !sheet.value) return
  width.value = view.value.clientWidth
  total.value = pageCount(sheet.value.scrollWidth, width.value)
  turn(page.value)
}

function toggleMenu() {
  clearTimeout(hideMenu)
  menuShown.value = !menuShown.value
  if (!menuShown.value) settingsShown.value = false
}

function toggleSettings() {
  clearTimeout(hideMenu)
  settingsShown.value = !settingsShown.value
}

function keydown(event: KeyboardEvent) {
  // A slider and a button take the keys that are theirs.
  if ((event.target as HTMLElement).closest('input, button')) return
  const forward = ['ArrowRight', 'PageDown', ' '].includes(event.key)
  if (!forward && !['ArrowLeft', 'PageUp'].includes(event.key)) return
  event.preventDefault()
  turn(page.value + (forward ? 1 : -1))
}

// Escape closes the settings first, and the reader only after.
function cancel(event: Event) {
  if (!settingsShown.value) return
  event.preventDefault()
  settingsShown.value = false
}

const onControls = (event: Event) => !!(event.target as HTMLElement).closest('[data-reader-ui]')

function pointerdown(event: PointerEvent) {
  pressed = event.button === 0 && !onControls(event) ? { x: event.clientX, y: event.clientY, time: event.timeStamp } : undefined
}

function pointerup(event: PointerEvent) {
  const down = pressed
  pressed = undefined
  if (!down || onControls(event) || !isTap(down, { x: event.clientX, y: event.clientY, time: event.timeStamp })) return
  // A tap beside the open settings puts them away, as a tap beside any menu does.
  if (settingsShown.value) return void (settingsShown.value = false)
  const zone = tapZone(event.clientX, window.innerWidth)
  if (zone === 'menu') toggleMenu()
  else turn(page.value + (zone === 'next' ? 1 : -1))
}

const sliderValue = (event: Event) => Number((event.target as HTMLInputElement).value)
// While a slider is dragged the page follows; the choice is saved when it is let go.
const preview = (changed: Partial<ReaderSettings>) => settings.previewReader(changed)
const choose = (changed: Partial<ReaderSettings>) => settings.setReader(changed)

function download() {
  const date = new Date().toISOString().split('T')[0]
  const file = new Blob([articleMarkdown(props.article, blocks.value, date)], { type: 'text/markdown' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(file)
  link.download = markdownFileName(props.article.title, date)
  link.click()
  URL.revokeObjectURL(link.href)
}

function tutorialDone(seen: boolean) {
  if (seen) void choose({ tutorialSeen: true })
  else tutorialDismissed.value = true
}
// Closed without "don't show again": gone for this article, back for the next.
const tutorialDismissed = ref(false)

watch(
  [blocks, status, spread, () => [settings.reader.size, settings.reader.lineHeight, settings.reader.marginV, settings.reader.marginH]],
  paginate,
  { flush: 'post', deep: true },
)

onMounted(async () => {
  dialog.value?.showModal()
  observer = new ResizeObserver(paginate)
  if (view.value) observer.observe(view.value)
  hideMenu = setTimeout(() => (menuShown.value = false), MENU_GLIMPSE_MS)
  try {
    const text = await api<{ blocks: Block[] }>('/article', {
      method: 'POST',
      json: { url: props.article.url },
      signal: controller.signal,
    })
    blocks.value = text.blocks
    status.value = 'ready'
  } catch {
    if (controller.signal.aborted) return
    blocks.value = props.article.summary ? [{ kind: 'paragraph', text: props.article.summary }] : []
    status.value = 'failed'
  }
})

onUnmounted(() => {
  controller.abort()
  observer?.disconnect()
  clearTimeout(hideMenu)
})
</script>

<template>
  <dialog
    ref="dialog"
    aria-labelledby="reader-title"
    class="reader"
    :style="{
      '--paper': colours.paper,
      '--ink': colours.ink,
      '--rule': colours.rule,
      '--heading': colours.heading ?? colours.ink,
      padding: `${settings.reader.marginV}px ${settings.reader.marginH}px`,
    }"
    @keydown="keydown"
    @cancel="cancel"
    @close="emit('close')"
    @pointerdown="pointerdown"
    @pointerup="pointerup"
  >
    <div ref="view" class="view">
      <!-- Focused when the reader opens, so that the keys turn pages and the menu can hide. -->
      <article
        ref="sheet"
        autofocus
        tabindex="-1"
        class="sheet"
        :class="{ spread }"
        :style="{
          fontSize: `${settings.reader.size}px`,
          lineHeight: settings.reader.lineHeight,
          columnGap: `${PAGE_GAP}px`,
          transform: `translateX(${-(page - 1) * (width + PAGE_GAP)}px)`,
        }"
      >
        <p class="source">{{ source }}</p>
        <h1 id="reader-title">{{ article.title }}</h1>
        <p v-if="status !== 'ready'" role="status" class="note">
          {{ status === 'loading' ? t('feed.busy') : blocks.length ? t('reader.summaryOnly') : t('reader.noBody') }}
        </p>
        <template v-for="(block, index) in blocks" :key="index">
          <h2 v-if="block.kind === 'heading'">{{ block.text }}</h2>
          <blockquote v-else-if="block.kind === 'quote'">{{ block.text }}</blockquote>
          <p v-else>{{ block.text }}</p>
        </template>
      </article>
    </div>

    <!-- The view settings, above the menu. -->
    <section v-if="settingsShown" data-reader-ui class="settings bg-base-100 text-base-content" :aria-label="t('reader.settings')">
      <header class="mb-4 flex items-center justify-between border-b border-base-300 pb-3">
        <h2 class="font-semibold">{{ t('reader.settings') }}</h2>
        <button class="btn btn-ghost btn-circle btn-xs" :aria-label="t('reader.closeSettings')" @click="settingsShown = false">
          <ReaderIcon name="x" />
        </button>
      </header>
      <div class="mb-5 flex justify-center gap-2.5" role="group" :aria-label="t('reader.paper')">
        <button
          v-for="theme in THEMES"
          :key="theme"
          class="swatch"
          :class="{ active: settings.reader.theme === theme }"
          :style="{ background: READER_THEMES[theme].paper }"
          :aria-label="t(`reader.theme.${theme}`)"
          :aria-pressed="settings.reader.theme === theme"
          :title="t(`reader.theme.${theme}`)"
          @click="choose({ theme })"
        ></button>
      </div>
      <label class="row">
        <span class="label-text"><ReaderIcon name="text" /> {{ t('reader.textSize') }}</span>
        <input
          type="range" class="range range-xs w-36" min="14" max="32" :value="settings.reader.size"
          @input="preview({ size: sliderValue($event) })" @change="choose({ size: sliderValue($event) })"
        />
      </label>
      <label class="row">
        <span class="label-text"><ReaderIcon name="spacing" /> {{ t('reader.lineSpacing') }}</span>
        <input
          type="range" class="range range-xs w-36" min="12" max="24" :value="Math.round(settings.reader.lineHeight * 10)"
          @input="preview({ lineHeight: sliderValue($event) / 10 })" @change="choose({ lineHeight: sliderValue($event) / 10 })"
        />
      </label>
      <label class="row">
        <span class="label-text"><ReaderIcon name="margin-v" /> {{ t('reader.marginV') }}</span>
        <input
          type="range" class="range range-xs w-36" min="40" max="120" :value="settings.reader.marginV"
          @input="preview({ marginV: sliderValue($event) })" @change="choose({ marginV: sliderValue($event) })"
        />
      </label>
      <label class="row">
        <span class="label-text"><ReaderIcon name="margin-h" /> {{ t('reader.marginH') }}</span>
        <input
          type="range" class="range range-xs w-36" min="20" max="80" :value="settings.reader.marginH"
          @input="preview({ marginH: sliderValue($event) })" @change="choose({ marginH: sliderValue($event) })"
        />
      </label>
      <div class="row">
        <span class="label-text"><ReaderIcon name="view" /> {{ t('reader.pageView') }}</span>
        <div class="join" role="group" :aria-label="t('reader.pageView')">
          <button
            v-for="count in [1, 2]"
            :key="count"
            class="btn btn-sm btn-square join-item"
            :class="settings.reader.pages === count ? 'btn-neutral' : ''"
            :aria-label="count === 1 ? t('reader.onePage') : t('reader.twoPages')"
            :aria-pressed="settings.reader.pages === count"
            :title="count === 1 ? t('reader.onePage') : t('reader.twoPages')"
            @click="choose({ pages: count })"
          >
            <ReaderIcon :name="count === 1 ? 'page-1' : 'page-2'" />
          </button>
        </div>
      </div>
    </section>

    <!-- The menu: out of sight while reading, back with a tap on the middle of the page. -->
    <nav data-reader-ui class="menu-bar bg-base-100/90 text-base-content" :class="{ shown: menuShown || settingsShown }">
      <button class="btn btn-ghost btn-circle btn-sm" :aria-label="t('reader.settings')" :aria-expanded="settingsShown" :title="t('reader.settings')" @click="toggleSettings">
        <ReaderIcon name="settings" />
      </button>
      <button class="btn btn-ghost btn-circle btn-sm" :aria-label="t('reader.previous')" :disabled="page === 1" @click="turn(page - 1)">
        <ReaderIcon name="previous" />
      </button>
      <span aria-live="polite" class="counter bg-base-content/5">{{ page }} / {{ total }}</span>
      <button class="btn btn-ghost btn-circle btn-sm" :aria-label="t('reader.next')" :disabled="page === total" @click="turn(page + 1)">
        <ReaderIcon name="next" />
      </button>
      <button class="btn btn-ghost btn-circle btn-sm" :aria-label="t('reader.download')" :title="t('reader.download')" :disabled="!blocks.length" @click="download">
        <ReaderIcon name="download" />
      </button>
      <button class="btn btn-ghost btn-circle btn-sm hover:text-error" :aria-label="t('reader.close')" :title="t('reader.close')" @click="dialog?.close()">
        <ReaderIcon name="close" />
      </button>
    </nav>

    <ReaderTutorial v-if="!settings.reader.tutorialSeen && !tutorialDismissed" @done="tutorialDone" />
  </dialog>
</template>

<style scoped>
.reader[open] {
  position: fixed;
  inset: 0;
  width: 100%;
  max-width: none;
  height: 100%;
  max-height: none;
  margin: 0;
  overflow: hidden;
  background: var(--paper);
  color: var(--ink);
  transition: background-color 0.3s, color 0.3s;
}
.view {
  height: 100%;
  overflow: hidden;
}
.sheet {
  height: 100%;
  column-count: 1;
  column-fill: auto;
  overflow-wrap: anywhere;
  font-family: Georgia, 'AppleMyungjo', 'Batang', serif;
  outline: none;
  transition: transform 0.3s ease;
}
.sheet.spread {
  column-count: 2;
}
@media (prefers-reduced-motion: reduce) {
  .sheet {
    transition: none;
  }
}
.source {
  font-family: var(--font-display, system-ui, sans-serif);
  font-size: 0.7em;
  font-weight: 600;
  opacity: 0.65;
}
h1,
.sheet h2 {
  color: var(--heading);
  font-family: 'Helvetica Neue', Arial, 'Apple SD Gothic Neo', sans-serif;
  font-weight: 700;
  line-height: 1.3;
  break-inside: avoid;
  break-after: avoid;
}
h1 {
  margin: 0.3em 0 1em;
  font-size: 1.65em;
}
.sheet h2 {
  margin: 1em 0 0.5em;
  font-size: 1.25em;
}
.sheet p {
  margin-bottom: 1.5em;
  text-align: justify;
}
.sheet .source {
  margin-bottom: 0;
}
.note {
  font-family: var(--font-sans, system-ui, sans-serif);
  font-size: 0.7em;
  opacity: 0.7;
}
blockquote {
  margin: 0 0 1.5em;
  padding-left: 1em;
  border-left: 4px solid var(--rule);
  font-style: italic;
  opacity: 0.85;
  break-inside: avoid;
}

.menu-bar {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 15;
  display: flex;
  height: 4rem;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  border-top: 1px solid rgb(0 0 0 / 0.1);
  font-family: var(--font-sans, system-ui, sans-serif);
  opacity: 0;
  pointer-events: none;
  transform: translateY(100%);
  transition: opacity 0.3s ease, transform 0.3s ease;
  backdrop-filter: blur(12px);
}
/* Reached with the Tab key, the menu comes into sight like after a tap. */
.menu-bar.shown,
.menu-bar:focus-within {
  opacity: 1;
  pointer-events: auto;
  transform: none;
}
.counter {
  min-width: 4.5rem;
  padding: 0.375rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
  text-align: center;
}

.settings {
  position: absolute;
  bottom: 5rem;
  left: 50%;
  z-index: 25;
  width: min(23rem, calc(100% - 2rem));
  max-height: calc(100% - 6rem);
  overflow-y: auto;
  padding: 1.25rem;
  border: 1px solid rgb(0 0 0 / 0.1);
  border-radius: 1rem;
  box-shadow: 0 8px 32px rgb(0 0 0 / 0.15);
  font-family: var(--font-sans, system-ui, sans-serif);
  transform: translateX(-50%);
}
.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.row:last-child {
  margin-bottom: 0;
}
.label-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}
.label-text svg {
  width: 1.125rem;
  height: 1.125rem;
  opacity: 0.6;
}
.swatch {
  width: 2.25rem;
  height: 2.25rem;
  border: 2px solid rgb(0 0 0 / 0.12);
  border-radius: 9999px;
  cursor: pointer;
  transition: transform 0.2s, border-color 0.2s;
}
.swatch:hover {
  transform: scale(1.1);
}
.swatch.active {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-base-100), 0 0 0 4px var(--color-primary);
}
</style>
