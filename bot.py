import nextcord
from nextcord.ext import commands
import importlib
import os
import sys
import subprocess
from config import BOT_TOKEN

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def install_requirements(requirements_path):
    """
    Устанавливает зависимости из requirements_path, если файл существует.
    Вызывается каждый запуск.
    """
    if not os.path.exists(requirements_path):
        return

    print(f"Установка/проверка зависимостей из {requirements_path}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
        print("Установка завершена.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при установке зависимостей из {requirements_path}: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")

def load_modules():
    modules_dir = os.path.join(os.path.dirname(__file__), "modules")
    sys.path.insert(0, modules_dir)

    root_req = os.path.join(os.path.dirname(__file__), "requirements.txt")
    install_requirements(root_req)

    for module_name in os.listdir(modules_dir):
        module_path = os.path.join(modules_dir, module_name)
        if os.path.isdir(module_path) and not module_name.startswith("__"):
            module_req = os.path.join(module_path, "requirements.txt")
            install_requirements(module_req)

            try:
                connector = importlib.import_module(f"{module_name}.connector")
                if hasattr(connector, "setup"):
                    connector.setup(bot)
                    print(f"Модуль {module_name} загружен")
                else:
                    print(f"Предупреждение: модуль {module_name} не имеет функции setup()")
            except Exception as e:
                print(f"Ошибка загрузки модуля {module_name}: {e}")

@bot.event
async def on_ready():
    print(f"Бот {bot.user} готов!")

if __name__ == "__main__":
    load_modules()
    bot.run(BOT_TOKEN)
