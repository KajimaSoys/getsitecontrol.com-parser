from selenium import webdriver
import time
import json
import csv


def main():
    driver = proxy(False)
    driver = login(driver)
    # temp_objects = get_obj_list(driver)

    driver.get('https://dash.getsitecontrol.com/sites/41393/report')
    time.sleep(5)

    temp_objects = [[82643, '1. Тигрёнок в наушниках'], [82733, '2. Полосатый гармонист'], [82736, '3. Лесной саксофонист'], [82737, '4. Звёздная вокалистка'], [82738, '5. Восьминогий флейтист']]

    objects = get_data(driver, temp_objects)
    save_data(objects)

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
    driver.get('https://dash.getsitecontrol.com/api/v1/sites/41393/widgets?mode=list')
    print('[INFO] Getting widget ID. It takes time, wait..')
    response = driver.find_element_by_tag_name('body').text
    json_list = json.loads(response)
    objects = []
    for item in json_list['objects']:
        obj = []
        obj.append(item['id'])
        obj.append(item['name'])
        objects.append(obj)
    print('[INFO] Receiving successfully')
    return objects


def get_data(driver, objects):
    print('[INFO] Data parsing')
    k=1
    for item in objects:
        time.sleep(1)
        driver.get(f'https://dash.getsitecontrol.com/api/v1/widgets/{str(item[0])}/responses_summary?country=&from=-14d&utm_source_medium=')
        response = driver.find_element_by_tag_name('body').text
        json_list = json.loads(response)
        for subitem in json_list['form_fields'][0]['options']:
            item.append(subitem['total'])
        print(f'[+] Processed {k}')
        k += 1
    print('[INFO] Successful parsing')
    return objects


def save_data(objects):
    print('[INFO] Saving data')
    f = open("stats.csv", "w+")
    f.close()
    with open("stats.csv", 'a') as outcsv:
        writer = csv.writer(outcsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        k=1
        for item in objects:
            try:
                average = (5*item[6]+4*item[5]+3*item[4]+2*item[3]+1*item[2])/(item[6]+item[5]+item[4]+item[3]+item[2])
            except ZeroDivisionError:
                average = 0
            writer.writerow([k, item[1], item[2], item[3], item[4], item[5], item[6], average])
            k += 1
    print('[INFO] Data saved successfully')


if __name__ == "__main__":
    main()