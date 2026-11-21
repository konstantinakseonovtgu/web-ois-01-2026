export default defineEventHandler((event) =>
    relayApi(event, `/api/events/${idParam(event)}/registrations`, { method: 'POST' }),
)