import time
import uuid

from datetime import datetime, date
from icalendar import Calendar, Event

from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from configuration import EMAIL, PASSWORD, FILENAME

def moodle_login(driver) -> webdriver.Chrome:
    time.sleep(0.2)

    google_element = driver.find_element(by=By.CSS_SELECTOR, value=".btn.login-identityprovider-btn.btn-block")
    time.sleep(0.2)
    google_element.click()

    email_element = driver.find_element(by=By.ID, value="identifierId")
    email_element.send_keys(EMAIL)

    time.sleep(0.2)

    next_button = driver.find_element(By.ID, "identifierNext")
    next_button.click()

    time.sleep(0.2)

    # Чекаємо, поки поле з'явиться (Google має анімацію переходу)
    password_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "Passwd"))
    )
    password_input.send_keys(PASSWORD)

    time.sleep(0.2)

    next_button2 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[text()='Далі']"))
    )
    next_button2.click()

    return driver

def parce_all_tasks(days) -> list:
    all_tasks = []

    for day in days:
        # Отримуємо дату з атрибута
        timestamp_str = day.get_attribute("data-day-timestamp")

        # Пропускаємо пусті клітинки, якщо такі є
        if not timestamp_str:
            continue

        # Конвертуємо timestamp у читабельну дату
        day_date = datetime.fromtimestamp(int(timestamp_str))
        date_formatted = day_date.strftime('%Y-%m-%d')

        # Знаходимо всі події в середині дня
        events = day.find_elements(By.CSS_SELECTOR, "li[data-region='event-item']")

        if events:
            # print(f"[{date_formatted}] Знайдено подій: {len(events)}")

            for event in events:
                try:
                    # елемент з посиланням
                    link_elem = event.find_element(By.TAG_NAME, "a")

                    # посилання
                    url = link_elem.get_attribute("href")

                    # назва події
                    title = link_elem.get_attribute("title")

                    task_info = {
                        "date": date_formatted,
                        "title": title,
                        "url": url,
                        "timestamp": timestamp_str
                    }
                    all_tasks.append(task_info)
                    # print(f"  --> {title}")

                except Exception as e:
                    print(f"  [!] Помилка обробки події: {e}")

    print("\n--- Збір завершено ---")
    print(f"Всього зібрано завдань: {len(all_tasks)}")

    return all_tasks



driver = webdriver.Chrome()
driver.get("https://teaching.kse.org.ua/calendar/view.php?view=month&time=1764540000")

logined_driver = moodle_login(driver)

time.sleep(5)

# знаходимо дні
table = logined_driver.find_element(By.TAG_NAME, "tbody")
days = table.find_elements(By.CSS_SELECTOR, "td.day")


tasks = parce_all_tasks(days)
for task in tasks:
    print(task)


cal = Calendar()
cal.add('prodid', '-//My Calendar Script//ua//')
cal.add('version', '2.0')

for task in tasks:
    # створюємо подію
    event = Event()

    date_str = '2025-12-25'
    # Перетворення рядка у date об'єкт
    d_object = date.fromisoformat(date_str)

    # подія в певний день
    event.add('dtstart', date.fromisoformat(task["date"]) )
    event.add('dtend', date.fromisoformat(task["date"]) )
    # event.add('dtstart', date(2025, 12, 24))
    # event.add('dtend', date(2025, 12, 24))

    # позначення що вільний в цей час
    event.add('transp', "TRANSPARENT")

    event.add('summary', task["title"])
    event.add('uid', str(uuid.uuid4()))
    event.add('dtstamp', datetime.now())

    event.add("url", task["url"])
    cal.add_component(event)

# зберігаємо до файлу

with open(FILENAME, 'wb') as file:
    file.write(cal.to_ical())

print(f"saved to {FILENAME}")

# time.sleep(100000)