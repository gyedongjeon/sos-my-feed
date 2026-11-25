<script setup lang="ts">
import { computed, ref, watchEffect } from 'vue'
import BrandMark from './components/BrandMark.vue'
import MorseSignal from './components/MorseSignal.vue'
import { en, ko } from './messages'

interface Article { title: string; url: string; summary: string; date: string }
interface Feed { title: string; url: string; articles: Article[] }
interface Library { feeds: Feed[]; language: 'en' | 'ko'; theme: string }

const initial: Library = { feeds: [], language: navigator.language.startsWith('ko') ? 'ko' : 'en', theme: '' }
const key = 'sos-my-feed.v1'
function load(): Library {
  try { return JSON.parse(localStorage.getItem(key) || 'null') ?? initial }
  catch { return initial }
}
const library = ref(load())
const t = computed(() => library.value.language === 'ko' ? ko : en)
const page = ref<'feed' | 'settings'>('feed')
const address = ref('')
const filter = ref('')
const removing = ref('')
const busy = ref(false)
const message = ref<keyof typeof en>()
const failures = ref<string[]>([])
const storageError = ref(false)
watchEffect(() => {
  document.documentElement.lang = library.value.language
  if (library.value.theme) document.documentElement.dataset.theme = library.value.theme
  else delete document.documentElement.dataset.theme
  try { localStorage.setItem(key, JSON.stringify(library.value)); storageError.value = false }
  catch { storageError.value = true }
})
const posts = computed(() => library.value.feeds
  .filter(feed => !filter.value || feed.url === filter.value)
  .flatMap(feed => feed.articles.map(article => ({ article, feed, time: Date.parse(article.date) || 0 })))
  .sort((a, b) => b.time - a.time))
async function fetchFeed(url: string): Promise<Feed> {
  const res = await fetch('/api/feed', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url }) })
  if (!res.ok) throw new Error()
  return { ...await res.json(), url }
}
async function subscribe() {
  if (busy.value) return
  message.value = undefined
  failures.value = []
  busy.value = true
  try {
    const parsed = new URL(address.value.trim())
    parsed.hash = ''
    if (library.value.feeds.some(feed => feed.url === parsed.href)) { message.value = 'duplicate'; return }
    const feed = await fetchFeed(parsed.href)
    library.value.feeds.push(feed)
    address.value = ''
    filter.value = feed.url
  } catch { message.value = 'failed' }
  finally { busy.value = false }
}
async function refresh() {
  busy.value = true
  message.value = undefined
  failures.value = []
  try {
    for (const feed of library.value.feeds) {
      try { Object.assign(feed, await fetchFeed(feed.url)) }
      catch { failures.value.push(feed.title) }
    }
    message.value = failures.value.length ? 'failed' : 'updated'
  } finally { busy.value = false }
}
function remove(url: string) {
  library.value.feeds = library.value.feeds.filter(feed => feed.url !== url)
  if (filter.value === url) filter.value = ''
  removing.value = ''
  failures.value = []
  message.value = undefined
}
</script>
<template>
  <div class="min-h-screen bg-base-200 text-base-content">
    <nav class="navbar bg-neutral text-neutral-content">
      <div class="mx-auto flex w-full max-w-5xl flex-wrap items-center gap-2 px-2">
        <button class="flex items-center gap-2 px-2 font-display text-xl" @click="page = 'feed'">
          <BrandMark class="size-7"/><span><b class="font-extrabold text-primary">SOS</b> My Feed</span>
        </button>
        <ul class="menu menu-horizontal ml-auto gap-1 px-0">
          <li v-for="tab in (['feed','settings'] as const)" :key="tab"><button :class="page === tab && 'bg-primary text-primary-content'" @click="page = tab">{{ t[tab] }}</button></li>
        </ul>
      </div>
    </nav>
    <main class="mx-auto max-w-3xl p-4 sm:p-8">
      <p v-if="storageError" role="alert" class="alert alert-warning">{{ t.saveError }}</p>
      <template v-if="page === 'feed'">
        <header class="py-8"><MorseSignal/>
          <h1 class="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl">{{ t.first }}<br><span class="text-primary">{{ t.second }}</span></h1>
          <p class="mt-3 text-base-content/70">{{ t.intro }}</p>
        </header>
        <form class="card card-border bg-base-100" @submit.prevent="subscribe">
          <div class="card-body gap-3"><label for="address" class="card-title">{{ t.address }}</label>
            <div class="flex flex-wrap gap-2"><input id="address" v-model="address" type="url" required placeholder="https://example.org/feed.xml" class="input grow basis-56">
              <button class="btn btn-primary" :disabled="busy">{{ t.subscribe }}</button></div>
          </div>
        </form>
        <p role="status" aria-live="polite" class="my-3 text-sm">{{ busy ? t.busy : message ? t[message] : '' }} {{ failures.join(', ') }}</p>
        <div v-if="library.feeds.length" class="mb-3 flex flex-wrap items-center gap-2">
          <button v-for="item in [{title:t.all,url:''}, ...library.feeds]" :key="item.url" class="btn btn-sm max-w-full truncate rounded-full" :aria-pressed="filter === item.url" :class="filter === item.url ? 'btn-primary' : 'bg-base-100'" @click="filter = item.url">{{ item.title }}</button>
          <button class="btn btn-sm btn-ghost ml-auto" :disabled="busy" @click="refresh">{{ t.refresh }}</button>
        </div>
        <div class="grid gap-3">
          <a v-for="post in posts" :key="JSON.stringify([post.feed.url,post.article.url])" :href="post.article.url" target="_blank" rel="noopener noreferrer" class="card card-border bg-base-100 transition hover:border-primary">
            <div class="card-body flex-row items-center gap-4"><div class="min-w-0 grow">
              <p class="text-xs text-base-content/65">{{ post.feed.title }} <span v-if="post.time">· {{ new Date(post.time).toLocaleDateString(library.language) }}</span></p>
              <h2 class="card-title my-1 break-words text-lg">{{ post.article.title }}</h2><p class="line-clamp-2 text-sm text-base-content/70">{{ post.article.summary }}</p>
            </div><span class="text-2xl text-primary" aria-hidden="true">›</span></div>
          </a>
          <section v-if="!posts.length" class="card card-border bg-base-100"><div class="card-body"><h2 class="card-title">{{ library.feeds.length ? t.noPosts : t.empty }}</h2><p v-if="!library.feeds.length">{{ t.hint }}</p></div></section>
        </div>
      </template>
      <template v-else>
        <h1 class="my-6 text-2xl font-semibold">{{ t.settings }}</h1>
        <section class="card card-border mb-4 bg-base-100"><div class="card-body gap-4">
          <label class="grid gap-2 font-semibold">{{ t.language }}<select v-model="library.language" class="select"><option value="ko">한국어</option><option value="en">English</option></select></label>
          <label class="grid gap-2 font-semibold">{{ t.theme }}<select v-model="library.theme" class="select"><option value="">{{ t.auto }}</option><option value="sos">{{ t.light }}</option><option value="sos-night">{{ t.dark }}</option></select></label>
        </div></section>
        <section class="card card-border bg-base-100"><div class="card-body"><h2 class="card-title">{{ t.subscriptions }}</h2>
          <p v-if="!library.feeds.length">{{ t.empty }}</p>
          <div v-for="feed in library.feeds" :key="feed.url" class="flex flex-wrap items-center gap-2 border-t border-base-300 py-3">
            <div class="min-w-0 grow basis-52"><b>{{ feed.title }}</b><p class="break-all text-xs">{{ feed.url }}</p></div>
            <button v-if="removing === feed.url" class="btn btn-sm" @click="removing = ''">{{ t.cancel }}</button>
            <button class="btn btn-sm btn-ghost" :disabled="busy" @click="removing === feed.url ? remove(feed.url) : removing = feed.url">{{ removing === feed.url ? t.confirm : t.remove }}</button>
          </div>
        </div></section>
      </template>
    </main>
  </div>
</template>
