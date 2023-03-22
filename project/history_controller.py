# если кто-то начинает использование то фунцкия берет его имя из бота, берет текущую дату
# Записывает элементы и выводы в фаил.
# Выдает фаил по запросу
import datetime
import os.path


# namus_f = str(datetime.datetime.now()) + str(bot.user)
def history_file(name_id: str, city: str, count_p: int, flag: str, message: list) -> None:
    # реформат флага в понятные данные
    if flag == 'PRICE_LOW_TO_HIGH':
        flag = 'Самые дешевые'
    elif flag == 'PRICE_HIGHEST_FIRST':
        flag = 'Самые дорогие'
    elif 'STANCE_FROM_LANDMARK' in flag:
        flag = 'Лучшие предложения, неподалеку от центра'

    shubidub = "\n".join(map(str, message[1:]))  # сборка выдачи
    # Имя пользователя уникально, значит фаил будет уникален,
    date = datetime.datetime.today()
    date_m = date.strftime('%d-%m-%Y %H:%M') # Дата момента записи
    content = '' \

    if os.path.exists(f'historys/{name_id}.txt',):
        with open(f'historys/{name_id}.txt', 'r', encoding='utf-8') as log:
            content = log.read()

    with open(f'historys/{name_id}.txt', 'w', encoding='utf-8') as log:
        log.write(f'{name_id} Вы искали {flag} {count_p}, отеля в городе {city}.\n{date_m}'
                  f'\nВам было предложено:\n')
        log.write(f'{shubidub} ...')  # который он берёт на последнем шаге, когда отправляет данные список гостиниц)
        log.write(content)
        log.close()
