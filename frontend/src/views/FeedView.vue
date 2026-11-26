<script setup lang="ts">
import { ref } from 'vue'
import ArticleReader from '../components/ArticleReader.vue'
import FeedCatalog from '../components/FeedCatalog.vue'
import MorseSignal from '../components/MorseSignal.vue'
import { t } from '../i18n'
import { type Post, useFeedsStore } from '../stores/feeds'
import { useSettingsStore } from '../stores/settings'

const feeds = useFeedsStore()
const settings = useSettingsStore()
const address = ref('')
// The article open in the reader.
const selected = ref<Post>()
// Whether the popular feeds are shown once there are subscriptions; before, they always are.
const browsing = ref(false)

async function subscribe() {
  if (await feeds.subscribe(address.value)) address.value = ''
}
</script>

<template>
  <main class="mx-auto max-w-3xl p-4 sm:p-8">
    <header class="py-8">
      <MorseSignal />
      <h1 class="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl">
        {{ t('feed.titleFirst') }}<br /><span class="text-primary">{{ t('feed.titleSecond') }}</span>
      </h1>
      <p class="mt-3 text-base-content/70">{{ t('feed.intro') }}</p>
    </header>

    <form class="card card-border bg-base-100" @submit.prevent="subscribe">
      <div class="card-body gap-3">
        <label for="address" class="card-title">{{ t('feed.address') }}</label>
        <div class="flex flex-wrap gap-2">
          <input id="address" v-model="address" type="url" required placeholder="https://example.org/feed.xml" class="input grow basis-56" />
          <button class="btn btn-primary" :disabled="feeds.busy">{{ t('feed.subscribe') }}</button>
        </div>
      </div>
    </form>
    <p role="status" aria-live="polite" class="my-3 text-sm">
      {{ feeds.busy ? t('feed.busy') : feeds.message ? t(feeds.message) : '' }} {{ feeds.failures.join(', ') }}
    </p>

    <FeedCatalog v-if="!feeds.feeds.length || browsing" class="mb-4" />

    <div v-if="feeds.feeds.length" class="mb-3 flex flex-wrap items-center gap-2">
      <button
        v-for="item in [{ title: t('feed.all'), id: null }, ...feeds.feeds]"
        :key="item.id ?? 0"
        class="btn btn-sm max-w-full truncate rounded-full"
        :aria-pressed="feeds.filter === item.id"
        :class="feeds.filter === item.id ? 'btn-primary' : 'bg-base-100'"
        @click="feeds.filter = item.id"
      >
        {{ item.title }}
      </button>
      <button class="btn btn-sm btn-ghost ml-auto" :aria-pressed="browsing" :class="{ 'btn-active': browsing }" @click="browsing = !browsing">
        {{ t('catalog.browse') }}
      </button>
      <button class="btn btn-sm btn-ghost" :disabled="feeds.busy" @click="feeds.refresh()">{{ t('feed.refresh') }}</button>
    </div>

    <div class="grid gap-3">
      <button
        v-for="post in feeds.posts"
        :key="`${post.feed.id} ${post.article.url}`"
        aria-haspopup="dialog"
        class="card card-border bg-base-100 text-left transition hover:border-primary"
        @click="selected = post"
      >
        <div class="card-body flex-row items-center gap-4">
          <div class="min-w-0 grow">
            <p class="text-xs text-base-content/65">
              {{ post.feed.title }} <span v-if="post.time">· {{ new Date(post.time).toLocaleDateString(settings.language) }}</span>
            </p>
            <h2 class="card-title my-1 break-words text-lg">{{ post.article.title }}</h2>
            <p class="line-clamp-2 text-sm text-base-content/70">{{ post.article.summary }}</p>
          </div>
          <span class="text-2xl text-primary" aria-hidden="true">›</span>
        </div>
      </button>
      <section v-if="feeds.feeds.length && !feeds.posts.length" class="card card-border bg-base-100">
        <div class="card-body">
          <h2 class="card-title">{{ t('feed.noPosts') }}</h2>
        </div>
      </section>
    </div>

    <ArticleReader v-if="selected" :article="selected.article" :source="selected.feed.title" @close="selected = undefined" />
  </main>
</template>
