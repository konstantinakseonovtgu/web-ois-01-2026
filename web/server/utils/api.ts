import type { H3Event } from 'h3'

type ApiOptions = {
    method?: 'GET' | 'POST' | 'PATCH' | 'DELETE' | 'PUT'
    body?: unknown
}

export async function callApi<T = unknown>(event: H3Event, path: string, options: ApiOptions = {}) {
    const { apiInternalUrl } = useRuntimeConfig(event)
    const cookie = getRequestHeader(event, 'cookie')

    const response = await $fetch.raw<T>(path, {
        baseURL: apiInternalUrl,
        method: options.method,
        body: options.body as Record<string, unknown>,
        headers: cookie ? { cookie } : {},
        ignoreResponseError: true
    })

    for (const setCookie of response.headers.getSetCookie()) {
        appendResponseHeader(event, 'set-cookie', setCookie)
    }

    return { status: response.status, data: response._data as T }
}

export async function relayApi(event: H3Event, path: string, options: ApiOptions = {}) {
    const {status, data} = await callApi(event, path, options)
    setResponseStatus(event, status)
    return data ?? null
}

export function idParam(event: H3Event, name = 'id'): string {
    const value = getRouterParam(event, name) ?? ''
    if (!/^\d+$/.test(value)) {
        throw createError({ status: 404, statusText: 'Not Found' })
    }
    return value
}

