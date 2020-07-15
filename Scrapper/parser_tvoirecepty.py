import requests as req
from bs4 import BeautifulSoup
from crawler_tvoirecepty import CrawlerTvoirecepty

session = req.session()
html = session.get('https://tvoirecepty.ru/recept/tsimes').text
soup = BeautifulSoup(html, 'lxml')
a = ['https://tvoirecepty.ru/recept/kurinoe-file-v-klyare', 'https://tvoirecepty.ru/recept/tsimes', 'https://tvoirecepty.ru/recept/pyure-iz-chechevitsy', 'https://tvoirecepty.ru/recept/bananovyi-rulet', 'https://tvoirecepty.ru/recept/kartofel-zharenyi-v-multivarke', 'https://tvoirecepty.ru/recept/zharkoe-s-kuritsei-v-multivarke', 'https://tvoirecepty.ru/recept/salat-s-risom-i-konservoi', 'https://tvoirecepty.ru/recept/krestyanskii-sup', 'https://tvoirecepty.ru/recept/pasta-s-kuritsei-i-zelenym-goroshkom-0', 'https://tvoirecepty.ru/recept/kartofel-v-multivarke', 'https://tvoirecepty.ru/recept/salat-iz-pekinki-0', 'https://tvoirecepty.ru/recept/morkov-s-syrom', 'https://tvoirecepty.ru/recept/biskvitnoe-pechene', 'https://tvoirecepty.ru/recept/voda-sassi']
b =  ['https://tvoirecepty.ru/recept/kurinoe-file-v-klyare', 'https://tvoirecepty.ru/recept/tsimes', 'https://tvoirecepty.ru/recept/pyure-iz-chechevitsy', 'https://tvoirecepty.ru/recept/bananovyi-rulet', 'https://tvoirecepty.ru/recept/kartofel-zharenyi-v-multivarke', 'https://tvoirecepty.ru/recept/zharkoe-s-kuritsei-v-multivarke', 'https://tvoirecepty.ru/recept/salat-s-risom-i-konservoi', 'https://tvoirecepty.ru/recept/krestyanskii-sup', 'https://tvoirecepty.ru/recept/pasta-s-kuritsei-i-zelenym-goroshkom-0', 'https://tvoirecepty.ru/recept/kartofel-v-multivarke', 'https://tvoirecepty.ru/recept/salat-iz-pekinki-0', 'https://tvoirecepty.ru/recept/morkov-s-syrom', 'https://tvoirecepty.ru/recept/biskvitnoe-pechene', 'https://tvoirecepty.ru/recept/voda-sassi']

class ParserTvoirecepty:

    def get_steps(self, item):
        instructions = ''
        info = item.find_all('div', class_='instruction row-xs margin-bottom-20')
        for i in range(len(info) - 1):
            instructions += info[i].text.replace('  ', '') + '\n'
        return instructions

    def get_ingredients(self, item):
        ingredients = []
        info = item.find('div', class_='ingredients-block recipe-list col-xs-12 col-sm-6 col-md-height col-full-height')
        info = info.find_all('div', class_='ingredient col-xs-12 nopadding margin-bottom-10 collapsed')
        for i in info:
            ingredient = i.find('div', class_='name pull-left').text
            ingredients.append(ingredient.strip())
        return ingredients

    def get_categories(self, item):
        tags = []
        info = item.find('div', class_='container nopadding').find_all('span', class_='tags-link')
        for i in info:
            tags.append(i.text)
        return tags

    def get_cal(self, soup):
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
            'image':  soup.find('div', class_='crop-xs col-xs-12 nopadding').find('img').get('src'),
            'ingredients': self.get_ingredients(soup),
            'link': url,
            'description': self.get_steps(soup),
            'calories': self.get_cal(soup),
            'time_cooking': self.get_time(soup),
            'categories': self.get_categories(soup)
        }
        print(recipe)
        return recipe


    def parse(self, list):
        for l in list:
            html = CrawlerTvoirecepty.get_html(CrawlerTvoirecepty(), l)
            if html.status_code == 200:
                self.get_content(html.text, l)
            else:
                print("error")


p = ParserTvoirecepty()
p.parse(b)
def get_title(soup):
    info = soup.find('div', class_='title-line container').find('h1', class_='pull-left fn').text
    return info
def get_tags(soup):
    tags = []
    info = soup.find('div', class_='container nopadding').find_all('span', class_='tags-link')
    for i in info:
        tags.append(i.text)
    return tags
def get_time(soup):
    info = soup.find('div',
                     class_='calories-block recipe-list col-xs-12 col-sm-12 col-md-12 nopadding margin-bottom-5').find(
        'div', class_='recipe_props cook-time col-xs-12')
    info = info.find('div', class_='pull-right row-xs').find('span', class_='bor font-130').text
    return info
def get_cal(soup):
    info = soup.find('div', class_='nutrition timing-block col-xs-12 col-sm-12 col-md-12 nopadding')
    info = info.find('div', class_='chart pull-right col-xs-3 nopadding').find('div', class_='doughnutSummary')
    info = info.find('p', class_='doughnutSummaryNumber').text
    return info
def get_ingredients(soup):
    ingredients = []
    info = soup.find('div', class_='ingredients-block recipe-list col-xs-12 col-sm-6 col-md-height col-full-height')
    info = info.find_all('div', class_='ingredient col-xs-12 nopadding margin-bottom-10 collapsed')
    for i in info:
        ingredient = i.find('div', class_='name pull-left').text
        ingredients.append(ingredient.strip())
    return ingredients
def get_image(soup):
    info = soup.find('div', class_='crop-xs col-xs-12 nopadding').find('img').get('src')
    return info
def get_quantity(soup):
    info = soup.find('div', class_='portions-count margin-bottom-30').find('span', class_='yield-wrapper')
    info = info.find('input', class_='quantity-field yield').get('value')
    return info
def get_cost(soup):
    info = soup.find('div', class_='col-xs-12 nopadding top-border margin-top-10 margin-bottom-10 padding-top-15')
    info = info.find('div', class_='pull-right').find('span', class_='cost-data bor').find('span')['data-per-portion']
    return str(int(float(info) * 62.17))
def get_instructions(soup):
    instructions = ''
    info = soup.find_all('div', class_='instruction row-xs margin-bottom-20')
    for i in range(len(info)-1):
        instructions += info[i].text.replace('  ', '') + '\n'
    return instructions

