import requests
from bs4 import BeautifulSoup


class CrawlerEdaRu:
    def __init__(self):
        self.links = []
        self.url = 'https://eda.ru/recepty'
        self.headers = {'user-agent':
                            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 '
                            'YaBrowser/20.7.0.899 Yowser/2.5 Yptp/1.23 Safari/537.36',
                        'accept': '*/*'}

    def get_html(self, url, params=None):
        return requests.get(url, headers=self.headers, params=params)

    def get_recipes_links(self):
        page_links = []
        for page_num in range(325):
            page_links.append(self.url + '?page=' + str(page_num + 1))
        print(page_links)
        for page in page_links:
            html = self.get_html(page)
            if html.status_code == 200:
                soup = BeautifulSoup(html.text, 'html.parser')
                items = soup.find_all('div', class_='horizontal-tile__content')
                for item in items:
                    self.links.append(str(self.url).rpartition('/')[0] +
                                      item.find('h3', class_='horizontal-tile__item-title')
                                      .find('a').get('href'))
            else:
                print("error")
        print(self.links)
        return self.links


class ParserEdaRu:

    def get_steps(self, item):
        steps = item.find_all('span', class_='instruction__description')
        arr_steps = []
        for step in steps:
            arr_steps.append(step.get_text(strip=True))
        return ' '.join(arr_steps)

    def get_ingredients(self, item):
        ingrid = item.find('div', class_='ingredients-list__content').find_all('span')
        str_ingrid = []
        for i in ingrid:
            if i.find('span') is None:
                pass
            else:
                str_ingrid.append(i.find('span').get_text(strip=True))
        return str_ingrid

    def get_categories(self, item):
        arr_categ = []
        categ = item.find(class_='breadcrumbs').find_all('a')
        for c in categ:
            arr_categ.append(c.get_text())
        return arr_categ
    
    def get_calories(self, item):
        cal = item.find('p', class_='nutrition__weight')
        if cal is not None:
            return cal.get_text()
        else:
            return None

    def get_time(self, item):
        time = item.find('span', class_='prep-time')
        if time is not None:
            return time.get_text(strip=True)
        else:
            return None

    def get_content(self, html, url):
        soup = BeautifulSoup(html, 'html.parser')
        item = soup.find(class_='recipe')
        recipe = {
            'name': item.find('h1').get_text(strip=True).replace('\xa0', ' '),
            'image': item.find('img').get('src'),
            'ingredients': self.get_ingredients(item),
            'link': url,
            'description': self.get_steps(item),
            'calories': self.get_calories(item),
            'time_cooking': self.get_time(item),
            'categories': self.get_categories(item)
        }
        print(recipe)
        return recipe

    def parse(self, list):
        for l in list:
            html = CrawlerEdaRu.get_html(CrawlerEdaRu(),l)
            if html.status_code == 200:
                self.get_content(html.text, l)
            else:
                print("error")

crawler = CrawlerEdaRu()
parser = ParserEdaRu()
#parser.parse(['https://eda.ru/recepty/zavtraki/sirniki-iz-tvoroga-18506', 'https://eda.ru/recepty/supy/sirnij-sup-po-francuzski-s-kuricej-32614'])
#crawler.get_recipes_links()
parser.parse(crawler.get_recipes_links())