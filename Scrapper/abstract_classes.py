from abc import ABC, abstractmethod, abstractproperty

class Crawler(ABC):

    @abstractmethod
    def get_html(self):
        print('as')

    @abstractmethod
    def get_recipes_links(self):
        pass

class Parser(ABC):

    @abstractmethod
    def get_steps(self, item):
        pass

    @abstractmethod
    def get_ingredients(self, item):
        pass

    @abstractmethod
    def get_categories(self, item):
        pass

    @abstractmethod
    def get_calories(self, soup):
        pass

    @abstractmethod
    def get_time(self, item):
        pass

    @abstractmethod
    def get_content(self, html, url):
        pass

    @abstractmethod
    def get_image(self, item):
        pass

    @abstractmethod
    def download_image(self, img_url, path):
        pass
