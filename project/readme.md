## **ПОДСКАЗКА ПО РАБОТЕ С БОТОМ**  
@DogmeetRestbot  

### Бот находится в режиме разработки, в данный момент:  
- * Отвечает на сообщение "Привет" и команду /hello-world *
- * Может быть запущен
- * Иногда предоставляет любопытный факт
- * Может выдавать погоду по запросу и совместно с запросом гостиниц
- * Для гостиниц не имеющих gaiaid (Например на территории РФ) необходимо использовать homeland
- * Может выполнять комманды из спика (с некоторыми погрешносятми), соответсвенно описанию:
- * собирает данные для сохранения в историю

## Порядок установки

* Скопировать файлы из проекта
git clone https://gitlab.skillbox.ru/mstislav_danilets/PA_Python_DPO_bot на станцию для запуска

* Установить необходимые модули из окружения консольной командой: 
pip install -r requirements.txt

* Зарегистрироваться на сайте rapidapi.com
Оформить подписку на API Hotels в удобном тарифном плане, после чего получить токен-ключ.

* Получить токен-ключ для бота у телеграм бота @BotFather следуя его инструкции.

* Внести ключи в соответствующие переменные в файле config.py (можно открыть блокнотом). Переменные помечены комментариями.

- * После установки необходимых зависимостей и проведения первичного конфигурирования можно запускать бота.

* Запустить бота консольной командой из папки с проектом или загрузив Фаил main.py из любого редактора python-кода.

* После запуска бот станет доступен в Telegram под тем именем, которое вы для него выбрали.



*В данном файле дается краткий комментарий для каждой используемой в боте функции.*  
*Бот старается давать подсказки, дабы вам было комфортнее его использовать, но для удобства*  
*подсказки собраны в данном файле документации*  


- Учебный бот для поиска гостиниц с сортировкой по цене, поиском лучших вариантов и возможностью посмотреть фотографии гостиниц
- Так же может помочь с текущей погодой в запрашиваемом регионе и небольшим колличеством мета-данных
- Создавался с прицелом на заинтересованное взаимодействие со стороны пользователя, потому снабжен некоторыми резвлекательными элементами 

![](site.com "Заголовок изображения")

@DogmeetRestbot 

1. Узнать топ самых дешёвых отелей в городе (команда /lowprice).
2. Узнать топ самых дорогих отелей в городе (команда /highprice).
3. Узнать топ отелей, наиболее подходящих по цене и расположению от центра
(самые дешёвые и находятся ближе всего к центру) (команда /bestdeal).
4. Узнать список гостиниц без сортировки и доп данных в регионе РФ (команда /homeland_rus)
5. Узнать историю поиска отелей (команда /history)
6. Напрямую узнать погоду, время, ветер и время заката в запрашиваемом регионе (команда /weather)


## Стандартные элементы

1. /start чтобы начать взаимодействие имеет ссылку на кнопку /fast_menu, включающую для пользователя 2 дополнительных быстрых кнопки: поиска по лучшему предложению и перехода на help (т.е. в меню). Дополнительно выдает интересный факт
2. /help открывает меню
3. /cancel или * посреди ввода данных 🗙 отменяет введенные данные что позволяет избегать ошибок и быстро ввести новый запрос города 