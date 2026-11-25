<script setup lang="ts">
// Shown over the reader the first time an article is opened: how pages are turned, where the
// settings are, and how to leave.
import { computed, ref } from 'vue'
import { type MessageKey, t } from '../i18n'

const emit = defineEmits<{
  /** `seen` is whether the guide need not be shown again. */
  done: [seen: boolean]
}>()

const STEPS: { title: MessageKey; text: MessageKey }[] = [
  { title: 'reader.tutorial.turnTitle', text: 'reader.tutorial.turn' },
  { title: 'reader.tutorial.customTitle', text: 'reader.tutorial.custom' },
  { title: 'reader.tutorial.doneTitle', text: 'reader.tutorial.done' },
]
const step = ref(0)
const skip = ref(false)
const last = computed(() => step.value === STEPS.length - 1)

function proceed() {
  if (last.value) emit('done', true)
  else step.value++
}
</script>

<template>
  <div data-reader-ui class="tutorial" role="group" :aria-label="t(STEPS[step].title)">
    <!-- Where a tap does what, on the first step. -->
    <template v-if="step === 0">
      <span class="zone left-[8%]" aria-hidden="true">‹</span>
      <span class="zone right-[8%]" aria-hidden="true">›</span>
    </template>
    <div class="card bg-base-100 text-base-content shadow-xl" :class="step === 0 ? 'mt-48' : ''">
      <div class="card-body gap-3 text-center">
        <button class="btn btn-ghost btn-circle btn-xs absolute top-2 right-2" :aria-label="t('reader.tutorial.close')" @click="emit('done', skip)">✕</button>
        <h3 class="card-title justify-center">{{ t(STEPS[step].title) }}</h3>
        <p class="text-sm text-base-content/70">{{ t(STEPS[step].text) }}</p>
        <div class="mt-2 flex items-center justify-between gap-4">
          <label class="flex cursor-pointer items-center gap-2 text-xs text-base-content/60">
            <input v-model="skip" type="checkbox" class="checkbox checkbox-xs" />
            {{ t('reader.tutorial.skip') }}
          </label>
          <button class="btn btn-primary btn-sm" @click="proceed">
            {{ last ? t('reader.tutorial.finish') : t('reader.tutorial.continue') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tutorial {
  position: absolute;
  inset: 0;
  z-index: 30;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: rgb(0 0 0 / 0.7);
  font-family: var(--font-sans, system-ui, sans-serif);
}
.card {
  width: 100%;
  max-width: 21rem;
}
.zone {
  position: absolute;
  top: 50%;
  display: grid;
  width: 3.75rem;
  height: 3.75rem;
  place-items: center;
  border: 2px solid rgb(255 255 255 / 0.5);
  border-radius: 9999px;
  background: rgb(255 255 255 / 0.2);
  color: white;
  font-size: 1.75rem;
  transform: translateY(-50%);
}
</style>
