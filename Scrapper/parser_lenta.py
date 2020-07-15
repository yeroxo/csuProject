import requests as req
from bs4 import BeautifulSoup
from Scrapper.crawler_lenta import CrawlerLenta
import random
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError
from requests.exceptions import Timeout
import ast

class ParserLenta:

    def get_steps(self, item):
        description = ''
        info = item.find_all('div', class_='recipe-step__content-wrapper')
        for i in info:
            description += i.find('h3', class_='recipe-step__title').text.strip() + '\n'
            description += i.find('div', class_='recipe-step__description').text.strip() + '\n'
        return description

    def get_ingredients(self, item):
        ingredients = []
        info = item.find_all('div', class_='recipe-ingredients-list-row')
        for ingredient in info:
            ingredients.append(ingredient.find('div', class_='recipe-checkbox__label').text)
        return ingredients

    def get_categories(self, item):
        tags = []
        info = item.find_all('a', class_='recipe-tags__item')
        for i in info:
            tags.append(i.text.replace('  ', '').strip())
        return tags

    def get_cal(self, soup):
        info = soup.find_all('div',
                             class_='recipe-nutritional-cell recipe-nutritional-cell--green recipe-nutritional-value__cell')
        for i in info:
            check = i.find('div', class_='recipe-nutritional-cell__title').text
            if check.replace(' ', '') == 'Энергия':
                cal = i.find('div', class_='recipe-nutritional-cell__sub-value').text
                return cal

    def get_content(self, html, url):
        soup = BeautifulSoup(html, 'lxml')
        recipe = {
            'name': soup.find('h1', class_='recipe-main-header__title').text.strip(),
            'image':  soup.find('div', class_='recipe-main-header__image').get('style')[22:88],
            'ingredients': self.get_ingredients(soup),
            'link': url,
            'description': self.get_steps(soup),
            'calories': self.get_cal(soup),
            'time_cooking': soup.find('div', class_='recipe-header-info__info').text,
            'categories': self.get_categories(soup)
        }
        print(recipe)
        return recipe


    def parse(self, list):
        for l in list:
            html = CrawlerLenta.get_html(CrawlerLenta(), l)
            if html.status_code == 200:
                self.get_content(html.text, l)
            else:
                print("error")

b = ['https://lenta.com/recepty/recipes/U/ustritsy-rokfeller/', 'https://lenta.com/recepty/recipes/k/Kartofelnyy-pirog-s-vetchinoy/']
#p = ParserLenta()
#p.parse(b)

def getHeader():
    list_of_headers = ['Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.0.1) Gecko/20060111 Firefox/1.5.0.1',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US)',
                       'Opera/9.0 (Windows NT 5.1; U; en)',
                       'Opera/9.00 (Nintendo Wii; U; ; 1309-9; en)',
                       'Opera/9.00 (Wii; U; ; 1038-58; Wii Shop Channel/1.0; en)',
                       'Mozilla/2.0 (compatible; MSIE 3.01; Windows 98)',
                       'Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0)']

    return random.choice(list_of_headers)

def getProxy():
    proxies = ['85.12.221.147:80',
               '46.101.113.185:80',
               '212.220.216.70:8080',
               '188.170.233.110:3128',
               '178.62.223.104:80'
               ]
    return random.choice(proxies)

def connect(url, header=True, timeout=5, proxy=True, retries=3):
    session = req.session()

    if header:
        header = {}
        header['User-agent'] = getHeader()
        session.headers = header

    session.timeout = timeout

    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    if proxy:
        proxy = getProxy()
        session.proxies = {'http': proxy}

    try:
        html = session.get(url)
        return html.text
    except ConnectionError:
        print(f'Something went wrong with this connection. Url - {url}')
    except Timeout:
        print(f'Waiting time is up. Url - {url}')

def get_name(item):
    info = item.find('h1', class_='recipe-main-header__title').text.strip()
    return info

def get_image(item):
    info = item.find('div', class_='recipe-main-header__image').get('style')[22:88]
    return info[22:88]

def get_time(item):
    info = item.find('div', class_='recipe-header-info__info').text
    return info

def get_cal(item):
    info = item.find_all('div', class_='recipe-nutritional-cell recipe-nutritional-cell--green recipe-nutritional-value__cell')
    for i in info:
        check = i.find('div', class_='recipe-nutritional-cell__title').text
        if check.replace(' ', '') == 'Энергия':
            cal = i.find('div', class_='recipe-nutritional-cell__sub-value').text
            return cal

def get_ingredients(item):
    ingredients = []
    info = item.find_all('div', class_='recipe-checkbox__label')
#    info = item.find('div', class_='recipe-ingredients-list-container').get('data-model')
    print(info)
    for ingredient in info:
        print(ingredient.find('div', class_='recipe-checkbox__label').text)
        ingredients.append(ingredient.find('div', class_='recipe-checkbox__label').text)
    return ingredients

html = req.get('https://lenta.com/recepty/recipes/v/vanilno-fruktovyy-zavtrak-s-chia/')
soup = BeautifulSoup(html.text, 'lxml')
print(get_ingredients(soup))
def get_description(item):
    description = ''
    info = item.find_all('div', class_='recipe-step__content-wrapper')
    for i in info:
        description += i.find('h3', class_='recipe-step__title').text.strip() + '\n'
        description += i.find('div', class_='recipe-step__description').text.strip() + '\n'
    return description

def categories(item):
    tags = []
    info = item.find_all('a', class_='recipe-tags__item')
    for i in info:
        tags.append(i.text.replace('  ', '').strip())
    return tags

