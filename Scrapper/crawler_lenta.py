from selenium import webdriver
import time
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import requests as req
import random
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError
from requests.exceptions import Timeout
if __name__ == '__main__':
    from selenium import webdriver
    import time
    from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    import time
    import requests as req
    import random
    from requests.adapters import HTTPAdapter
    from requests.exceptions import ConnectionError
    from requests.exceptions import Timeout

    chromedriver = "C:/Users/vertn/Downloads/chromedriver_win32 (1)/chromedriver.exe"
    driver = webdriver.Chrome(executable_path=chromedriver)
    wait = WebDriverWait(driver, 60)
    driver.get('https://lenta.com/recepty/catalog-recepty/')
    basebutton = driver.find_element_by_class_name('spinner-lock')
    links = []

    try:
        while True:
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//div[@class = 'recipe-catalog__pagination recipe-pagination']//button")))
            button = basebutton.find_element_by_xpath("//div[@class = 'recipe-catalog__pagination recipe-pagination']//button")
            if button.text == 'Показать ещё':
                button.click()
    except TimeoutException:
        linkss = driver.find_elements_by_class_name('recipe-grid__item')
        for i in linkss:
            link = i.find_element_by_tag_name('a').get_attribute('href')
            links.append(link)
        print(len(links))

class CrawlerLenta:
    def __init__(self):
        self.links = []
        self.url = 'https://lenta.com/recepty/catalog-recepty/'
        self.headers = {'user-agent':
                            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 '
                            'YaBrowser/20.7.0.899 Yowser/2.5 Yptp/1.23 Safari/537.36',
                        'accept': '*/*'}

    def get_selenium_html(self, url, params=None):
        chromedriver = "C:/Users/vertn/Downloads/chromedriver_win32 (1)/chromedriver.exe"
        driver = webdriver.Chrome(executable_path=chromedriver)
        wait = WebDriverWait(driver, 60)
        driver.get(url)
        return driver

    def getHeader(self):
        list_of_headers = ['Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.0.1) Gecko/20060111 Firefox/1.5.0.1',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US)',
                           'Opera/9.0 (Windows NT 5.1; U; en)',
                           'Opera/9.00 (Nintendo Wii; U; ; 1309-9; en)',
                           'Opera/9.00 (Wii; U; ; 1038-58; Wii Shop Channel/1.0; en)',
                           'Mozilla/2.0 (compatible; MSIE 3.01; Windows 98)',
                           'Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0)']

        return random.choice(list_of_headers)

    def getProxy(self):
        proxies = ['85.12.221.147:80',
                   '46.101.113.185:80',
                   '212.220.216.70:8080',
                   '188.170.233.110:3128',
                   '178.62.223.104:80'
                   ]
        return random.choice(proxies)

    def get_html(self, url, header=True, timeout=5, proxy=True, retries=3):
        session = req.session()

        if header:
            header = {}
            header['User-agent'] = self.getHeader()
            session.headers = header

        session.timeout = timeout

        adapter = HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        if proxy:
            proxy = self.getProxy()
            session.proxies = {'http': proxy}

        try:
            html = session.get(url)
            return html
        except ConnectionError:
            print(f'Something went wrong with this connection. Url - {url}')
        except Timeout:
            print(f'Waiting time is up. Url - {url}')



    def get_recipes_links(self):
        basebutton = driver.find_element_by_class_name('spinner-lock')
        links = []
        html = self.get_selenium_html(self.url)
        try:
            while True:
                wait.until(EC.visibility_of_element_located(
                    (By.XPATH, "//div[@class = 'recipe-catalog__pagination recipe-pagination']//button")))
                button = basebutton.find_element_by_xpath(
                    "//div[@class = 'recipe-catalog__pagination recipe-pagination']//button")
                if button.text == 'Показать ещё':
                    button.click()
        except TimeoutException:
            linkss = driver.find_elements_by_class_name('recipe-grid__item')
            for i in linkss:
                link = i.find_element_by_tag_name('a').get_attribute('href')
                links.append(link)
        return links


