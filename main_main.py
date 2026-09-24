import time
import os
import random
from datetime import datetime
import threading
import sys

print("=== СТАРТ СКРИПТА MAIN_MAIN ===", flush=True)

try:
    import vk_api
    print("Библиотека vk_api импортирована успешно", flush=True)
    
    from vk_api.longpoll import VkLongPoll, VkEventType
    print("LongPoll импортирован успешно", flush=True)
except Exception as e:
    print(f"ОШИБКА ИМПОРТА: {e}", flush=True)

# НАСТРОЙКИ
TOKEN = os.getenv('TOKEN')
ALLOWED_USER_ID = 802229179  # Твой ID

# Список ваших групп (ID должны быть с минусом)
TARGET_GROUPS = [
    -66681616, 
    -126208468, 
    -192608888, 
    -193487983, 
    -56897360,
    # Добавь остальные свои группы при необходимости
]

if __name__ == '__main__':
    try:
        print("Попытка авторизации в VK...", flush=True)
        vk_session = vk_api.VkApi(token=TOKEN)
        vk = vk_session.get_api()
        print("Авторизация успешна! Запуск прослушивания...", flush=True)
        
        # Инициализация LongPoll для чтения сообщений
        longpoll = VkLongPoll(vk_session)
        print("LongPoll успешно запущен. Жду сообщения в Избранном...", flush=True)

        for event in longpoll.listen():
            # Проверяем: новое ли это сообщение, входящее, и от тебя ли оно (Избранное)
            if event.type == VkEventType.MESSAGE_NEW and not event.from_me:
                if event.user_id == ALLOWED_USER_ID:
                    print(f"Получено сообщение из Избранного: {event.text}", flush=True)
                    
                    # 1. Сразу отправляем ответное подтверждение тебе в чат
                    try:
                        vk.messages.send(
                            peer_id=event.user_id,
                            message="Принял ваше сообщение! Начинаю публикацию...",
                            random_id=random.randint(0, 10**9)
                        )
                        print("Отправлено подтверждение в чат.", flush=True)
                    except Exception as send_err:
                        print(f"Не удалось отправить подтверждение: {send_err}", flush=True)

                    # 2. Рассылаем текст по группам
                    for group_id in TARGET_GROUPS:
                        try:
                            vk.wall.post(
                                owner_id=group_id,
                                message=event.text
                            )
                            print(f"Успешно опубликовано в группу {group_id}", flush=True)
                            time.sleep(2) # Пауза между постами, чтобы не получить бан от ВК
                        except Exception as post_err:
                            print(f"Ошибка публикации в группу {group_id}: {post_err}", flush=True)
                            
                    print("Цикл публикации завершен. Снова жду сообщения...", flush=True)

    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА В РАБОТЕ БОТА: {e}", flush=True)
