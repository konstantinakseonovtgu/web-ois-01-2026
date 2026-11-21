from pydantic import AwareDatetime, BaseModel, ConfigDict, EmailStr, Field, model_validator


class Club(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class Room(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    building: str
    capacity: int


class EventBase(BaseModel):
    title: str = Field(min_length=3, max_length=200, examples=["Как устроен поиск Яндекса"])
    description: str = Field(default="", max_length=5000)
    club_id: int = Field(examples=[1])
    room_id: int = Field(examples=[1])
    starts_at: AwareDatetime = Field(examples=["2026-11-27T18:00:00+07:00"])
    ends_at: AwareDatetime = Field(examples=["2026-11-27T20:00:00+07:00"])
    capacity: int = Field(gt=0, le=1000, examples=[30])


class EventCreate(EventBase):
    @model_validator(mode="after")
    def check_time_order(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("Время окончания должно быть позже времени начала")
        return self


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    room_id: int | None = None
    starts_at: AwareDatetime | None = None
    ends_at: AwareDatetime | None = None
    capacity: int | None = Field(default=None, gt=0, le=1000)


class EventRead(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str = Field(examples=["published"])
    club: Club
    room: Room
    free_seats: int = Field(examples=[12], description="Лимит минус активные записи")


class EventPage(BaseModel):
    items: list[EventRead]
    total: int
    page: int
    size: int


class RegistrationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    user_id: int
    status: str
    created_at: AwareDatetime


class Participant(BaseModel):
    user_id: int
    full_name: str
    email: str
    created_at: AwareDatetime

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    clubs: list[Club] = Field(description="Клубы, которые ведёт организатор; у студента — пусто")

class MyRegistration(BaseModel):
    registration_id: int
    event_id: int
    title: str
    starts_at: AwareDatetime
    ends_at: AwareDatetime
    club: Club
    room: Room

class RegisterRequest(BaseModel):
    email: EmailStr = Field(examples=["new.student@tsu.ru"])
    full_name: str = Field(min_length=2, max_length=200, examples=["Мария Новикова"])
    password: str = Field(min_length=15, max_length=128, examples=["correct horse battery"])


class LoginRequest(BaseModel):
    email: str = Field(examples=["anna@web-ois.local"])
    password: str = Field(examples=["webois-demo"])


class ErrorResponse(BaseModel):
    detail: str = Field(examples=["Мероприятие не найдено"])
