from selenium import webdriver
import time
import json
import csv
import logging

logging.basicConfig(filename='errors.log', level=logging.WARNING,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

def main():
    f = open("stats.csv", "w+")
    f.close()
    driver = proxy(False)
    driver = login(driver)
    temp_objects = get_obj_list(driver)
    # temp_objects = temp_objects[:20]

    driver.get('https://dash.getsitecontrol.com/sites/41393/report')
    time.sleep(5)

    get_data(driver, temp_objects)

    command = input()
    if command == 'exit':
        driver.quit()


def proxy(on):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    PATH = 'C:\Program Files (x86)\Python38-32/chromedriver.exe'

    if on:
        options = {
            'proxy':
                {
                    'http': '',
                    'https': ''
                },
        }
        driver = webdriver.Chrome(PATH, seleniumwire_options=options, options=chrome_options)
    else:
        driver = webdriver.Chrome(PATH, options=chrome_options)
    print('[INFO] Successful initialization')
    return driver


def login(driver):
    driver.get('https://dash.getsitecontrol.com/sites')
    time.sleep(5)

    if driver.find_element_by_class_name('registration-page__content'):
        driver.find_element_by_name('email').send_keys('tah.kazan@yandex.ru')
        driver.find_element_by_name('password-input').send_keys('c75453b4')
        driver.find_element_by_class_name('signin__action').click()

    time.sleep(3)
    print('[INFO] Successful authorization')
    return driver


def get_obj_list(driver):
    print('[INFO] Getting widget ID. It takes time, wait..')
    driver.get('https://dash.getsitecontrol.com/api/v1/sites/41393/widgets?mode=list')
    response = driver.find_element_by_tag_name('body').text
    json_list = json.loads(response)
    objects = []
    for item in json_list['objects']:
        obj = []
        id = item['id']
        name = item['name']
        date = item['date_created']
        date = date[:10]
        actions = item['statistics']['metrics_total']['actions']['submit']
        views = item['statistics']['metrics_total']['views']
        ctr = item['statistics']['metrics_total']['ctr']
        obj.extend((id, name, date, actions, views, ctr))
        objects.append(obj)
    print('[INFO] Receiving successfully')
    return objects


def get_data(driver, objects):
    print('[INFO] Data parsing')
    k = 1
    for item in objects:
        time.sleep(1)
        driver.get(f'https://dash.getsitecontrol.com/api/v1/widgets/{str(item[0])}/responses_summary?country=&from=-14d&utm_source_medium=')
        try:
            response = driver.find_element_by_tag_name('body').text
            json_list = json.loads(response)
            for subitem in json_list['form_fields'][0]['options']:
                item.append(subitem['total'])
            print(f'[+] Processed {k}')
            save_data(item, k)
        except Exception as _ex:
            logger.error(_ex)
            print('[ERROR] An error occurred while working with item №' + str(item[0]) + '. Check errors.log for details\n[INFO] Saving the existing information')
            save_errordata(item, k)
            print(f'[~] Saved {k}')
        k += 1
    print('[INFO] Successful parsing')


def save_data(item, k):
    with open("stats.csv", 'a') as outcsv:
        writer = csv.writer(outcsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        try:
            average = (5*item[10]+4*item[9]+3*item[8]+2*item[7]+1*item[6])/(item[10]+item[9]+item[8]+item[7]+item[6])
        except ZeroDivisionError:
            average = 0
        writer.writerow([k, item[1], item[2], item[6], item[7], item[8], item[9], item[10], average, item[3], item[4], item[5]])


def save_errordata(item, k):
    with open("stats.csv", 'a') as outcsv:
        writer = csv.writer(outcsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerow(
            [k, ' ', item[2], ' ', ' ', ' ', ' ', ' ', ' ', item[3], item[4], item[5]])


if __name__ == "__main__":
    main()