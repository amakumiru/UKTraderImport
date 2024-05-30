# UK Trade Data Processing

Этот проект предназначен для получения и обработки данных о торговле Великобритании через API UK Trade Info. Скрипт извлекает информацию о товарах, странах, портах и типах потоков, фильтрует и сохраняет данные в CSV файл.

## Установка

Для работы этого проекта необходим Python 3 и следующие библиотеки:

- requests

Вы можете установить необходимые библиотеки, выполнив следующую команду:

```bash
pip install requests
```

## Использование

1. Скачайте или клонируйте репозиторий.
2. Перейдите в каталог проекта.
3. Запустите скрипт:

```bash
python main.py
```

## Описание скрипта

Скрипт `main.py` выполняет следующие действия:

1. Отправляет GET-запрос к API UK Trade Info для получения данных об импорте за декабрь 2015 года.
2. Расширяет данные о товаре, чтобы включить информацию о Cn8Code и Cn8LongDescription.
3. Обрабатывает полученные данные, извлекая и форматируя информацию о стране, континенте, порте, стоимости, массе и других атрибутах.
4. Сохраняет результаты в файл `import_data.csv`.

### Основные функции

- `send_get_request(url, params=None)`: Отправляет GET-запрос и обрабатывает ошибки.
- `get_data(url, filters=None)`: Получает данные с указанного URL с применением фильтров.
- `get_country_info(country_id)`: Получает информацию о стране по ее ID.
- `get_flowtype_description(flowtype_id)`: Получает описание типа потока по его ID.
- `get_portname(port_id)`: Получает название порта по его ID.
- `process_import_data(import_data)`: Обрабатывает данные импорта и возвращает результат в виде словаря.
- `main()`: Основная функция, которая выполняет весь процесс получения, обработки и сохранения данных.

## Формат CSV

Файл `import_data.csv` будет содержать следующие столбцы:

- `Cn8Code`: Код CN8 товара
- `Cn8LongDescription`: Описание товара
- `EU / NON EU`: Принадлежность к ЕС
- `Continent`: Континент страны
- `Country`: Страна
- `PortName`: Название порта
- `Value (£)`: Стоимость в фунтах стерлингов
- `Net Mass (Kg)`: Чистая масса в килограммах
- `Supp Unit`: Дополнительная единица измерения
- `Flow Type`: Тип потока (импорт/экспорт)
- `Year`: Год
- `Month`: Месяц

## Примеры данных

Пример строки данных, полученной и сохраненной в CSV:

```csv
Cn8Code,Cn8LongDescription,EU / NON EU,Continent,Country,PortName,Value (£),Net Mass (Kg),Supp Unit,Flow Type,Year,Month
01012100,Pure-bred breeding horses,EU,European Union,France,Not Collected,4579640.0,13166.0,54.0,EU Imports,2015,December
```

## Контактная информация

Если у вас есть вопросы или предложения, пожалуйста, свяжитесь со мной по адресу: [amakumiru@yandex.ru]
```
