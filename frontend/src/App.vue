<script setup lang="ts">
import { ref, watchEffect } from 'vue'
import BrandMark from './components/BrandMark.vue'
import { t } from './i18n'
import { saveLibrary } from './storage'
import { useFeedsStore } from './stores/feeds'
import { useSettingsStore } from './stores/settings'

const settings = useSettingsStore()
const feeds = useFeedsStore()
const LINK = 'hover:bg-neutral-content/10'
const storageError = ref(false)

watchEffect(() => {
  document.documentElement.lang = settings.language
  if (settings.theme) document.documentElement.dataset.theme = settings.theme
  else delete document.documentElement.dataset.theme
})

// Every change of the subscriptions or the preferences is kept in the browser.
watchEffect(() => {
  const { language, theme, readerSize } = settings
  storageError.value = !saveLibrary({ feeds: feeds.feeds, language, theme, readerSize })
})
</script>

<template>
  <div class="min-h-screen bg-base-200 text-base-content">
    <nav class="navbar bg-neutral text-neutral-content">
      <div class="mx-auto flex w-full max-w-5xl flex-wrap items-center gap-2 px-2">
        <RouterLink class="flex items-center gap-2 px-2 font-display text-xl" to="/">
          <BrandMark class="size-7" />
          <span><span class="font-extrabold text-primary">SOS</span> <span class="font-medium">My Feed</span></span>
        </RouterLink>
        <ul class="menu menu-horizontal ml-auto gap-1 px-0">
          <li><RouterLink :class="LINK" to="/" exact-active-class="bg-primary text-primary-content hover:bg-primary">{{ t('nav.feed') }}</RouterLink></li>
          <li><RouterLink :class="LINK" to="/settings" active-class="bg-primary text-primary-content hover:bg-primary">{{ t('nav.settings') }}</RouterLink></li>
        </ul>
      </div>
    </nav>
    <p v-if="storageError" role="alert" class="alert alert-warning alert-soft mx-auto mt-4 max-w-3xl">{{ t('app.saveError') }}</p>
    <RouterView />
  </div>
</template>
