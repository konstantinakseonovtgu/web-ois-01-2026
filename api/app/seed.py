from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Club, Event, Registration, Room, User

TOMSK = timezone(timedelta(hours=7))


def nov(day: int, hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 11, day, hour, minute, tzinfo=TOMSK)


def main() -> None:
    with SessionLocal() as session:
        if session.scalar(select(User.id).limit(1)) is not None:
            print("В базе уже есть данные — ничего не загружаю. Начать с нуля: make db-reset")
            return

        admin = User(email="admin@web-ois.local", full_name="Администратор Системы", password_hash="-", role="admin")
        irina = User(email="it.club@web-ois.local", full_name="Ирина Котова", password_hash="-", role="organizer")
        gleb = User(email="chess@web-ois.local", full_name="Глеб Ферзев", password_hash="-", role="organizer")
        anna = User(email="anna@web-ois.local", full_name="Анна Смирнова", password_hash="-")
        boris = User(email="boris@web-ois.local", full_name="Борис Ковалёв", password_hash="-")
        vera = User(email="vera@web-ois.local", full_name="Вера Лебедева", password_hash="-")
        denis = User(email="denis@web-ois.local", full_name="Денис Орлов", password_hash="-")
        session.add_all([admin, irina, gleb, anna, boris, vera, denis])

        it_club = Club(name="IT-клуб", slug="it-club", description="Лекции и мастер-классы по разработке", organizers=[irina])
        chess = Club(name="Шахматный клуб", slug="chess", description="Турниры и разборы партий", organizers=[gleb])
        cinema = Club(name="Киноклуб", slug="cinema", description="Показы и обсуждения", organizers=[irina])
        session.add_all([it_club, chess, cinema])

        r214 = Room(name="Ауд. 214", building="Главный корпус", capacity=40)
        r101 = Room(name="Ауд. 101", building="Главный корпус", capacity=120)
        cowork = Room(name="Коворкинг", building="Научная библиотека", capacity=25)
        session.add_all([r214, r101, cowork])

        yandex = Event(
            club=it_club, room=r214, author=irina, title="Как устроен поиск Яндекса",
            description="Лекция выпускника о поисковых системах",
            starts_at=nov(20, 18), ends_at=nov(20, 20), capacity=40, status="published",
        )
        tournament = Event(
            club=chess, room=r101, author=gleb, title="Турнир по шахматам",
            description="Блиц, контроль 5+3",
            starts_at=nov(22, 12), ends_at=nov(22, 16), capacity=64, status="published",
        )
        git = Event(
            club=it_club, room=cowork, author=irina, title="Мастер-класс: Git без боли",
            description="Ветки, слияния и как не потерять работу",
            starts_at=nov(24, 17), ends_at=nov(24, 19), capacity=2, status="published",
        )
        stalker = Event(
            club=cinema, room=r214, author=irina, title="Кино: «Сталкер»",
            description="Показ и обсуждение",
            starts_at=nov(27, 18), ends_at=nov(27, 20, 45), capacity=40, status="pending",
        )
        cancelled = Event(
            club=chess, room=r214, author=gleb, title="Разбор партий чемпионата",
            description="Отменено: лектор заболел",
            starts_at=nov(20, 18, 30), ends_at=nov(20, 19, 30), capacity=30, status="cancelled",
        )
        session.add_all([yandex, tournament, git, stalker, cancelled])

        session.add_all([
            Registration(event=yandex, user=anna),
            Registration(event=yandex, user=boris),
            Registration(event=tournament, user=boris),
            Registration(event=git, user=anna),
        ])

        session.commit()
        print("Демо-данные загружены: 7 пользователей, 3 клуба, 3 аудитории, 5 мероприятий, 4 записи")


if __name__ == "__main__":
    main()
