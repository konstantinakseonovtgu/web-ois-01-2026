from datetime import datetime, time, timedelta, timezone

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Club, Event, Registration, Room, User
from app.security import hash_password

TOMSK = timezone(timedelta(hours=7))

DEMO_PASSWORD = "webois-demo"


TODAY = datetime.now(TOMSK).date()


def in_days(days: int, hour: int, minute: int = 0) -> datetime:
    return datetime.combine(TODAY + timedelta(days=days), time(hour, minute), TOMSK)


def main() -> None:
    with SessionLocal() as session:
        if session.scalar(select(User.id).limit(1)) is not None:
            print("В базе уже есть данные — ничего не загружаю. Начать с нуля: make db-reset")
            return

        def person(email: str, full_name: str, role: str = "student") -> User:
            return User(email=email, full_name=full_name, role=role, password_hash=hash_password(DEMO_PASSWORD))

        admin = person("admin@web-ois.local", "Администратор Системы", "admin")
        irina = person("it.club@web-ois.local", "Ирина Котова", "organizer")
        gleb = person("chess@web-ois.local", "Глеб Ферзев", "organizer")
        anna = person("anna@web-ois.local", "Анна Смирнова")
        boris = person("boris@web-ois.local", "Борис Ковалёв")
        vera = person("vera@web-ois.local", "Вера Лебедева")
        denis = person("denis@web-ois.local", "Денис Орлов")
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
            starts_at=in_days(5, 18), ends_at=in_days(5, 20), capacity=40, status="published",
        )
        tournament = Event(
            club=chess, room=r101, author=gleb, title="Турнир по шахматам",
            description="Блиц, контроль 5+3",
            starts_at=in_days(7, 12), ends_at=in_days(7, 16), capacity=64, status="published",
        )
        git = Event(
            club=it_club, room=cowork, author=irina, title="Мастер-класс: Git без боли",
            description="Ветки, слияния и как не потерять работу",
            starts_at=in_days(9, 17), ends_at=in_days(9, 19), capacity=2, status="published",
        )
        stalker = Event(
            club=cinema, room=r214, author=irina, title="Кино: «Сталкер»",
            description="Показ и обсуждение",
            starts_at=in_days(12, 18), ends_at=in_days(12, 20, 45), capacity=40, status="pending",
        )
        cancelled = Event(
            club=chess, room=r214, author=gleb, title="Разбор партий чемпионата",
            description="Отменено: лектор заболел",
            starts_at=in_days(5, 18, 30), ends_at=in_days(5, 19, 30), capacity=30, status="cancelled",
        )
        session.add_all([yandex, tournament, git, stalker, cancelled])
        session.flush()

        session.add_all([
            Event(club=it_club, room=cowork, author=irina, title="Разбор резюме джунов",
                  description="Приносите резюме — разберём, что в нём читают первым",
                  starts_at=in_days(3, 17), ends_at=in_days(3, 18, 30), capacity=20, status="published"),
            Event(club=it_club, room=r214, author=irina, title="Docker за один вечер",
                  description="От первого контейнера до compose с базой",
                  starts_at=in_days(14, 18), ends_at=in_days(14, 20), capacity=35, status="published"),
            Event(club=chess, room=r101, author=gleb, title="Сеанс одновременной игры",
                  description="Мастер играет с тридцатью соперниками сразу",
                  starts_at=in_days(15, 15), ends_at=in_days(15, 18), capacity=30, status="published"),
            Event(club=cinema, room=r214, author=irina, title="Кино: «Солярис»",
                  description="Показ и обсуждение",
                  starts_at=in_days(19, 18), ends_at=in_days(19, 20, 50), capacity=40, status="published"),
            Event(club=chess, room=cowork, author=gleb, title="Мат в два хода",
                  description="Решаем задачи на время, призы — шоколадки",
                  starts_at=in_days(21, 16), ends_at=in_days(21, 18), capacity=25, status="published"),
            Event(club=it_club, room=r101, author=irina, title="Хакатон: финал",
                  description="Защита проектов команд перед жюри",
                  starts_at=in_days(26, 10), ends_at=in_days(26, 20), capacity=100, status="published"),
            Event(club=cinema, room=r214, author=irina, title="Студенческий короткий метр",
                  description="Фильмы студентов вуза и разговор с авторами",
                  starts_at=in_days(28, 19), ends_at=in_days(28, 21), capacity=40, status="published"),
        ])

        session.add_all([
            Registration(event=yandex, user=anna),
            Registration(event=yandex, user=boris),
            Registration(event=tournament, user=boris),
            Registration(event=git, user=anna),
        ])

        session.commit()
        print("Демо-данные загружены: 7 пользователей, 3 клуба, 3 аудитории, 12 мероприятий, 4 записи")
        print(f"Пароль всех демо-пользователей: {DEMO_PASSWORD}")


if __name__ == "__main__":
    main()
