const polling = process.env.WATCH_POLLING === 'true'

export default defineNuxtConfig({
  compatibilityDate: '2026-10-01',
  devtools: { enabled: false },

  css: ['~/assets/main.css'],

  app: {
    head: {
      htmlAttrs: { lang: 'ru' },
      title: 'Студенческая афиша',
      titleTemplate: '%s · WEB-ОИС',
      link: [{ rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }],
    },
  },

  runtimeConfig: {
    apiInternalUrl: process.env.API_INTERNAL_URL ?? 'http://localhost:8000',
    public: {
      siteUrl: 'http://localhost:3000',
    },
  },

  routeRules: {
    '/api/**': { proxy: `${process.env.API_INTERNAL_URL ?? 'http://localhost:8000'}/api/**` },
  },

  vite: polling ? { server: { watch: { usePolling: true, interval: 300 } } } : {},
  watchers: polling ? { chokidar: { usePolling: true, interval: 300 } } : {},
})
