import requests as req
from bs4 import BeautifulSoup
from abstract_classes import Crawler


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


if __name__ == '__main__':
    a = CrawlerTvoirecepty()
#    links = a.get_recipes_links()
 #   for i in links:
  #      print(i)
   # print(len(links))
