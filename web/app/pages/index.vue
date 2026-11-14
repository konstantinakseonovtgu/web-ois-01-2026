<script setup lang="ts">
import type { Club, EventPage } from '~/types/api'

const PAGE_SIZE = 6

const route = useRoute()
const config = useRuntimeConfig()

const clubId = computed(() => Number(route.query.club) || undefined)
const page = computed(() => Math.max(1, Number(route.query.page) || 1))

const { data: clubs } = await useFetch<Club[]>('/api/clubs')

const { data: afisha, error } = await useFetch<EventPage>('/api/events', {
  query: { club_id: clubId, page, size: PAGE_SIZE },
})

if (error.value) {
  throw createError({ status: 502, statusText: 'Bad Gateway', message: 'Не удалось загрузить афишу', fatal: true })
}

const pages = computed(() => Math.ceil((afisha.value?.total ?? 0) / PAGE_SIZE))

function afishaLink(club?: number, toPage = 1) {
  const query: Record<string, string> = {}
  if (club) query.club = String(club)
  if (toPage > 1) query.page = String(toPage)
  return { path: '/', query }
}

const description = 'Лекции, турниры, кино и мастер-классы студенческих клубов. Записаться можно онлайн.'
useSeoMeta({
  title: 'Афиша',
  description,
  ogTitle: 'Афиша студенческих клубов · WEB-ОИС',
  ogDescription: description,
  ogImage: `${config.public.siteUrl}/og-default.png`,
  ogUrl: config.public.siteUrl,
  ogType: 'website',
  ogLocale: 'ru_RU',
  twitterCard: 'summary_large_image',
})
</script>

<template>
  <div>
    <h1>Афиша</h1>

    <nav class="filters" aria-label="Клубы">
      <NuxtLink :to="afishaLink()" class="chip" :class="{ 'chip--active': !clubId }">Все</NuxtLink>
      <NuxtLink
        v-for="club in clubs"
        :key="club.id"
        :to="afishaLink(club.id)"
        class="chip"
        :class="{ 'chip--active': club.id === clubId }"
      >
        {{ club.name }}
      </NuxtLink>
    </nav>

    <p v-if="!afisha?.items.length" class="empty">Здесь пока пусто — загляните позже.</p>

    <div v-else class="grid">
      <EventCard v-for="event in afisha.items" :key="event.id" :event="event" />
    </div>

    <nav v-if="pages > 1" class="pager" aria-label="Страницы">
      <NuxtLink v-if="page > 1" :to="afishaLink(clubId, page - 1)">← Раньше</NuxtLink>
      <span>Страница {{ page }} из {{ pages }}</span>
      <NuxtLink v-if="page < pages" :to="afishaLink(clubId, page + 1)">Позже →</NuxtLink>
    </nav>
  </div>
</template>
