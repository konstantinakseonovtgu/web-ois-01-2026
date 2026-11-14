const TIME_ZONE = 'Asia/Tomsk'

const dayMonth = new Intl.DateTimeFormat('ru-RU', { timeZone: TIME_ZONE, day: 'numeric', month: 'long' })
const weekday = new Intl.DateTimeFormat('ru-RU', { timeZone: TIME_ZONE, weekday: 'short' })
const hourMinute = new Intl.DateTimeFormat('ru-RU', { timeZone: TIME_ZONE, hour: '2-digit', minute: '2-digit' })
const plural = new Intl.PluralRules('ru-RU')

export function formatDate(iso: string): string {
  const date = new Date(iso)
  return `${dayMonth.format(date)}, ${weekday.format(date)}`
}

export function formatTimeRange(startIso: string, endIso: string): string {
  return `${hourMinute.format(new Date(startIso))}–${hourMinute.format(new Date(endIso))}`
}

export function seatsLabel(free: number): string {
  if (free <= 0) return 'мест нет'
  const word = { one: 'место', few: 'места', many: 'мест', other: 'места' }[plural.select(free)] ?? 'мест'
  return `осталось ${free} ${word}`
}
