export default defineNuxtRouteMiddleware((to) => {
  const user = useUser().value
  if (!user) {
    return navigateTo({ path: '/login', query: { next: to.fullPath } })
  }
  if (user.role === 'student') {
    return abortNavigation(
      createError({
        status: 403,
        statusText: 'Forbidden',
        message: 'Создавать мероприятия могут организаторы клубов',
        fatal: true,
      }),
    )
  }
})
