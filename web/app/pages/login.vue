<script setup lang="ts">
import type { User } from '~/types/api'

const route = useRoute()
const user = useUser()

const email = ref('')
const password = ref('')
const error = ref('')
const pending = ref(false)

const next = computed(() => {
  const value = String(route.query.next ?? '/')
  return value.startsWith('/') && !value.startsWith('//') && !value.startsWith('/\\') ? value : '/'
})

async function submit() {
  error.value = ''
  pending.value = true
  try {
    user.value = await $fetch<User>('/bff/login', {
      method: 'POST',
      body: { email: email.value, password: password.value },
    })
    await navigateTo(next.value)
  }
  catch (e) {
    error.value = apiErrorMessage(e)
  }
  finally {
    pending.value = false
  }
}

useSeoMeta({ title: 'Вход', robots: 'noindex' })
</script>

<template>
  <form class="form" @submit.prevent="submit">
    <h1>Вход</h1>
    <label class="field">
      <span>Email</span>
      <input v-model="email" type="email" autocomplete="username" required>
    </label>
    <label class="field">
      <span>Пароль</span>
      <input v-model="password" type="password" autocomplete="current-password" required>
    </label>
    <p v-if="error" class="form__error" role="alert">{{ error }}</p>
    <button class="button" :disabled="pending">{{ pending ? 'Входим…' : 'Войти' }}</button>
  </form>
</template>