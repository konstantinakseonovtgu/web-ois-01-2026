INSERT INTO users (email, full_name, password_hash, role) VALUES
                                                              ('admin@web-ois.local',   'Администратор Системы',      '-', 'admin'),
                                                              ('it.club@web-ois.local', 'Ирина Котова',               '-', 'organizer'),
                                                              ('chess@web-ois.local',   'Глеб Ферзев',                '-', 'organizer'),
                                                              ('anna@web-ois.local',    'Анна Смирнова',              '-', 'student'),
                                                              ('boris@web-ois.local',   'Борис Ковалёв',              '-', 'student'),
                                                              ('vera@web-ois.local',    'Вера Лебедева',              '-', 'student'),
                                                              ('denis@web-ois.local',   'Денис Орлов',                '-', 'student');

INSERT INTO clubs (name, slug, description) VALUES
                                                ('IT-клуб',        'it-club', 'Лекции и мастер-классы по разработке'),
                                                ('Шахматный клуб', 'chess',   'Турниры и разборы партий'),
                                                ('Киноклуб',       'cinema',  'Показы и обсуждения');

INSERT INTO club_organizers (user_id, club_id)
SELECT u.id, c.id FROM users u, clubs c
WHERE (u.email, c.slug) IN (
                            ('it.club@web-ois.local', 'it-club'),
                            ('it.club@web-ois.local', 'cinema'),
                            ('chess@web-ois.local',   'chess')
    );

INSERT INTO rooms (name, building, capacity) VALUES
                                                 ('Ауд. 214',  'Главный корпус',      40),
                                                 ('Ауд. 101',  'Главный корпус',      120),
                                                 ('Коворкинг', 'Научная библиотека',  25);

INSERT INTO events (club_id, room_id, created_by, title, description, starts_at, ends_at, capacity, status)
SELECT c.id, r.id, u.id, v.title, v.description, v.starts_at, v.ends_at, v.capacity, v.status
FROM (VALUES
          (1, 'it-club', 'Ауд. 214',  'it.club@web-ois.local', 'Как устроен поиск Яндекса',
           'Лекция выпускника о поисковых системах',
           timestamptz '2026-11-20 18:00+07', timestamptz '2026-11-20 20:00+07', 40, 'published'),
          (2, 'chess',   'Ауд. 101',  'chess@web-ois.local',   'Турнир по шахматам',
           'Блиц, контроль 5+3',
           timestamptz '2026-11-22 12:00+07', timestamptz '2026-11-22 16:00+07', 64, 'published'),
          (3, 'it-club', 'Коворкинг', 'it.club@web-ois.local', 'Мастер-класс: Git без боли',
           'Ветки, слияния и как не потерять работу',
           timestamptz '2026-11-24 17:00+07', timestamptz '2026-11-24 19:00+07', 2,  'published'),
          (4, 'cinema',  'Ауд. 214',  'it.club@web-ois.local', 'Кино: «Сталкер»',
           'Показ и обсуждение',
           timestamptz '2026-11-27 18:00+07', timestamptz '2026-11-27 20:45+07', 40, 'pending'),
          (5, 'chess',   'Ауд. 214',  'chess@web-ois.local',   'Разбор партий чемпионата',
           'Отменено: лектор заболел',
           timestamptz '2026-11-20 18:30+07', timestamptz '2026-11-20 19:30+07', 30, 'cancelled')
     ) AS v(n, club_slug, room_name, author_email, title, description, starts_at, ends_at, capacity, status)
         JOIN clubs c ON c.slug = v.club_slug
         JOIN rooms r ON r.name = v.room_name
         JOIN users u ON u.email = v.author_email
ORDER BY v.n;

INSERT INTO registrations (event_id, user_id)
SELECT e.id, u.id FROM events e, users u
WHERE (e.title, u.email) IN (
                             ('Как устроен поиск Яндекса',  'anna@web-ois.local'),
                             ('Как устроен поиск Яндекса',  'boris@web-ois.local'),
                             ('Турнир по шахматам',         'boris@web-ois.local'),
                             ('Мастер-класс: Git без боли', 'anna@web-ois.local')
    )
ORDER BY e.id, u.id;