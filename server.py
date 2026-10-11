import os
import sqlite3
import requests
from typing import Optional
from fastmcp import FastMCP

mcp = FastMCP(name="DevAssistant MCP")

DB_FILE = "dev_tasks.db"


def init_db():
    """Создает локальную SQLite базу данных для задач, если её еще нет."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            priority TEXT DEFAULT 'normal'
        )
    ''')
    conn.commit()
    conn.close()



init_db()


@mcp.tool()
def add_dev_task(title: str, priority: str = "normal") -> str:
    """
    Добавить новую задачу или баг в локальный бэклог разработчика.

    Args:
        title: Суть задачи или описания бага.
        priority: Приоритет задачи (low, normal, high, critical).
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, priority) VALUES (?, ?)", (title, priority))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return f"Успешно создана задача #{task_id}: '{title}' с приоритетом {priority}."


@mcp.tool()
def list_dev_tasks(status: Optional[str] = None) -> str:
    """
    Вывести список задач разработчика из базы данных с возможностью фильтрации по статусу.

    Args:
        status: Фильтр по статусу (например, 'pending', 'completed' или оставить пустым для всех).
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if status:
        cursor.execute("SELECT id, title, status, priority FROM tasks WHERE status = ?", (status,))
    else:
        cursor.execute("SELECT id, title, status, priority FROM tasks")

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "Список задач пуст."

    result = "Список задач разработчика:\n"
    for row in rows:
        t_id, title, stat, prio = row[0], row[1], row[2], row[3]
        result += f"- [ID: {t_id}] Приоритет: {prio} | Статус: {stat} | Задача: {title}\n"

    return result


@mcp.tool()
def check_url_health(url: str) -> str:
    """
    Проверить доступность внешнего API или веб-страницы (возвращает статус-код и время ответа).

    Args:
        url: Полный URL для проверки (например, https://api.github.com)
    """
    try:
        response = requests.get(url, timeout=5)
        return f"URL: {url} | Статус-код: {response.status_code} | Время отклика: {response.elapsed.total_seconds():.2f} сек."
    except Exception as e:
        return f"Ошибка при запросе к {url}: {str(e)}"



@mcp.resource("config://project-info")
def get_project_info() -> str:
    """Предоставляет общую системную информацию и метаданные о текущем окружении."""
    return f"Python Environment: Active | Database File: {DB_FILE} | OS: {os.name}"


if __name__ == "__main__":
    mcp.run(transport="stdio")