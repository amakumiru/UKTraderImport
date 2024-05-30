import aiohttp
import asyncio
import csv
import calendar

# Вспомогательная функция для отправки GET-запросов и обработки ошибок
async def send_get_request(session, url, params=None, retries=3):
    for attempt in range(retries):
        try:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as e:
            if e.status in {403, 429}:  # Forbidden or Too Many Requests
                print(f"Ошибка: {e.status}, message='{e.message}', url={e.request_info.url} при запросе к {url}")
                await asyncio.sleep(60 if e.status == 429 else 1)
            else:
                print(f"Ошибка: {e.status}, message='{e.message}', url={e.request_info.url} при запросе к {url}")
        except aiohttp.ClientError as e:
            print(f"Ошибка: {e} при запросе к {url}")

async def fetch_all_data(ports, countries, flowtypes):
    base_url = "https://api.uktradeinfo.com/OTS"
    params = {
        "$filter": "MonthId eq 201512 and CommodityId gt 93 and (FlowTypeId eq 1 or FlowTypeId eq 3)",
        "$expand": "Commodity"
    }
    results = []

    async with aiohttp.ClientSession() as session:
        next_link = base_url + "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        while next_link:
            response = await send_get_request(session, next_link)
            if response and 'value' in response:
                tasks = [process_import_data(session, import_data, ports, countries, flowtypes) for import_data in response['value']]
                page_results = await asyncio.gather(*tasks)
                results.extend([result for result in page_results if result])
                next_link = response.get('@odata.nextLink')
                if next_link:
                    await asyncio.sleep(1)  # Задержка для избежания лимитов запросов
            else:
                next_link = None

    return results

async def fetch_lookup_data():
    async with aiohttp.ClientSession() as session:
        # Словари для хранения данных
        ports = {}
        countries = {}
        flowtypes = {}

        # Получение данных по портам
        next_link = "https://api.uktradeinfo.com/Port?$select=PortId,PortName"
        while next_link:
            response = await send_get_request(session, next_link)
            if response and 'value' in response:
                for item in response['value']:
                    ports[item['PortId']] = item['PortName']
                next_link = response.get('@odata.nextLink')
                if next_link:
                    await asyncio.sleep(1)
            else:
                next_link = None

        # Получение данных по странам
        next_link = "https://api.uktradeinfo.com/Country?$select=CountryId,CountryName,Area1a"
        while next_link:
            response = await send_get_request(session, next_link)
            if response and 'value' in response:
                for item in response['value']:
                    countries[item['CountryId']] = {
                        "CountryName": item['CountryName'],
                        "Continent": item['Area1a']
                    }
                next_link = response.get('@odata.nextLink')
                if next_link:
                    await asyncio.sleep(1)
            else:
                next_link = None

        # Получение данных по типам потоков
        next_link = "https://api.uktradeinfo.com/FlowType?$select=FlowTypeId,FlowTypeDescription"
        while next_link:
            response = await send_get_request(session, next_link)
            if response and 'value' in response:
                for item in response['value']:
                    flowtypes[item['FlowTypeId']] = item['FlowTypeDescription'].strip()
                next_link = response.get('@odata.nextLink')
                if next_link:
                    await asyncio.sleep(1)
            else:
                next_link = None

    return ports, countries, flowtypes

async def process_import_data(session, import_data, ports, countries, flowtypes):
    if float(import_data['Value']) > 0.0:
        Cn8Code = import_data['Commodity']['Cn8Code']
        Cn8LongDescription = import_data['Commodity']['Cn8LongDescription']
        country_data = countries.get(import_data['CountryId'], {})
        CountryName = country_data.get('CountryName', 'N/A')
        Continent = country_data.get('Continent', 'N/A')
        EU = 'EU' if Continent == 'European Union' else 'NON EU'
        Value = import_data.get('Value', 'N/A')
        NetMass = import_data.get('NetMass', 'N/A')
        SuppUnit = import_data.get('SuppUnit', 'N/A')
        FlowType = flowtypes.get(import_data['FlowTypeId'], 'Неизвестный тип потока')
        PortName = ports.get(import_data['PortId'], 'Ошибка: Не удалось получить название порта')
        Year = int(str(import_data['MonthId'])[:4])
        Month = calendar.month_name[int(str(import_data['MonthId'])[4:])]

        result = {
            "Cn8Code": Cn8Code,
            "Cn8LongDescription": Cn8LongDescription,
            "EU / NON EU": EU,
            "Continent": Continent,
            "Country": CountryName,
            "PortName": PortName,
            "Value (£)": Value,
            "Net Mass (Kg)": NetMass,
            "Supp Unit": SuppUnit,
            "Flow Type": FlowType,
            "Year": Year,
            "Month": Month
        }
        return result

async def main():
    ports, countries, flowtypes = await fetch_lookup_data()
    results = await fetch_all_data(ports, countries, flowtypes)

    # Вывод данных
    for item in results:
        print(item)

    # Сохранение данных в CSV
    csv_columns = ["Cn8Code", "Cn8LongDescription", "EU / NON EU", "Continent", "Country", "PortName", "Value (£)", "Net Mass (Kg)", "Supp Unit", "Flow Type", "Year", "Month"]
    csv_file = "import_data.csv"

    try:
        with open(csv_file, 'w', newline='', encoding='UTF-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for item in results:
                writer.writerow(item)
    except IOError as e:
        print(f"I/O error: {e}")

# Запуск основного асинхронного цикла
if __name__ == "__main__":
    asyncio.run(main())
