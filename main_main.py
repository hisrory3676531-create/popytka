import time
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

# Дальше идут ваши настройки (TOKEN, GROUP_ID и т.д.)
TOKEN = 'vk1.a.BPZCacj7IsrqAR7SxKODed8fchYdmPhjUY1__zquhkpfWw6Nfp9ljEXFIVhkrsCNDA_2jqSbeR5qyLm_0UwW0470rHC73YWkCLiZh3Dx4_sMJk0UvYvbLOneQWuE-nvks5HCPaHG2TJ1Ayb8GiEQcnevHr69mupSdG80KMpFvnDckEOwvkZpEwJuocJCRiPi-Z4B2bmISQ0ll-MdIg1P8w'
ALLOWED_USER_ID = 802229179

# И весь основной код функции main() или запуска обернем в блок:
if __name__ == '__main__':
    try:
        print("Попытка авторизации в VK...", flush=True)
        vk_session = vk_api.VkApi(token=TOKEN)
        vk = vk_session.get_api()
        print("Авторизация успешна! Запуск прослушивания...", flush=True)
        
        # Здесь идет ваш основной цикл работы бота...
        
    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА В РАБОТЕ БОТА: {e}", flush=True)

# НАСТРОЙКИ ДЛЯ ОСНОВНОЙ СТРАНИЦЫ
TOKEN = 'vk1.a.BPZCacj7IsrqAR7SxKODed8fchYdmPhjUY1__zquhkpfWw6Nfp9ljEXFIVhkrsCNDA_2jqSbeR5qyLm_0UwW0470rHC73YWkCLiZh3Dx4_sMJk0UvYvbLOneQWuE-nvks5HCPaHG2TJ1Ayb8GiEQcnevHr69mupSdG80KMpFvnDckEOwvkZpEwJuocJCRiPi-Z4B2bmISQ0ll-MdIg1P8w'
ALLOWED_USER_ID = 802229179  # Ваш ID

# Список из 6 групп, куда бот будет поочередно отправлять посты
TARGET_GROUPS = [
    -66681616,   # 1. Группа 1
    -126208468,  # 2. Группа 2
    -196260888,  # 3. Группа 3
    -193487983,  # 4. Группа 4
    -56897360,   # 5. Группа 5
    -98668610,   # 6. Группа 6
]

# Общие переменные
current_text = None
is_running = False
text_lock = threading.Lock()

def posting_worker(user_id):
    global current_text, is_running
    last_post_ids = {group_id: None for group_id in TARGET_GROUPS}
    
    print("Цикл фоновых публикаций запущен.")
    
    while True:
        try:
            with text_lock:
                running_status = is_running
                text_to_send = current_text
                
            if not running_status or not text_to_send:
                time.sleep(1)
                continue
                
            now = datetime.now()
            
            # Если наступила полночь (00:00), останавливаем работу
            if now.hour == 0 and now.minute == 0:
                with text_lock:
                    is_running = False
                for group_id, post_id in last_post_ids.items():
                    if post_id:
                        try:
                            vk.wall.delete(owner_id=group_id, post_id=post_id)
                        except Exception:
                            pass
                print("Наступило 00:00. Работа завершена.")
                continue
                
            cycle_start_time = time.time()
            cycle_interval = random.randint(60, 300) # от 1 до 5 минут
            
            # Проходим по каждой группе по очереди
            for i, group_id in enumerate(TARGET_GROUPS):
                with text_lock:
                    if not is_running:
                        break
                    active_text = current_text
                    
                try:
                    # 1. Удаляем предыдущий пост в этой группе, если он был
                    if last_post_ids[group_id]:
                        try:
                            vk.wall.delete(owner_id=group_id, post_id=last_post_ids[group_id])
                            print(f"Старый пост в группе {group_id} удален.")
                        except Exception as e:
                            print(f"Не удалось удалить пост в группе {group_id}: {e}")
                    
                    # 2. Публикуем текст расписания
                    response = vk.wall.post(
                        owner_id=group_id,
                        message=active_text
                    )
                    last_post_ids[group_id] = response['post_id']
                    print(f"Опубликован новый пост в группе {group_id}, ID: {response['post_id']}")
                    
                except Exception as e:
                    print(f"Ошибка при публикации в группу {group_id}: {e}")
                
                # Пауза между группами
                if i < len(TARGET_GROUPS) - 1:
                    group_delay = random.randint(0, 20)
                    if group_delay > 0:
                        print(f"Пауза перед следующей группой: {group_delay} сек.")
                        time.sleep(group_delay)
                
            elapsed_time = time.time() - cycle_start_time
            remaining_time = cycle_interval - elapsed_time
            
            if remaining_time > 0:
                print(f"Все группы обновлены. Ждем оставшиеся {int(remaining_time)} сек. до конца цикла.")
                waited = 0
                while waited < remaining_time:
                    with text_lock:
                        if not is_running:
                            break
                    time.sleep(1)
                    waited += 1
                    
        except Exception as e:
            # Защита от падения фонового цикла
            print(f"⚠️ Ошибка в рабочем потоке рассылки: {e}. Перезапуск цикла через 5 секунд...")
            time.sleep(5)

if __name__ == "__main__":
    while True:
        try:
            print("Инициализация подключения к ВКонтакте...")
            vk_session = vk_api.VkApi(token=TOKEN)
            vk = vk_session.get_api()
            longpoll = VkLongPoll(vk_session)
            
            print("Бот успешно запущен и слушает Избранное...")
            
            # Запускаем фоновый поток рассылки
            worker_thread = threading.Thread(target=posting_worker, args=(ALLOWED_USER_ID,), daemon=True)
            worker_thread.start()
            
            # Основной цикл прослушивания сообщений
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    if event.user_id == ALLOWED_USER_ID:
                        with text_lock:
                            current_text = event.text
                            is_running = True
                        print(f"-> Получен новый текст расписания! Обновляем посты...")
                    else:
                        print(f"Игнорирую сообщение от постороннего (ID: {event.user_id})")
                        
        except Exception as e:
            # Защита от обрыва связи с LongPoll (если пропадает интернет или падает VK)
            print(f"⚠️ Критическая ошибка соединения с VK: {e}")
            print("Переподключение через 10 секунд...")
            time.sleep(10)
