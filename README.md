# koloAgent

Персональный Telegram Business бот-ассистент (подключается к аккаунту через Telegram Business).

Архитектура и конвенции повторяют [Tunnex](https://github.com/koloideal/Tunnex):
слои `domain` / `application` / `infrastructure` / `presentation`, DI через dishka,
конфиг — TOML + dature, БД — PostgreSQL + SQLAlchemy + alembic, планировщик — APScheduler.

## Структура

```
src/koloagent/
├── __main__.py                    # entrypoint: python -m koloagent
├── domain/                        # сущности, исключения (бизнес-логика)
├── application/                   # интеракторы, фасады, сервисы, DTO
├── infrastructure/
│   ├── ioc.py                     # dishka-провайдеры
│   ├── config/                    # TOML-конфиг (dature)
│   ├── database/                  # engine, модели, DAO
│   ├── logging/                   # JSON/текстовый логгер
│   └── scheduling/tasks.py        # фоновые задачи APScheduler
└── presentation/
    ├── business_handlers.py       # business_* апдейты (клиентские чаты)
    ├── owner_handlers.py          # прямые сообщения боту
    └── error_handlers.py          # глобальная обработка ошибок
```

## Запуск

```bash
cp secret_data/config.example.toml secret_data/config.toml  # заполнить token и owner_id
just install-dev   # uv sync --all-groups
just run           # uv run python -m koloagent
just watch         # автоперезапуск при изменениях
```

Далее бот добавляется в Telegram: Настройки → Telegram Business → Чат-боты.

## Миграции

```bash
uv run alembic revision --autogenerate -m "message"
uv run alembic upgrade head
```
