<script setup lang="ts">
import { computed, ref } from 'vue'
import { type CatalogFeed, recommend, type Topic, TOPICS } from '../catalog'
import { t } from '../i18n'
import { LANGUAGES, type PageLanguage } from '../languages'
import { useFeedsStore } from '../stores/feeds'
import { useSettingsStore } from '../stores/settings'

const feeds = useFeedsStore()
const settings = useSettingsStore()
// The language chosen here; until one is, that of the pages.
const chosenLanguage = ref<PageLanguage | null>(null)
const language = computed(() => chosenLanguage.value ?? settings.language)
// The interests chosen; none recommends every feed in the language.
const interests = ref<Topic[]>([])
// The addresses ticked to subscribe to.
const ticked = ref<string[]>([])

// Only the topics the language has feeds on are offered, and only those of the chosen
// interests count, so changing the language never leaves an empty list.
const topics = computed(() => TOPICS.filter((topic) => recommend(language.value, [topic]).length))
const shown = computed(() => recommend(language.value, interests.value.filter((topic) => topics.value.includes(topic))))
const isSubscribed = (feed: CatalogFeed) => feeds.feeds.some((f) => f.url === feed.url)
const open = computed(() => shown.value.filter((feed) => !isSubscribed(feed)))
const chosen = computed(() => open.value.filter((feed) => ticked.value.includes(feed.url)))

const host = (url: string) => new URL(url).hostname.replace(/^(www|feeds|rss)\d*\./, '')

function toggle<T>(list: T[], item: T): T[] {
  return list.includes(item) ? list.filter((x) => x !== item) : [...list, item]
}

function selectAll() {
  ticked.value = [...new Set([...ticked.value, ...open.value.map((feed) => feed.url)])]
}

async function subscribe() {
  await feeds.subscribeAll(chosen.value)
  ticked.value = []
}
</script>

<template>
  <section class="card card-border bg-base-100">
    <div class="card-body gap-4">
      <div>
        <h2 class="card-title">{{ t('catalog.title') }}</h2>
        <p class="text-sm text-base-content/70">{{ t('catalog.intro') }}</p>
      </div>

      <label class="grid gap-2 font-semibold sm:max-w-xs">
        {{ t('catalog.language') }}
        <select class="select" :value="language" @change="chosenLanguage = ($event.target as HTMLSelectElement).value as PageLanguage">
          <option v-for="l in LANGUAGES" :key="l.code" :value="l.code">{{ l.label }}</option>
        </select>
      </label>

      <fieldset>
        <legend class="mb-2 font-semibold">{{ t('catalog.interests') }}</legend>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="topic in topics"
            :key="topic"
            type="button"
            class="btn btn-sm rounded-full"
            :aria-pressed="interests.includes(topic)"
            :class="interests.includes(topic) ? 'btn-primary' : 'bg-base-100'"
            @click="interests = toggle(interests, topic)"
          >
            {{ t(`catalog.topic.${topic}`) }}
          </button>
        </div>
      </fieldset>

      <ul class="grid gap-1 sm:grid-cols-2">
        <li v-for="feed in shown" :key="feed.url">
          <label class="flex cursor-pointer items-start gap-3 rounded-box p-2 hover:bg-base-200" :class="{ 'cursor-default opacity-60': isSubscribed(feed) }">
            <input
              type="checkbox"
              class="checkbox checkbox-primary checkbox-sm mt-0.5"
              :checked="isSubscribed(feed) || ticked.includes(feed.url)"
              :disabled="isSubscribed(feed) || feeds.busy"
              @change="ticked = toggle(ticked, feed.url)"
            />
            <span class="min-w-0">
              <span class="block break-words font-medium">{{ feed.title }}</span>
              <span class="text-xs text-base-content/60">
                {{ isSubscribed(feed) ? t('catalog.subscribed') : host(feed.url) }} ·
                {{ feed.topics.map((topic) => t(`catalog.topic.${topic}`)).join(', ') }}
              </span>
            </span>
          </label>
        </li>
      </ul>

      <div class="card-actions items-center justify-end">
        <button type="button" class="btn btn-ghost btn-sm" :disabled="!open.length || feeds.busy" @click="selectAll">
          {{ t('catalog.selectAll') }}
        </button>
        <button type="button" class="btn btn-primary" :disabled="!chosen.length || feeds.busy" @click="subscribe">
          {{ t('catalog.subscribe', { count: chosen.length }) }}
        </button>
      </div>
    </div>
  </section>
</template>
