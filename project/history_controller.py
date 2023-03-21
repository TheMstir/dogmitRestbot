# если кто-то начинает использование то фунцкия берет его имя из бота, берет текущую дату
# Записывает элементы и выводы в фаил.
# Выдает фаил по запросу
import datetime


# namus_f = str(datetime.datetime.now()) + str(bot.user)
def history_file(name_id: str, city: str, count_p: int, flag: str, message: list):
    # реформат флага в понятные данные
    if flag == 'PRICE_LOW_TO_HIGH':
        flag = 'Самые дешевые'
    elif flag == 'PRICE_HIGHEST_FIRST':
        flag = 'Самые дорогие'
    elif 'STANCE_FROM_LANDMARK' in flag:
        flag = 'Лучшие предложения, неподалеку от центра'

    shubidub = "\n".join(map(str, message[1:]))  # сборка выдачи
    # Имя пользователя уникально, значит фаил будет уникален,
    # date_f = datetime.datetime.now()  # Дата момента записи
    with open(f'historys/{name_id}.json', 'r', encoding='utf-8') as log:
        content = log.read()

    with open(f'historys/{name_id}.json', 'w', encoding='utf-8') as log:
        log.write(f'{str(datetime.datetime.now())}\n{name_id} Вы искали {flag} {count_p} отеля в городе {city}.'
                  f'\nВам было предложено:\n')
        log.write(f'{shubidub} ...')  # который он берёт на последнем шаге, когда отправляет данные список гостиниц)
        log.write(content)
        log.close()
