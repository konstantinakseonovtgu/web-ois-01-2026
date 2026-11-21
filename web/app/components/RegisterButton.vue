<script setup lang="ts">
import type { EventItem, MyRegistration } from '~/types/api'

const props = defineProps<{ event: EventItem }>()
const emit = defineEmits<{ changed: [] }>()

const user = useUser()
const route = useRoute()

const { data: mine, status, refresh } = await useFetch<{ registrations: MyRegistration[] }>('/bff/my', {
  server: false,
  immediate: !!user.value,
})
const registered = computed(() => mine.value?.registrations.some(r => r.event_id === props.event.id) ?? false)

const pending = ref(false)
const message = ref('')

async function act(method: 'POST' | 'DELETE') {
  message.value = ''
  pending.value = true
  try {
    await $fetch(`/bff/events/${props.event.id}/registration`, { method })
    await refresh()
    emit('changed')
  }
  catch (e) {
    message.value = apiErrorMessage(e)
  }
  finally {
    pending.value = false
  }
}
</script>

<template>
  <div class="register">
    <NuxtLink v-if="!user" class="button" :to="{ path: '/login', query: { next: route.fullPath } }">
      Войти, чтобы записаться
    </NuxtLink>
    <button v-else-if="status !== 'success'" class="button" disabled>Проверяем запись…</button>
    <template v-else-if="registered">
      <p class="register__status">Вы записаны</p>
      <button class="button button--ghost" :disabled="pending" @click="act('DELETE')">Отменить запись</button>
    </template>
    <button v-else class="button" :disabled="pending || event.free_seats <= 0" @click="act('POST')">
      {{ event.free_seats > 0 ? 'Записаться' : 'Мест нет' }}
    </button>
    <p v-if="message" class="form__error" role="alert">{{ message }}</p>
  </div>
</template>
