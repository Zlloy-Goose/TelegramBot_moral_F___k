from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
import datetime

import logging
logging.basicConfig(
    filename = 'log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

ADMIN_NAME = ''  #Имя для проверки на пользователя
try: # проверка на присуствии имени в файле info.txt
    with open('info.txt', 'r', encoding='utf-8') as f:
        name = f.readlines()
        if len(name) < 2:
            with open('log' , 'a', encoding='utf-8') as logs:
                logs.write(datetime.datetime.now().strftime( '%Y-%m-%d %H:%M')  + "Нет имени пользователя")
        else:
            if name[1].find('@') == -1:
                with open('log' , 'a', encoding='utf-8') as logs:
                    logs.write(datetime.datetime.now().strftime( '%Y-%m-%d %H:%M')  + "Не найдено имени пользователя, Поставьте перед ним символ @")
            else:
                ADMIN_NAME = name[1][name[1].find('@'):].strip()  # Имя должно находиться после знака @
except BaseException as e: 
    with open('log' , 'a', encoding='utf-8') as logs:
        logs.write(datetime.datetime.now().strftime( '%Y-%m-%d %H:%M')  + e) 


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """После команды start и help выводит сообщение что умеет этот бот"""
    if ADMIN_NAME == update.effective_user.name:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text = """Это бот  удаляет сообщения которые содержат слова из словаря
  /addwords <..> <..> .. - Команда позволяет добавить слова в словарь (команда и нужные слова через пробел)
  /delwords <..> <..> .. - Удаляет все слова после пробела
  /checkwords            - Посмотреть все слова в словаре 
  /clearwords            - Удаляет все слова в словаре""")
    else:
         await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text = """Это бот  удаляет сообщения которые содержат слова из словаря\n  /checkwords - Посмотреть все слова в словаре""" )
    

async def textmessage(upate: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тут происходит проверка каждого сообщения и сравнивается со словарем (каждое с каждым)"""
    try:
        with open('dict', 'r', encoding='utf-8') as dict_words:
            words = dict_words.readlines()
    except BaseException as e:
        with open('log' , 'a', encoding='utf-8') as logs:
            logs.write(datetime.datetime.now().strftime( '%Y-%m-%d %H:%M')  + e)
    for i in range(len(words)):
        words[i]= words[i].strip()
    try:
        for word in words:      
            if word in upate.effective_message.text.lower().split(' '):
        
                await context.bot.delete_message(upate.effective_chat.id, upate.effective_message.id)
        # await context.bot.send_message(chat_id=upate.effective_chat.id,
        #                             text=str(upate.effective_user.id)+'  -  ' + str(upate.effective_message.id))
    except BaseException as e:
        with open('log' , 'a', encoding='utf-8') as logs:
            logs.write(datetime.datetime.now().strftime( '%Y-%m-%d %H:%M')  + e) 



async def add_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление слова в словарь"""
    if ADMIN_NAME == update.effective_user.name:
        with open('dict', 'r+', encoding='utf-8') as dict_words:
            words = dict_words.readlines()
            for i in range(len(words)):
                 words[i] = words[i].strip()
            for word in update.effective_message.text.lower().split(' ')[1:]:
                if not(word in words):
                    dict_words.write(word+'\n')
            await context.bot.send_message(chat_id=update.effective_chat.id , text = "Готово")
    else:
        await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)



async def del_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаление введеных слов из словаря"""
    if ADMIN_NAME == update.effective_user.name:    
        not_found_words = [] # слова которые не нашли
        chat_id = update.effective_chat.id
        try:
            with open('dict', 'r+', encoding='utf-8') as dict_words:
                words = dict_words.readlines()
                for i in range(len(words)):
                    words[i] = words[i].strip()
                for word in update.effective_message.text.lower().split(' ')[1:]:
                        try:
                            words.remove(word)
                        except ValueError:
                            not_found_words.append(word)
                dict_words.seek(0)
                for word in words:
                    dict_words.write('\n'+word)
        except BaseException as e:
            with open('log' , 'a', encoding='utf-8') as logs:
                logs.write(datetime.datetime.now().strftime( '%Y-%m-%d %H:%M')  + e) 
        if not_found_words == []:
            await context.bot.send_message(chat_id, 'Готово')
        else:
            text = ''
            for word in not_found_words:
                text += word + ' -> Не найдено\n'
            await context.bot.send_message(chat_id, text)
    else:
        await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)
    
async def check_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просто отправляет в чат какие слова в словаре """
    try:
        with open('dict', 'r', encoding='utf-8') as file_dict:
            words = file_dict.readlines()
            
        if words == []:
            await context.bot.send_message(update.effective_chat.id, 'Ничего не найдено')
        else:
            for i in range(len(words)):
                words[i] = words[i].strip()
            text = ''
            for word in words:
                text += word + '\n'
            await context.bot.send_message(update.effective_chat.id, text)
    except BaseException as e:
        with open('log' , 'a', encoding='utf-8') as logs:
            logs.write(datetime.datetime.now().strftime( '%Y-%m-%d %H:%M') + e)


async def clear_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаляет содержимое словаря"""
    if ADMIN_NAME == update.effective_user.name:
            with open('dict', 'w', encoding='utf-8') as file_dict:
                file_dict.seek(0)
            await context.bot.send_message(update.effective_chat.id, "Готово")     
    else:
        await context.bot.delete_message(update.effective_chat.id, update.effective_message.id) 


async def bad_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ошибочных команд"""
    if ADMIN_NAME == update.effective_user.name:
        await context.bot.send_message(update.effective_chat.id, "Не верная команда")
    else:
        await context.bot.delete_message(update.effective_chat.id, update.effective_message.id)

def main():
    try:
        with open("info.txt", 'r+', encoding='utf-8') as f: # Файл который содержит токен и имя пользователя 
            token = f.readline().strip()
            token = token[token.find('"'):].strip('"')  #Токен должен быть в "
            if token == '':
                with open('log' , 'a', encoding='utf-8') as logs:
                    logs.write(datetime.datetime.now().strftime( '%Y-%m-%d %H:%M')  + 'Не Найден TOKEN бота!!')
            else:
                try:
                    d = open('dict', 'r+', encoding='utf-8')  # приводим словарь к единому виду и перезаписываем 
                    lines = d.readlines()
                    for i in range(len(lines)):
                        lines[i] = lines[i].lower()
                    d.seek(0)
                    d.writelines(lines)
                    d.close()
                    myBot = ApplicationBuilder().token(token).build()
                    myBot.add_handler(MessageHandler(filters.TEXT&(~filters.COMMAND), textmessage))
                    myBot.add_handler(CommandHandler(['start', 'help'], start))
                    myBot.add_handler(CommandHandler('addwords', add_word))
                    myBot.add_handler(CommandHandler('delwords', del_words))
                    myBot.add_handler(CommandHandler('checkwords', check_words))
                    myBot.add_handler(CommandHandler('clearwords', clear_words))
                    myBot.add_handler(MessageHandler(filters.COMMAND, bad_command))                    

                    myBot.run_polling(allowed_updates=Update.ALL_TYPES)
                except BaseException as e:
                    with open('log' , 'a', encoding='utf-8') as logs:
                        logs.write(datetime.datetime.now().strftime( '%Y-%m-%d %H:%M')  + e)    

  
    except BaseException as e:
        with open('log' , 'a', encoding='utf-8') as logs:
            logs.write(datetime.datetime.now().strftime( '%Y-%m-%d %H:%M') + ' Проблема с файлом info.txt ' +  '   '  + str(e))
    
if __name__ == "__main__":
    main()