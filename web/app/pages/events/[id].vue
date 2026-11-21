<script setup lang="ts">
import type { EventItem } from '~/types/api'

const route = useRoute()
const config = useRuntimeConfig()

const { data: event, error, refresh } = await useFetch<EventItem>(() => `/api/events/${route.params.id}`)

if (error.value) {
  const notFound = error.value.status === 404 || error.value.status === 422
  throw createError({
    status: notFound ? 404 : 502,
    statusText: notFound ? 'Not Found' : 'Bad Gateway',
    message: notFound ? 'Такого мероприятия нет' : 'Не удалось загрузить мероприятие',
    fatal: true,
  })
}

const STATUS: Record<string, string> = {
  pending: 'На модерации',
  rejected: 'Отклонено',
  cancelled: 'Отменено',
}

const when = computed(() =>
    event.value ? `${formatDate(event.value.starts_at)}, ${formatTimeRange(event.value.starts_at, event.value.ends_at)}` : '',
)

const description = computed(() =>
    event.value ? `${when.value}, ${event.value.room.name}. ${event.value.description}` : '',
)

useSeoMeta({
  title: () => event.value?.title,
  description,
  ogTitle: () => event.value?.title,
  ogDescription: description,
  ogImage: `${config.public.siteUrl}/og-default.png`,
  ogImageWidth: 1200,
  ogImageHeight: 630,
  ogUrl: () => `${config.public.siteUrl}/events/${route.params.id}`,
  ogType: 'website',
  ogSiteName: 'WEB-ОИС',
  ogLocale: 'ru_RU',
  twitterCard: 'summary_large_image',
})
</script>

<template>
  <article v-if="event" class="event">
    <NuxtLink to="/" class="back">← Вся афиша</NuxtLink>
    <p class="card__club">{{ event.club?.name }}</p>
    <h1>{{ event.title }}</h1>

    <dl class="facts">
      <dt>Когда</dt>
      <dd>{{ when }}</dd>
      <dt>Где</dt>
      <dd>{{ event.room?.name }}, {{ event.room?.building }}</dd>
      <dt>Места</dt>
      <dd class="seats" :class="{ 'seats--none': event.free_seats <= 0 }">
        {{ seatsLabel(event.free_seats) }} из {{ event.capacity }}
      </dd>
    </dl>

    <p class="event__description">{{ event.description }}</p>

    <RegisterButton v-if="event.status === 'published'" :event="event" @changed="refresh()" />
  </article>
</template>
