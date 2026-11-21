<script setup lang="ts">
import type { MyRegistration, User } from '~/types/api'

definePageMeta({ middleware: 'auth' })
useSeoMeta({ title: 'Мои записи', robots: 'noindex' })

const user = useUser()
const { data, error, refresh } = await useFetch<{ user: User, registrations: MyRegistration[] }>('/bff/my')

if (error.value?.status === 401) {
  user.value = null
  await navigateTo({ path: '/login', query: { next: '/me' } })
}

const cancelling = ref<number | null>(null)
const message = ref('')

async function cancel(eventId: number) {
  message.value = ''
  cancelling.value = eventId
  try {
    await $fetch(`/bff/events/${eventId}/registration`, { method: 'DELETE' })
    await refresh()
  }
  catch (e) {
    message.value = apiErrorMessage(e)
  }
  finally {
    cancelling.value = null
  }
}
</script>

<template>
  <div>
    <h1>Мои записи</h1>
    <p v-if="message" class="form__error" role="alert">{{ message }}</p>

    <p v-if="!data?.registrations.length" class="empty">
      Вы пока никуда не записаны. <NuxtLink to="/">Открыть афишу</NuxtLink>
    </p>

    <ul v-else class="my-list">
      <li v-for="item in data.registrations" :key="item.registration_id" class="my-item">
        <div>
          <NuxtLink :to="`/events/${item.event_id}`" class="my-item__title">{{ item.title }}</NuxtLink>
          <p class="card__where">
            {{ formatDate(item.starts_at) }} · {{ formatTimeRange(item.starts_at, item.ends_at) }} · {{ item.room.name }}
          </p>
        </div>
        <button class="button button--ghost" :disabled="cancelling === item.event_id" @click="cancel(item.event_id)">
          Отменить
        </button>
      </li>
    </ul>
  </div>
</template>
