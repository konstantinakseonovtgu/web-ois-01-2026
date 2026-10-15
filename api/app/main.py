from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="WEB-ОИС API",
    description="API студенческой афиши мероприятий",
    version="0.1.0"
)

EVENTS = [
    {"id": 1, "title": "Как устроен поиск Яндекса", "club": "IT-клуб", "room": "Аудитория 203"},
    {"id": 2, "title": "Турнир по шахматам", "club": "Шахматный клуб", "room": "Аудитория 311"}
]

@app.get("/api/health")
def health():
    return { "status": "ok" }

@app.get("/api/events")
def list_events():
    return EVENTS

@app.get("/api/events/{event_id}")
def get_event(event_id: int):
    for event in EVENTS:
        if event["id"] == event_id:
            return event
    raise HTTPException(status_code=404, detail="Мероприятие не найдено")