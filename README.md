# My Booking — template

Run:

```bash
cp .env.example .env
docker compose up --build
```
Запуск тестов, когда контейнер запущен:
docker compose exec web pytest -v
API will be available at http://localhost:8000
