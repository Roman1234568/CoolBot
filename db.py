 # db.py
import sqlite3

DB_NAME = "careers.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS professions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                tags TEXT NOT NULL
            )
        """)

def add_profession(name, description, tags):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO professions (name, description, tags) VALUES (?, ?, ?)",
                     (name, description, tags))

def find_professions_by_tags(user_tags):
    """Возвращает до 3 профессий, отсортированных по количеству совпадающих тегов."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT name, description, tags FROM professions")
    rows = cur.fetchall()
    conn.close()

    user_set = set(user_tags)
    scored = []
    for row in rows:
        prof_tags = set(row['tags'].split(','))
        match_count = len(prof_tags & user_set)
        if match_count > 0:
          
            scored.append((match_count, len(prof_tags), row))
   
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [{"name": r[2]['name'], "description": r[2]['description']} for r in scored[:3]]

def add_sample_professions():
    with sqlite3.connect(DB_NAME) as conn:
        count = conn.execute("SELECT COUNT(*) FROM professions").fetchone()[0]
        if count > 0:
            return

    samples = [
        ("Программист", "Разработка ПО, написание кода, решение алгоритмических задач.", "data,remote,high_salary,learning_yes,analytical"),
        ("Менеджер по продажам", "Общение с клиентами, переговоры, достижение планов.", "people,office,high_salary,learning_familiar,communicative"),
        ("Дизайнер интерьеров", "Создание уютных и функциональных пространств, работа с цветом и материалами.", "creative,remote,medium_salary,learning_yes,creative_tasks"),
        ("Электрик", "Монтаж и ремонт электрооборудования, работа на объектах.", "tech,travel,medium_salary,learning_familiar,practical"),
        ("HR-специалист", "Подбор персонала, адаптация, развитие сотрудников.", "people,office,medium_salary,learning_yes,communicative"),
        ("Аналитик данных", "Сбор и интерпретация данных, построение отчётов.", "data,remote,high_salary,learning_yes,analytical"),
        ("Фотограф", "Съёмка мероприятий, обработка фото, творческий подход.", "creative,travel,medium_salary,learning_yes,creative_tasks"),
        ("Повар", "Приготовление блюд, разработка рецептов, работа в команде.", "people,office,medium_salary,learning_familiar,practical"),
        ("Логист", "Организация перевозок, оптимизация маршрутов, работа с документами.", "data,office,medium_salary,learning_yes,analytical"),
        ("Ремонтник бытовой техники", "Диагностика и ремонт, выезд к клиентам.", "tech,travel,high_salary,learning_familiar,practical"),
        ("Видеомонтажёр", "Создание видео, монтаж, спецэффекты.", "creative,remote,high_salary,learning_yes,creative_tasks"),
        ("Маркетолог", "Анализ рынка, продвижение продуктов, коммуникации.", "data,office,high_salary,learning_yes,communicative"),
        ("Строитель", "Возведение зданий, работа с инструментами, физический труд.", "tech,travel,medium_salary,learning_familiar,practical"),
        ("Копирайтер", "Написание текстов, контент для сайтов и соцсетей.", "creative,remote,medium_salary,learning_yes,creative_tasks"),
        ("Системный администратор", "Настройка и поддержка IT-инфраструктуры.", "tech,office,high_salary,learning_yes,analytical"),
    ]

    for name, desc, tags in samples:
        add_profession(name, desc, tags)