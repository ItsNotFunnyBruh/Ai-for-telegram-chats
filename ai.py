import requests
import re
from telethon import TelegramClient, events

# НАСТРОЙКИ TELEGRAM
API_ID = ''
API_HASH = ''
SESSION_NAME = 'ai_telegram_session'
# ЮЗЕРНЕЙМ ЧЕЛОВЕКА, В ЧАТЕ С КОТОРЫМ БУДЕТ РАБОТАТЬ БОТ
TARGET_USERNAME = ''  

# НАСТРОЙКИ НЕЙРОСЕТИ
API_KEY = ''
API_URL = ""  
MODEL_NAME = ""


client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


@client.on(events.NewMessage(chats=TARGET_USERNAME, pattern=re.compile(r"/help(?: |$)(.*)", re.IGNORECASE)))
async def handle_ai_command(event):
    question = event.pattern_match.group(1).strip()

    if not question:
        await event.reply("Пожалуйста, напишите ваш вопрос после команды `/help`.")
        return

    processing_message = await event.reply("Думаю...")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Ты ИИ асистент, твоя задача отвечать на вопросы. Если пользователь просит тебя что то написать, например: (Напиши: как дела) то твоя задача просто писать то о чем попросил пользователь, и больше ничего лишнего. Отвечай не большим текстом, только главные моменты которые относятся к вопросу."},
            {"role": "user", "content": question}
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()  
        result = response.json()
        ai_response = result['choices'][0]['message']['content'].strip()

        await processing_message.edit(ai_response)
        
    except requests.exceptions.RequestException as e:
        await processing_message.edit(f"Ошибка сети при обращении к API: {e}")
    except (KeyError, IndexError):
        await processing_message.edit("Не удалось получить корректный ответ от нейросети. Проверьте API ключ и название модели.")
    except Exception as e:
        await processing_message.edit(f"Произошла непредвиденная ошибка: {e}")


async def main():
    await client.start()
    print("Клиент запущен. Отслеживание команд активно.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())