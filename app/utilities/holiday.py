import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

forecastYear = 2024
_url = f'https://www.tanggalan.com/{forecastYear}'
_response = requests.get(_url)

tanggalanContent = None
if _response.status_code == 200:
    tanggalanContent = BeautifulSoup(_response.content, 'html.parser')
else:
    print('Fetch from Tanggalan Failed')

def _extract_holidays(tanggalan: BeautifulSoup, year: int) -> list:
    months_num = {
        'januari': '01', 'februari': '02', 'maret': '03', 'april': '04',
        'mei': '05', 'juni': '06', 'juli': '07', 'agustus': '08',
        'september': '09', 'oktober': '10', 'november': '11', 'desember': '12'
    }
    holidays = []
    article_element = tanggalan.find('article')
    ul_elem = article_element.find_all('ul')
    for ul in ul_elem:
        month_info = ul.find('a', href=True)
        if month_info and str(year) in month_info['href']:
            month = month_info.get_text().strip().replace(str(year), '').strip()
            month_num = months_num[month.lower()]
            table_elem = ul.find_all('table')
            if len(table_elem):
                table = table_elem[0]
                td_elem = table.find_all('td')
                for index, holiday in enumerate(td_elem):
                    if index % 2 == 0:
                        day = holiday.text.strip()
                        description = holiday.find_next_sibling('td')
                        if description:
                            if '-' in day:
                                start_day, end_day = map(int, day.split('-'))
                                for range_day in range(start_day, end_day + 1):
                                    date_string = f'{year}-{month_num}-{str(range_day).zfill(2)}'
                                    res = {
                                        'Tanggal': date_string,
                                        'Keterangan': description.text.strip()
                                    }
                                    holidays.append(res)
                            else:
                                date_string = f'{year}-{month_num}-{day.zfill(2)}'
                                res = {
                                    'Tanggal': date_string,
                                    'Keterangan': description.text.strip()
                                }
                                holidays.append(res)
    return holidays

holiday_data = _extract_holidays(tanggalanContent, forecastYear)
df_holidays = pd.DataFrame(holiday_data)
df_holidays['Tanggal'] = pd.to_datetime(df_holidays['Tanggal'])
df_holidays.to_csv('holidays_2024.csv', index=False)

# Create the directory if it does not exist
output_dir = 'static/holiday'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Path to save the CSV file
output_file_path = os.path.join(output_dir, 'holidays_2024.csv')
df_holidays.to_csv(output_file_path, index=False)
print(f'Holidays saved to {output_file_path}')