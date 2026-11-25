<script setup lang="ts">
import { ref } from 'vue'
import { t } from '../i18n'
import { useFeedsStore } from '../stores/feeds'
import { useSettingsStore } from '../stores/settings'

const feeds = useFeedsStore()
const settings = useSettingsStore()
// The address of the feed whose removal waits to be confirmed.
const removing = ref('')

function remove(url: string) {
  feeds.remove(url)
  removing.value = ''
}
</script>

<template>
  <main class="mx-auto max-w-3xl p-4 sm:p-8">
    <h1 class="my-6 text-2xl font-semibold">{{ t('settings.title') }}</h1>
    <section class="card card-border mb-4 bg-base-100">
      <div class="card-body gap-4">
        <label class="grid gap-2 font-semibold">
          {{ t('settings.language') }}
          <select v-model="settings.language" class="select">
            <option value="ko">한국어</option>
            <option value="en">English</option>
          </select>
        </label>
        <label class="grid gap-2 font-semibold">
          {{ t('settings.theme') }}
          <select v-model="settings.theme" class="select">
            <option value="">{{ t('settings.auto') }}</option>
            <option value="sos">{{ t('settings.light') }}</option>
            <option value="sos-night">{{ t('settings.dark') }}</option>
          </select>
        </label>
      </div>
    </section>

    <section class="card card-border bg-base-100">
      <div class="card-body">
        <h2 class="card-title">{{ t('settings.subscriptions') }}</h2>
        <p v-if="!feeds.feeds.length">{{ t('feed.empty') }}</p>
        <div v-for="feed in feeds.feeds" :key="feed.url" class="flex flex-wrap items-center gap-2 border-t border-base-300 py-3">
          <div class="min-w-0 grow basis-52">
            <b>{{ feed.title }}</b>
            <p class="break-all text-xs">{{ feed.url }}</p>
          </div>
          <button v-if="removing === feed.url" class="btn btn-sm" @click="removing = ''">{{ t('settings.cancel') }}</button>
          <button class="btn btn-sm btn-ghost" :disabled="feeds.busy" @click="removing === feed.url ? remove(feed.url) : (removing = feed.url)">
            {{ removing === feed.url ? t('settings.confirm') : t('settings.remove') }}
          </button>
        </div>
      </div>
    </section>
  </main>
</template>
