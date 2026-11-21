<script setup lang="ts">
const user = useUser()

async function logout() {
  await $fetch('/bff/logout', { method: 'POST' }).catch(() => {})
  user.value = null
  await navigateTo('/')
}
</script>

<template>
  <header class="header">
    <div class="container header__inner">
      <NuxtLink to="/" class="header__logo">WEB-ОИС</NuxtLink>
      <span class="header__tagline">студенческая афиша</span>
      <nav class="header__nav">
        <template v-if="user">
          <NuxtLink v-if="user.role !== 'student'" to="/events/new">Создать</NuxtLink>
          <NuxtLink to="/me">Мои записи</NuxtLink>
          <span class="header__user">{{ user.full_name }}</span>
          <button class="header__logout" @click="logout">Выйти</button>
        </template>
        <NuxtLink v-else to="/login">Войти</NuxtLink>
      </nav>
    </div>
  </header>
</template>