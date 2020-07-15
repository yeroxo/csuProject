from Db.db import SqliteRecipes

from Scrapper.crawler_tvoirecepty import CrawlerTvoirecepty
from Scrapper.parser_tvoirecepty import ParserTvoirecepty


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
                rec = parser.get_content(html.text, l)
                self.db.add_recipe(rec)
            else:
                print("error")


c = Scrapper()
c.parse_site(CrawlerTvoirecepty(), ParserTvoirecepty())
c.parse_site(CrawlerTvoirecepty(), ParserTvoirecepty())
