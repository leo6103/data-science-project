import time
from selenium import webdriver
from bs4 import BeautifulSoup


driver = webdriver.Chrome()
driver.get('https://www.thegioididong.com/laptop#c=44&o=17&pi=14')
time.sleep(10)
# Get all HTML content
html = driver.page_source
soup = BeautifulSoup(html.encode('utf-8'), 'html.parser')

# print(type(html))
elements_with_data_id = soup.find_all('li', attrs={'data-price': True})

laptop_names = [element.find_next().get('data-name') for element in elements_with_data_id]
