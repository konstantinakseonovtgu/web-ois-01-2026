export default defineNuxtRouteMiddleware((to) => {
    if (!useUser().value) {
        return navigateTo({ path: '/login', query: { next: to.fullPath } })
    }
})