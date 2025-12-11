# Система автоматического мониторинга и анализа сетевого трафика

## Описание

Полнофункциональная система для мониторинга сетевого трафика, обнаружения аномалий и автоматического реагирования на инциденты безопасности.

## Возможности

- ✅ Захват и анализ сетевого трафика
- ✅ Обнаружение DDoS атак
- ✅ Детекция сканирования портов
- ✅ ML-анализ поведения
- ✅ Автоматическая блокировка угроз
- ✅ Веб-интерфейс для мониторинга
- ✅ Система отчетности

## Технологический стек

**Backend:**
- Python 3.11+
- FastAPI
- SQLAlchemy
- Scapy
- Scikit-learn
- PostgreSQL

**Frontend:**
- HTML5
- CSS3
- Vanilla JavaScript

## Быстрый старт

### Вариант 1: Docker (рекомендуется)

```bash
# Клонировать или скопировать проект
cd traffic_monitoring_system

# Запустить с Docker Compose
docker-compose up -d

# Открыть в браузере
http://localhost:8000
```

### Вариант 2: Локальный запуск

```bash
# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
export DATABASE_URL="postgresql://user:password@localhost:5432/traffic_monitor"
export SECRET_KEY="your-secret-key"

# Запустить приложение
python -m backend.main
```

## Доступы по умолчанию

- **Логин:** admin
- **Пароль:** admin123

## Структура проекта

```
traffic_monitoring_system/
├── backend/              # Backend приложение
│   ├── models/          # Доменные модели
│   ├── repositories/    # Репозитории данных
│   ├── services/        # Бизнес-логика
│   ├── api/            # REST API
│   └── database/       # Настройка БД
├── frontend/            # Frontend приложение
│   ├── css/            # Стили
│   ├── js/             # JavaScript
│   └── *.html          # HTML страницы
├── docker-compose.yml   # Docker конфигурация
└── requirements.txt     # Python зависимости
```

## Архитектура

Система реализует все классы и компоненты из диаграмм:

- **Захват трафика:** CaptureAgent, PacketCapture
- **Обработка:** Processor, RawFlow, ProcessedEvent
- **Анализ:** CorrelationEngine, EventAnalyzer, MLBehaviorAnalyzer
- **Реагирование:** ResponseController, AutoBlockStrategy
- **Хранение:** Репозитории для всех сущностей

## API Endpoints

- `POST /api/token` - Аутентификация
- `GET /api/status` - Статус системы
- `GET /api/incidents` - Список инцидентов
- `POST /api/incidents/{id}/close` - Закрыть инцидент
- `GET /api/traffic/top` - Топ трафика
- `POST /api/capture/start` - Запустить захват
- `GET /api/rules` - Список правил
- `POST /api/rules` - Создать правило

## Примечания

- Для захвата реального трафика требуются root привилегии
- В продакшн среде измените SECRET_KEY и пароли БД
- Система использует PostgreSQL для хранения данных
- ML модели обучаются на собранных данных

## Лицензия

Учебный проект для ЛР №5
