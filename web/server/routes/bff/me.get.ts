export default defineEventHandler(async (event) => {
    const { status, data } = await callApi(event, '/api/auth/me')
    return { user: status === 200 ? data : null }
})