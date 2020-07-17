from Db.db import SqliteRecipes

from Scrapper.crawler_tvoirecepty import CrawlerTvoirecepty
from Scrapper.parser_tvoirecepty import ParserTvoirecepty
from Scrapper.eda_ru import CrawlerEdaRu
from Scrapper.eda_ru import ParserEdaRu
import model


class Scrapper:
    def __init__(self):
        self.sites = {}
        self.db = SqliteRecipes()

    def parse_site(self, crawler, parser):
        print(crawler)
        self.sites[crawler.url] = [crawler, parser]
        links = crawler.get_recipes_links()
        for l in links:
            html = crawler.get_html(l)
            if html.status_code == 200:
                rec_text = parser.get_content(html.text, l)
                rec = model.recipe.Recipe(rec_text.name, rec_text.image, rec_text.ingredients,
                                          rec_text.link, rec_text.description, rec_text.calories, rec_text.time_cooking,
                                          rec_text.categories)
                self.db.add_recipe(rec)
            else:
                print("error")


c = Scrapper()
# c.parse_site(CrawlerTvoirecepty(), ParserTvoirecepty())
#c.parse_site(CrawlerEdaRu(), ParserEdaRu())
