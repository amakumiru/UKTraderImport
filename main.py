import requests
import csv
import calendar

def send_get_request(url, params=None):
    """Отправляет GET-запрос и обрабатывает ошибки."""
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Ошибка: {e} при запросе к {url}")
        return None

def get_data(url, filters=None):
    """Получает данные с указанного URL с применением фильтров."""
    response = send_get_request(url, filters)
    return response['value'][0] if response and 'value' in response else None

def get_country_info(country_id):
    """Получает информацию о стране по ее ID."""
    url = f"https://api.uktradeinfo.com/Country?$select=CountryName,Area1a&$filter=CountryId eq {country_id}"
    return get_data(url)

def get_flowtype_description(flowtype_id):
    """Получает описание типа потока по его ID."""
    url = f"https://api.uktradeinfo.com/FlowType?$select=FlowTypeDescription&$filter=FlowTypeId eq {flowtype_id}"
    data = get_data(url)
    return data['FlowTypeDescription'].strip() if data else 'Неизвестный тип потока'

def get_portname(port_id):
    """Получает название порта по его ID."""
    url = f"https://api.uktradeinfo.com/Port?$select=PortName&$filter=PortId eq {port_id}"
    data = get_data(url)
    return data['PortName'] if data else 'Ошибка: Не удалось получить название порта'

def process_import_data(import_data):
    """Обрабатывает данные импорта и возвращает результат в виде словаря."""
    commodity_id = import_data.get('CommodityId')
    if not commodity_id or not isinstance(import_data['Commodity'], dict):
        return None

    if float(import_data['Value']) > 0.0:
        Cn8Code = import_data['Commodity']['Cn8Code']
        Cn8LongDescription = import_data['Commodity']['Cn8LongDescription']
        country_data = get_country_info(import_data['CountryId'])
        CountryName = country_data['CountryName'] if country_data else 'N/A'
        Continent = country_data['Area1a'] if country_data else 'N/A'
        EU = 'EU' if Continent == 'European Union' else 'NON EU'
        Value = import_data.get('Value', 'N/A')
        NetMass = import_data.get('NetMass', 'N/A')
        SuppUnit = import_data.get('SuppUnit', 'N/A')
        FlowType = get_flowtype_description(import_data['FlowTypeId'])
        PortName = get_portname(import_data['PortId'])
        Year = int(str(import_data['MonthId'])[:4])
        Month = calendar.month_name[int(str(import_data['MonthId'])[4:])]

        return {
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
    return None

def main():
    base_url = "https://api.uktradeinfo.com/OTS"
    params = {
        "$filter": "MonthId eq 201512 and CommodityId gt 93 and (FlowTypeId eq 1 or FlowTypeId  eq 3)",
        "$expand": "Commodity",
        "$top": 20
    }

    response = send_get_request(base_url, params)
    if response and 'value' in response:
        results = []
        for import_data in response['value']:
            result = process_import_data(import_data)
            if result:
                results.append(result)

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
    else:
        print("Ошибка: Не удалось получить данные.")

if __name__ == "__main__":
    main()
