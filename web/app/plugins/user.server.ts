import type { User } from '~/types/api'

export default defineNuxtPlugin(async () => {
    const answer = await useRequestFetch()<{ user: User | null }>('/bff/me')
        .catch(() => ({ user: null }))
    useUser().value = answer.user
})