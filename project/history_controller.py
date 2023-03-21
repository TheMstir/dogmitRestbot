# если кто-то начинает использование то фунцкия берет его имя из бота, берет текущую дату
# Записывает элементы и выводы в фаил.
# Выдает фаил по запросу
# так же может применяться для многозадачности, сохраняя конфиг запроса в личном файле, а не в классе

import datetime


#namus_f = str(datetime.datetime.now()) + str(bot.user)
def history_file(name_id: str, city, count_p, flag, message: list):
    # реформат флага в понятные данные
    if flag == 'PRICE_LOW_TO_HIGH':
        flag = 'Самые дешевые'
    elif flag == 'PRICE_HIGHEST_FIRST':
        flag = 'Самые дорогие'
    elif 'STANCE_FROM_LANDMARK' in flag:
        flag = 'Лучшие предложения, неподалеку от центра'

    shubidub = "\n".join(map(str, message[1:]))  # сборка выдачи
    # Имя пользователя уникально, значит фаил будет уникален,
    date_f = datetime.datetime.now()  # Дата момента записи

    with open(f'historys/{name_id}.json', 'a', encoding='utf-8') as log:
        log.write(f'{date_f}\n{name_id} Вы искали {flag} {count_p} отеля в городе {city}.\nВам было предложено:\n')
        log.write(shubidub)  # который он берёт на последнем шаге, когда отправляет данные список гостиниц)
        print('я записал что-то')
        log.close()
