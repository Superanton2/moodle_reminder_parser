import requests
from bs4 import BeautifulSoup

url = "https://teaching.kse.org.ua/calendar/view.php?view=month&time=1764540000"
response = requests.get(url)
print(response.text)