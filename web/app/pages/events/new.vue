<script setup lang="ts">
import type { Club, EventItem, Room } from '~/types/api'

definePageMeta({ middleware: 'organizer' })
useSeoMeta({ title: 'Новое мероприятие', robots: 'noindex' })

const { data: options } = await useFetch<{ clubs: Club[], rooms: Room[] }>('/bff/event-form')

const onlyClub = options.value?.clubs.length === 1 ? options.value.clubs[0]!.id : null

const form = reactive({
  title: '',
  description: '',
  club_id: onlyClub as number | null,
  room_id: null as number | null,
  date: '',
  start: '18:00',
  end: '20:00',
  capacity: 30,
})
const room = computed(() => options.value?.rooms.find(r => r.id === form.room_id))

const error = ref('')
const pending = ref(false)

const tomsk = (date: string, time: string) => `${date}T${time}:00+07:00`

async function submit() {
  error.value = ''
  pending.value = true
  try {
    const created = await $fetch<EventItem>('/bff/events', {
      method: 'POST',
      body: {
        title: form.title,
        description: form.description,
        club_id: form.club_id,
        room_id: form.room_id,
        starts_at: tomsk(form.date, form.start),
        ends_at: tomsk(form.date, form.end),
        capacity: form.capacity,
      },
    })
    await navigateTo(`/events/${created.id}`)
  }
  catch (e) {
    error.value = apiErrorMessage(e)
  }
  finally {
    pending.value = false
  }
}
</script>

<template>
  <form class="form form--wide" @submit.prevent="submit">
    <h1>Новое мероприятие</h1>

    <label class="field">
      <span>Название</span>
      <input v-model.trim="form.title" required minlength="3" maxlength="200">
    </label>

    <label class="field">
      <span>Описание</span>
      <textarea v-model.trim="form.description" rows="4" maxlength="5000" />
    </label>

    <div class="form__row">
      <label class="field">
        <span>Клуб</span>
        <select v-model.number="form.club_id" required>
          <option :value="null" disabled>Выберите клуб</option>
          <option v-for="club in options?.clubs" :key="club.id" :value="club.id">{{ club.name }}</option>
        </select>
      </label>
      <label class="field">
        <span>Аудитория</span>
        <select v-model.number="form.room_id" required>
          <option :value="null" disabled>Выберите аудиторию</option>
          <option v-for="r in options?.rooms" :key="r.id" :value="r.id">{{ r.name }} — до {{ r.capacity }} мест</option>
        </select>
      </label>
    </div>

    <div class="form__row">
      <label class="field">
        <span>Дата</span>
        <input v-model="form.date" type="date" required>
      </label>
      <label class="field">
        <span>Начало</span>
        <input v-model="form.start" type="time" required>
      </label>
      <label class="field">
        <span>Конец</span>
        <input v-model="form.end" type="time" required>
      </label>
      <label class="field">
        <span>Мест</span>
        <input v-model.number="form.capacity" type="number" required min="1" :max="room?.capacity ?? 1000">
      </label>
    </div>

    <p class="form__hint">Время — по Томску. После создания мероприятие уходит на модерацию.</p>
    <p v-if="error" class="form__error" role="alert">{{ error }}</p>
    <button class="button" :disabled="pending">{{ pending ? 'Создаём…' : 'Создать' }}</button>
  </form>
</template>
