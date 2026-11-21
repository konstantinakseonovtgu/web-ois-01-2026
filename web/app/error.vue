<script setup lang="ts">
import type { NuxtError } from '#app'

const props = defineProps<{ error: NuxtError }>()

const TEXTS: Record<number, { title: string, hint: string }> = {
  403: { title: 'Сюда нельзя', hint: 'У вашей учётной записи нет прав на эту страницу.' },
  404: { title: 'Такой страницы нет', hint: 'Возможно, мероприятие удалили или в адресе опечатка.' },
}
const text = computed(() =>
    TEXTS[props.error.status] ?? { title: 'Что-то пошло не так', hint: 'Попробуйте обновить страницу через минуту.' },
)

useSeoMeta({ title: () => text.value.title })
</script>

<template>
  <AppHeader />
  <main class="container main error">
    <p class="error__code">{{ error.status }}</p>
    <h1>{{ text.title }}</h1>
    <p>{{ text.hint }}</p>
    <button class="button" @click="clearError({ redirect: '/' })">На афишу</button>
  </main>
</template>
