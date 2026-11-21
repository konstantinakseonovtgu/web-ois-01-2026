export default defineEventHandler((event) =>
    relayApi(event, `/api/events/${idParam(event)}/registrations/me`, { method: 'DELETE' }),
)