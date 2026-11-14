<script setup lang="ts">
import type { EventItem } from '~/types/api'

defineProps<{ event: EventItem }>()
</script>

<template>
  <article class="card">
    <p class="card__club">{{ event.club.name }}</p>
    <h2 class="card__title">
      <NuxtLink :to="`/events/${event.id}`">{{ event.title }}</NuxtLink>
    </h2>
    <p class="card__when">
      {{ formatDate(event.starts_at) }} · {{ formatTimeRange(event.starts_at, event.ends_at) }}
    </p>
    <p class="card__where">{{ event.room.name }}, {{ event.room.building }}</p>
    <p class="seats" :class="{ 'seats--none': event.free_seats <= 0 }">
      {{ seatsLabel(event.free_seats) }}
    </p>
  </article>
</template>
