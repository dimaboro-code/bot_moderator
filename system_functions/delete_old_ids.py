import aiocron
from db import delete_old_data


async def setup_schedule():
    try:
        # Определение времени запуска (каждый час)
        cron_expression = '0 * * * *'

        # Создание расписания и запуск
        cron = aiocron.crontab(cron_expression, func=delete_old_data)
        cron.start()

        print("Расписание успешно установлено")
    except Exception as e:
        print(f"Произошла ошибка при установке расписания: {str(e)}")