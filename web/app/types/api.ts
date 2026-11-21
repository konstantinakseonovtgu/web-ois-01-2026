export interface Club {
  id: number
  name: string
}

export interface Room {
  id: number
  name: string
  building: string
  capacity: number
}

export interface EventItem {
  id: number
  title: string
  description: string
  club_id: number
  room_id: number
  starts_at: string
  ends_at: string
  capacity: number
  status: string
  club: Club
  room: Room
  free_seats: number
}

export interface EventPage {
  items: EventItem[]
  total: number
  page: number
  size: number
}

export interface User {
  id: number
  email: string
  full_name: string
  role: 'student' | 'organizer' | 'admin'
  clubs: Club[]
}

export interface MyRegistration {
  registration_id: number
  event_id: number
  title: string
  starts_at: string
  ends_at: string
  club: Club
  room: Room
}
