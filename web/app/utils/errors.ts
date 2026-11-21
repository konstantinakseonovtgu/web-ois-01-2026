export function apiErrorMessage(error: unknown): string {
    const detail = (error as { data?: { detail?: unknown } } | null)?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
        return detail
            .map(item => String((item as { msg?: string }).msg ?? '').replace(/^Value error, /, ''))
            .join('; ')
    }
    return 'Не удалось связаться с сервером. Попробуйте ещё раз.'
}