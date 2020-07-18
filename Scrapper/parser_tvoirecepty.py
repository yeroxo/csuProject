import requests as req
from bs4 import BeautifulSoup
from model.recipe import Recipe
from urllib.request import urlretrieve
import urllib
from Scrapper.abstract_classes import *


class CrawlerTvoirecepty(Crawler):
    def __init__(self):
        self.links = []
        self.url = 'https://tvoirecepty.ru/recepty?page='
        self.headers = {'user-agent':
                            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 '
                            'YaBrowser/20.7.0.899 Yowser/2.5 Yptp/1.23 Safari/537.36',
                        'accept': '*/*'}

    def get_html(self, url, params=None):
        return req.get(url, headers=self.headers, params=params)

    def get_recipes_links(self):
        for page in range(1, 2):
            url_page = self.url + str(page)
            html = self.get_html(url_page)
            if html.status_code == 200:
                soup = BeautifulSoup(html.text, 'lxml')
                recipes = soup.find_all('div', class_='details product-description')
                for recipe in recipes:
                    linkk = recipe.find('a').get('href')
                    self.links.append('https://tvoirecepty.ru' + linkk)
            else:
                print("error")
        return self.links

    def __str__(self):
        return self.url


session = req.session()
html = session.get('https://tvoirecepty.ru/recept/tsimes').text
soup = BeautifulSoup(html, 'lxml')
a = ['https://tvoirecepty.ru/recept/kurinoe-file-v-klyare', 'https://tvoirecepty.ru/recept/tsimes',
     'https://tvoirecepty.ru/recept/pyure-iz-chechevitsy', 'https://tvoirecepty.ru/recept/bananovyi-rulet',
     'https://tvoirecepty.ru/recept/kartofel-zharenyi-v-multivarke',
     'https://tvoirecepty.ru/recept/zharkoe-s-kuritsei-v-multivarke',
     'https://tvoirecepty.ru/recept/salat-s-risom-i-konservoi', 'https://tvoirecepty.ru/recept/krestyanskii-sup',
     'https://tvoirecepty.ru/recept/pasta-s-kuritsei-i-zelenym-goroshkom-0',
     'https://tvoirecepty.ru/recept/kartofel-v-multivarke', 'https://tvoirecepty.ru/recept/salat-iz-pekinki-0',
     'https://tvoirecepty.ru/recept/morkov-s-syrom', 'https://tvoirecepty.ru/recept/biskvitnoe-pechene',
     'https://tvoirecepty.ru/recept/voda-sassi']
b = ['https://tvoirecepty.ru/recept/kurinoe-file-v-klyare', 'https://tvoirecepty.ru/recept/tsimes',
     'https://tvoirecepty.ru/recept/pyure-iz-chechevitsy', 'https://tvoirecepty.ru/recept/bananovyi-rulet',
     'https://tvoirecepty.ru/recept/kartofel-zharenyi-v-multivarke',
     'https://tvoirecepty.ru/recept/zharkoe-s-kuritsei-v-multivarke',
     'https://tvoirecepty.ru/recept/salat-s-risom-i-konservoi', 'https://tvoirecepty.ru/recept/krestyanskii-sup',
     'https://tvoirecepty.ru/recept/pasta-s-kuritsei-i-zelenym-goroshkom-0',
     'https://tvoirecepty.ru/recept/kartofel-v-multivarke', 'https://tvoirecepty.ru/recept/salat-iz-pekinki-0',
     'https://tvoirecepty.ru/recept/morkov-s-syrom', 'https://tvoirecepty.ru/recept/biskvitnoe-pechene',
     'https://tvoirecepty.ru/recept/voda-sassi']


class ParserTvoirecepty(Parser):

    def get_steps(self, item):
        instructions = ''
        info = item.find_all('div', class_='instruction row-xs margin-bottom-20')
        for i in range(len(info) - 1):
            instructions += info[i].text.replace('  ', '') + '\n'
        if instructions == '':
            info = item.find_all('div', class_='instruction col-sm-6 nopadding-right pull-right row-xs')
            for i in range(len(info) - 1):
                instructions += info[i].text.replace('  ', '') + '\n'
        return instructions

    def get_ingredients(self, item):
        ingredients = []
        info = item.find('div', class_='ingredients-block recipe-list col-xs-12 col-sm-6 col-md-height col-full-height')
        info = info.find_all('div', class_='ingredient col-xs-12 nopadding margin-bottom-10 collapsed')
        for i in info:
            ingredient = i.find('div', class_='name pull-left').text
            ingredients.append(ingredient.strip().lower())
        return ingredients

    def get_categories(self, item):
        tags = []
        info = item.find('div', class_='container nopadding').find_all('span', class_='tags-link')
        for i in info:
            tags.append(i.text)
        return tags

    def get_calories(self, soup):
        info = soup.find('div', class_='nutrition timing-block col-xs-12 col-sm-12 col-md-12 nopadding')
        info = info.find('div', class_='chart pull-right col-xs-3 nopadding').find('div', class_='doughnutSummary')
        info = info.find('p', class_='doughnutSummaryNumber').text
        return info

    def get_time(self, soup):
        info = soup.find('div',
                         class_='calories-block recipe-list col-xs-12 col-sm-12 col-md-12 nopadding margin-bottom-5').find(
            'div', class_='recipe_props cook-time col-xs-12')
        info = info.find('div', class_='pull-right row-xs').find('span', class_='bor font-130').text
        return info

    def get_content(self, html, url):
        soup = BeautifulSoup(html, 'lxml')
        recipe = {
            'name': soup.find('div', class_='title-line container').find('h1', class_='pull-left fn').text,
            'image': self.get_image(soup),
            'ingredients': self.get_ingredients(soup),
            'link': url,
            'description': self.get_steps(soup),
            'calories': self.get_calories(soup),
            'time_cooking': self.get_time(soup),
            'categories': self.get_categories(soup)
        }
        recipe_rec = Recipe(recipe['name'], recipe['image'], recipe['ingredients'], recipe['link'],
                            recipe['description'], recipe['calories'], recipe['time_cooking'], recipe['categories'])
        print(recipe)
        return recipe_rec

    def get_image(self, soup):
        link = soup.find('div', class_='crop-xs col-xs-12 nopadding').find('img').get('src')
        elements = link.split('/')
        name = elements[-1]
        path = f'../photos/{name}'
        self.download_image(link, path)
        return path

# c = CrawlerTvoirecepty()
# print(c.url)
# c = set(c)
# print(len(c))
# print(c)
# p = ParserTvoirecepty()
# p.parse(['https://tvoirecepty.ru/recept/bulochki-s-dzhemom'])
