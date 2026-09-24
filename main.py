import time
import random
from datetime import datetime
import threading
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

# НАСТРОЙКИ ДЛЯ СТРАНИЦЫ «ПРЕМИУМ»
TOKEN = 'vk1.a.I7P1ILR2L-Xq2g4P-SzeCrBL30ougwSz1trrNMdQVmYm_gTN_z8sqsqI_Y5fNITr_D7mONGLhUXzKPGTQ_fiAU5wAAIpHtcYtMugdrp1p5DvoSmpuj6RdxqjD3-21kenyAu9sl_0C_9iBPPPqtv1_dZoLd5RuPa243I83_JLiJAuJZsWTLLbr8dKh8gZloEHBpscVie47FCsVxA7t3z-bQ'
ALLOWED_USER_ID = 1108362341  # Ваш ID

# Список из 6 групп, куда бот будет поочередно отправлять посты
TARGET_GROUPS = [
    -66681616,   # 1. Вставьте ID восьмой группы
    -126208468,  # 2. Вставьте ID третьей группы
    -196260888,  # 3. Вставьте ID четвертой группы
    -193487983,  # 4. Вставьте ID пятой группы
    -56897360,  # 5. Вставьте ID шестой группы
    -98668610,   # 6. Вставьте ID седьмой группы
]

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