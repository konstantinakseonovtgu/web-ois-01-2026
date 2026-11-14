<script setup lang="ts">
import type { NuxtError } from '#app'

const props = defineProps<{ error: NuxtError }>()

const notFound = computed(() => props.error.status === 404)

useSeoMeta({ title: () => (notFound.value ? 'Страница не найдена' : 'Ошибка') })
</script>

<template>
  <AppHeader />
  <main class="container main error">
    <p class="error__code">{{ error.status }}</p>
    <h1>{{ notFound ? 'Такой страницы нет' : 'Что-то пошло не так' }}</h1>
    <p>{{ notFound ? 'Возможно, мероприятие удалили или в адресе опечатка.' : 'Попробуйте обновить страницу через минуту.' }}</p>
    <button class="button" @click="clearError({ redirect: '/' })">На афишу</button>
  </main>
</template>
