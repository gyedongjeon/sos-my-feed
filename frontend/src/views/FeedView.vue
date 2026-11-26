<script setup lang="ts">
import { ref } from 'vue'
import ArticleReader from '../components/ArticleReader.vue'
import FeedCatalog from '../components/FeedCatalog.vue'
import MorseSignal from '../components/MorseSignal.vue'
import ReaderIcon from '../components/ReaderIcon.vue'
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

/** Opens an article in the reader; it counts as read from then on. */
function open(post: Post) {
  selected.value = post
  feeds.mark([post], true)
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
        <span class="truncate">{{ item.title }}</span>
        <span v-if="feeds.unread(item.id)" class="badge badge-sm" :class="feeds.filter === item.id ? 'badge-neutral' : 'badge-primary badge-soft'">
          {{ feeds.unread(item.id) }}
        </span>
      </button>
      <button class="btn btn-sm btn-ghost ml-auto" :aria-pressed="browsing" :class="{ 'btn-active': browsing }" @click="browsing = !browsing">
        {{ t('catalog.browse') }}
      </button>
      <button class="btn btn-sm btn-ghost" :disabled="feeds.busy" @click="feeds.refresh()">{{ t('feed.refresh') }}</button>
    </div>
    <div v-if="feeds.feeds.length" class="mb-3 flex flex-wrap items-center gap-2">
      <label class="label cursor-pointer gap-2 text-sm">
        <input v-model="feeds.unreadOnly" type="checkbox" class="toggle toggle-sm toggle-primary" />
        {{ t('feed.unreadOnly') }}
      </label>
      <button class="btn btn-sm btn-ghost ml-auto" :disabled="!feeds.unread(feeds.filter)" @click="feeds.markAllRead()">{{ t('feed.markAllRead') }}</button>
    </div>

    <div class="grid gap-3">
      <!-- An article opens in the reader; the icon beside it opens the site's own page instead. -->
      <div
        v-for="post in feeds.posts"
        :key="`${post.feed.id} ${post.article.url}`"
        class="card card-border flex-row items-center bg-base-100 transition hover:border-primary"
      >
        <button aria-haspopup="dialog" class="card-body min-w-0 grow flex-row items-center gap-4 text-left" @click="open(post)">
          <div class="min-w-0 grow" :class="{ 'opacity-60': post.article.read }">
            <p class="text-xs text-base-content/65">
              {{ post.feed.title }} <span v-if="post.time">· {{ new Date(post.time).toLocaleDateString(settings.language) }}</span>
            </p>
            <h2 class="card-title my-1 break-words text-lg" :class="{ 'font-normal': post.article.read }">{{ post.article.title }}</h2>
            <p class="line-clamp-2 text-sm text-base-content/70">{{ post.article.summary }}</p>
          </div>
          <span class="text-2xl text-primary" aria-hidden="true">›</span>
        </button>
        <!-- A dot while the article is unread; a ring once it is read. Either marks it the other way. -->
        <button
          class="btn btn-ghost btn-circle btn-sm shrink-0"
          :aria-label="`${t(post.article.read ? 'feed.markUnread' : 'feed.markRead')}: ${post.article.title}`"
          :title="t(post.article.read ? 'feed.markUnread' : 'feed.markRead')"
          @click="feeds.mark([post], !post.article.read)"
        >
          <span class="size-2.5 rounded-full border-2 border-primary" :class="{ 'bg-primary': !post.article.read }"></span>
        </button>
        <a
          class="btn btn-ghost btn-circle btn-sm mr-3 shrink-0 text-base-content/60"
          :href="post.article.url"
          target="_blank"
          rel="noreferrer"
          @click="feeds.mark([post], true)"
          :aria-label="`${t('reader.original')}: ${post.article.title}`"
          :title="t('reader.original')"
        >
          <ReaderIcon name="external" />
        </a>
      </div>
      <section v-if="feeds.feeds.length && !feeds.posts.length" class="card card-border bg-base-100">
        <div class="card-body">
          <h2 class="card-title">{{ t(feeds.unreadOnly && feeds.unread(feeds.filter) === 0 ? 'feed.allRead' : 'feed.noPosts') }}</h2>
        </div>
      </section>
    </div>

    <ArticleReader v-if="selected" :article="selected.article" :source="selected.feed.title" @close="selected = undefined" />
  </main>
</template>
