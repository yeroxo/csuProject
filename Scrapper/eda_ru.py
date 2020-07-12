import requests
from bs4 import BeautifulSoup


class Crawler:
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
        for page_num in range(3329):
            page_links.append(self.url + '?page=' + str(page_num + 1))
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
        return self.links


class Parser:

    def get_content(self, html, url):
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all(class_='recipe')

        recipe = []
        for item in items:
            steps = item.find_all('span', class_='instruction__description')
            arr_steps = []
            for step in steps:
                arr_steps.append(step.get_text(strip=True))
            str_steps = ' '.join(arr_steps)
            ingrid = item.find('div', class_='ingredients-list__content').find_all('span')
            str_ingrid = []
            for i in ingrid:
                if i.find('span') is None:
                    pass
                else:
                    str_ingrid.append(i.find('span').get_text(strip=True))
            arr_categ = []
            categ = item.find(class_='breadcrumbs').find_all('a')
            for c in categ:
                arr_categ.append(c.get_text())
            recipe.append({
                'name': item.find('h1').get_text(strip=True),
                'image': item.find('img').get('src'),
                'ingredients': str_ingrid,
                'link': url,
                'description': str_steps,
                'calories': item.find('p', class_='nutrition__weight').get_text(),
                'time_cooking': item.find('span', class_='prep-time').get_text(strip=True),
                'categories': arr_categ
            })
        print(recipe)
        return recipe

    def parse(self, list):
        for l in list:
            html = Crawler.get_html(Crawler(),l)
            if html.status_code == 200:
                self.get_content(html.text,l)
            else:
                print("error")

