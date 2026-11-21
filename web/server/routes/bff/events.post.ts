export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  return relayApi(event, '/api/events', { method: 'POST', body })
})
