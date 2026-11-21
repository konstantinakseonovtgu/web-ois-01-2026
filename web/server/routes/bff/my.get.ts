export default defineEventHandler(async (event) => {
    const [me, registrations] = await Promise.all([
        callApi(event, '/api/auth/me'),
        callApi(event, '/api/me/registrations'),
    ])
    for (const answer of [me, registrations]) {
        if (answer.status !== 200) {
            setResponseStatus(event, answer.status)
            return answer.data
        }
    }
    return { user: me.data, registrations: registrations.data }
})