type Me = { role: string, clubs: { id: number, name: string }[] }

export default defineEventHandler(async (event) => {
  const me = await callApi<Me>(event, '/api/auth/me')
  if (me.status !== 200) {
    setResponseStatus(event, me.status)
    return me.data
  }
  const [clubs, rooms] = await Promise.all([
    me.data.role === 'admin' ? callApi(event, '/api/clubs') : { status: 200, data: me.data.clubs },
    callApi(event, '/api/rooms'),
  ])
  return { clubs: clubs.data, rooms: rooms.data }
})
