import requests as req
from bs4 import BeautifulSoup
#%%
links = []
session = req.session()
url = 'https://tvoirecepty.ru/recepty?page='
for page in range(1,5):
    url_page = url + str(page)
    html = session.get(url_page).text
    soup = BeautifulSoup(html, 'lxml')
    recipes = soup.find_all('div', class_ = 'details product-description')
    for recipe in recipes:
        linkk = recipe.find('a').get('href')
        links.append('https://tvoirecepty.ru' + linkk)
for i in links:
    print(i)
print(len(links))

