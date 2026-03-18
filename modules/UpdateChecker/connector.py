import aiohttp
import os
from nextcord.ext import commands

# Пытаемся получить URL для проверки версии из config.py
try:
    from config import GITHUB_REPO_RAW_VERSION_URL
except ImportError:
    GITHUB_REPO_RAW_VERSION_URL = None
    print("[UpdateChecker] Предупреждение: не задан GITHUB_REPO_RAW_VERSION_URL в config.py. Проверка обновлений отключена.")

__version__ = "1.0.0"  # версия самого модуля (не системы)

async def check_update(bot):
    """Асинхронно проверяет наличие обновлений системы."""
    if GITHUB_REPO_RAW_VERSION_URL is None:
        return  # ничего не делаем, если URL не задан

    # Определяем путь к локальному файлу version.txt
    # Предполагается, что version.txt лежит в корне проекта (на один уровень выше папки modules)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # поднимаемся на 3 уровня: connector.py -> UpdateChecker -> modules -> корень
    version_file = os.path.join(base_dir, 'version.txt')

    if not os.path.exists(version_file):
        print("[UpdateChecker] Файл version.txt не найден в корне проекта.")
        return

    with open(version_file, 'r') as f:
        local_version = f.read().strip()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(GITHUB_REPO_RAW_VERSION_URL) as resp:
                if resp.status == 200:
                    remote_version = (await resp.text()).strip()
                    if remote_version == local_version:
                        print(f"[UpdateChecker] ✅ Система актуальна (версия {local_version})")
                    else:
                        print(f"[UpdateChecker] ⚠️ Доступно обновление! Локальная версия: {local_version}, удалённая: {remote_version}")
                else:
                    print(f"[UpdateChecker] Не удалось проверить обновления: HTTP {resp.status}")
    except Exception as e:
        print(f"[UpdateChecker] Ошибка при проверке обновлений: {e}")

def setup(bot: commands.Bot):
    """Инициализация модуля: запускает фоновую проверку обновлений."""
    bot.loop.create_task(check_update(bot))
    print("[UpdateChecker] Модуль инициализирован")
