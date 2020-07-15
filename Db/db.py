import sqlite3
from collections import Counter
from sqlite3 import Error
import model.recipe
from urllib.request import urlretrieve
import urllib
import sys


class SqliteRecipes:
    def __init__(self):
        self.connection = self.create_connection("../Db/database.db")
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_connection(self, path):
        connection = None
        try:
            connection = sqlite3.connect(path)
            print("Connection to SQLite DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")

        return connection

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("Query executed successfully")
        except Error as e:
            print(f"The error '{e}' occurred")

    def execute_query_with_value(self, query, value):
        try:
            self.cursor.execute(query, value)
            self.connection.commit()
            print("Query executed successfully")
        except Error as e:
            print(f"The error '{e}' occurred")

    def create_tables(self):
        self.execute_query(self.create_users_table)
        self.execute_query(self.create_products_table)
        self.execute_query(self.create_recipes_table)
        self.execute_query(self.create_ingredients_table)
        self.execute_query(self.create_favourites_table)
        self.execute_query(self.create_categories_table)
        self.execute_query(self.create_categ_of_rec_table)
        self.execute_query(self.create_history_table)

    def add_product(self, product):
        args = (product,)
        self.execute_query_with_value(self.insert_new_product, args)
        self.connection.commit()

    def add_category(self, category):
        args = (category,)
        self.execute_query_with_value(self.insert_new_category, args)
        self.connection.commit()

    def add_user(self, user):
        args = (user,)
        cursor = self.connection.cursor()
        cursor.execute(self.find_exist_user, args)
        row = cursor.fetchone()
        if row is None:
            self.execute_query_with_value(self.insert_new_user, args)
            self.connection.commit()

    def add_recipe(self, recipe):
        path = self.get_img_path(recipe.image)
        image = self.download_image(recipe.image, path )
        recipe.image = path
        image = self.convert_image(recipe.image)
        self.connection.executemany(self.insert_new_recipe, ((recipe.name, image, recipe.description,
                                                              recipe.link, recipe.calories, recipe.time_cooking),))
        self.add_ingredients(recipe.ingredients)
        self.add_categories(recipe.categories)
        self.connection.commit()

    def get_img_path(self, link):
        elements = link.split('/')
        name = elements[-1]
        print(f'C:\\Users\\vertn\\Desktop\\images\\{name}')
        return f'C:\\Users\\vertn\\Desktop\\images\\{name}'

    def add_ingredients(self, ingr_list):
        self.execute_query(self.find_recept_id)
        r_id = int(str(self.cursor.fetchone())[1:-2])
        for i in ingr_list:
            self.cursor.execute(self.find_exist_products, (i,))
            row = self.cursor.fetchone()
            if row is None:
                self.add_product(i)
            self.execute_query_with_value(self.find_ing_id, (i,))
            ing_id = int(str(self.cursor.fetchone())[1:-2])
            args = (r_id, ing_id)
            self.execute_query_with_value(self.insert_ingredient_to_recipe, args)

    def add_categories(self, ceteg_list):
        self.execute_query(self.find_recept_id)
        r_id = int(str(self.cursor.fetchone())[1:-2])
        for c in ceteg_list:
            self.cursor.execute(self.find_exist_category, (c,))
            row = self.cursor.fetchone()
            if row is None:
                self.add_category(c)
            self.execute_query_with_value(self.find_categ_id, (c,))
            categ_id = int(str(self.cursor.fetchone())[1:-2])
            args = (str(r_id), str(categ_id))
            self.execute_query_with_value(self.insert_categoty_to_recipe, args)

    def bot_find_recipes(self, user_id, str_ing=None, str_filt=None):
        filt_res = []
        ing_res = []
        if str_filt is not None:
            filters_list = str_filt.split(', ')
            filt_res = self.bot_select_by_category(filters_list)
        if str_ing is not None:
            ing_list = str_ing.split(', ')
            ing_res = self.bot_select_by_ingredients(ing_list)
        self.add_to_history(user_id, str_ing, str_filt)
        self.connection.commit()
        if str_ing is not None and str_filt is not None:
            final_result = list((Counter(ing_res) & Counter(filt_res)).elements())
            print(final_result)
            return final_result
        if str_ing is None and str_filt is None:
            return []
        if str_ing is not None:
            print(ing_res)
            return ing_res
        else:
            print(filt_res)
            return filt_res

    def find_with_categories(self, elem):
        self.execute_query_with_value("""SELECT distinct c1.rec_id FROM categories_of_recipes c1 
                            join categories c2 on c1.c_id = c2.c_id and c2.c_name LIKE ?""", (elem,))
        return self.cursor.fetchall()

    def bot_select_by_category(self, categ_list):
        final_result = self.find_with_categories(categ_list[0])
        if len(categ_list) != 1:
            for categ in categ_list:
                res = self.find_with_categories(categ)
                final_result = list((Counter(res) & Counter(final_result)).elements())
        for i in final_result:
            final_result.remove(i)
            i = i[0]
            final_result.insert(0, i)
        return final_result

    def find_with_ingredients(self, elem):
        self.execute_query_with_value("""SELECT distinct c1.rec_id FROM ingredients c1 
                            join products c2 on c1.pr_id = c2.pr_id and c2.pr_name LIKE ?""", (elem,))
        return self.cursor.fetchall()

    def bot_select_by_ingredients(self, ingr_list):
        final_result = self.find_with_ingredients(ingr_list[0])
        if len(ingr_list) != 1:
            for ingr in ingr_list:
                res = self.find_with_ingredients(ingr)
                final_result = list((Counter(res) & Counter(final_result)).elements())
        for i in final_result:
            final_result.remove(i)
            i = i[0]
            final_result.insert(0, i)
        return final_result

    def bot_show_hisrory(self, user_id):
        self.execute_query_with_value("""select * from history where user_id like ?""", (user_id,))

    def add_to_history(self, user_id, products, categories):
        self.execute_query_with_value("""insert into history (user_id, products, categories, date_of_adding) 
        values(?,?,?,?);""", (user_id, products, categories, self.date_now()))

    def bot_show_categories(self):
        self.execute_query("""select * from categories;""")

    def bot_show_favourites(self, user_id):
        self.execute_query_with_value("""select * from favourites where user_id like ?""", (user_id,))

    def bot_add_favourite(self, user_id, rec_id):
        self.cursor.execute("""select * from favourites where user_id like ? and rec_id = ?""",
                            (user_id, str(rec_id)))
        row = self.cursor.fetchone()
        if row is None:
            self.execute_query_with_value(
                """insert into favourites(rec_id, user_id, date_of_adding) values(?, ?, ?);""",
                (rec_id, user_id, self.date_now()))

    def date_now(self):
        self.execute_query("""SELECT date('now');""")
        return str(self.cursor.fetchone())[1:-2]

    def bot_delete_favourite(self, user_id, rec_id):
        self.execute_query_with_value("""delete from favourites where user_id like ? and rec_id = ?""",
                                      (user_id, rec_id))

    def bot_make_user_admin(self, user_id):
        self.execute_query_with_value("""UPDATE users SET user_admin = TRUE WHERE user_id like ? """, (user_id,))

    def bot_delete_user_admin(self, user_id):
        self.execute_query_with_value("""UPDATE users SET user_admin = FALSE WHERE user_id like ? """, (user_id,))

    def read_image(self, img_path):

        try:
            er = 1
            fin = open(img_path, "rb")
            er = 2
            img = fin.read()
            print('картинку считали')
            return img

        except IOError:
            print("Error")
            print(er)
            sys.exit(1)

        finally:
            if fin:
                fin.close()

    def convert_image(self, img_path):
        data = self.read_image(img_path)
        binary = sqlite3.Binary(data)
        return binary

    def download_image(self, img_url, path):
        urllib.parse.quote(':')
        return urlretrieve(img_url, path)

    create_products_table = """
    CREATE TABLE IF NOT EXISTS products (
      pr_id INTEGER PRIMARY KEY AUTOINCREMENT,
      pr_name TEXT NOT NULL
    );
    """

    create_categories_table = """
       CREATE TABLE IF NOT EXISTS categories (
         c_id INTEGER PRIMARY KEY AUTOINCREMENT,
         c_name TEXT NOT NULL
       );
       """

    create_recipes_table = """
    CREATE TABLE IF NOT EXISTS recipes (
      rec_id INTEGER PRIMARY KEY AUTOINCREMENT,
      rec_name TEXT NOT NULL,
      rec_image BLOB NOT NULL,
      recipe TEXT NOT NULL,
      rec_link TEXT,
      rec_calories,
      rec_time TEXT
    );
    """

    create_ingredients_table = """
    CREATE TABLE IF NOT EXISTS ingredients (
       rec_id INTEGER NOT NULL,
       pr_id INTEGER NOT NULL,
       FOREIGN KEY (rec_id) REFERENCES recipes(rec_id),
       FOREIGN KEY (pr_id) REFERENCES products(pr_id)
    );
    """

    create_users_table = """
       CREATE TABLE IF NOT EXISTS users (
         user_id TEXT PRIMARY KEY,
         user_admin BOOLEAN NOT NULL,
         date_of_adding DATE NOT NULL
       );
       """

    create_history_table = """
       CREATE TABLE IF NOT EXISTS history (
         user_id TEXT NOT NULL,
         products TEXT,
         categories TEXT,
         date_of_adding DATE NOT NULL,
         FOREIGN KEY (user_id) REFERENCES users(user_id)
       );
       """

    create_favourites_table = """
        CREATE TABLE IF NOT EXISTS favourites (
           rec_id INTEGER NOT NULL,
           user_id INTEGER NOT NULL,
           date_of_adding DATE NOT NULL,
           FOREIGN KEY (rec_id) REFERENCES recipes(rec_id),
           FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        """

    create_categ_of_rec_table = """
       CREATE TABLE IF NOT EXISTS categories_of_recipes (
          rec_id INTEGER NOT NULL,
          c_id INTEGER NOT NULL,
          FOREIGN KEY (rec_id) REFERENCES recipes(rec_id),
          FOREIGN KEY (c_id) REFERENCES categories(c_id)
       );
       """

    insert_new_product = """
    insert into products(pr_name) values(?);
    """

    insert_new_category = """
       insert into categories(c_name) values(?);
       """

    insert_new_user = """
       insert into users(user_id, user_admin, date_of_adding) values(?, FALSE, date('now'));
       """

    delete_user = """
        delete from users where user_id = ?
    """

    insert_new_recipe = """
    insert into recipes(rec_name, rec_image, recipe, rec_link, rec_calories, rec_time) 
    values(?,?,?,?,?,?);
    """

    insert_ingredient_to_recipe = """
    insert into ingredients(rec_id, pr_id)
    values(?, ?);
    """

    insert_categoty_to_recipe = """
    insert into categories_of_recipes(rec_id, c_id)
    values(?,?);
    """

    find_exist_products = """
    select pr_id from products where pr_name = ?;
    """

    find_exist_category = """
    select * from categories where c_name = ?;
    """

    find_exist_user = """
    select * from users where user_id = ?;
    """

    find_recept_id = """
    select max(rec_id) from recipes;
    """

    find_ing_id = """
    select pr_id from products where pr_name = ?;
    """

    find_categ_id = """
    select c_id from categories where c_name = ?;
    """

    find_rec_filter = """
    select * from recipes r
    join categories_of_recipes c on r.rec_id = c.rec_id
    and c.c_id = ?;   
    """

if __name__ == '__main__':
    db = SqliteRecipes()
    rec = model.recipe.Recipe('Блинчики', r"../photos/43LlEln7bzo.jpg", ['яйца', 'мука', 'молоко', 'сахар', 'соль'],
                              'http:\\eda.ru', 'все смешать и на сковороду', '200', '30 минут', ['масленица',
                                                                                                 'на сковороде'])
    rec2 = model.recipe.Recipe('Оладушки с шоколадом', r"../photos/UxXWRfrboy4.jpg",
                               ['яйца', 'мука', 'кефир', 'сахар', 'шоколад',
                                'масло подсолнечное'], 'http:\\eda.ru',
                               'все смешать и на сковороду пуньк-пуньк', '300',
                               '10 минут', ['быстрые рецепты', 'на сковороде', 'завтрак'])
    rec4 = model.recipe.Recipe('Тохгхтик ням-ням', r"../photos/43LlEln7bzo.jpg",
                               ['яйца', 'мука', 'молоко', 'сахар', 'сгущеное молоко', 'орехи'],
                               'http:\\eda.ru', 'тяп-ляп и готово', '700', '31 час', ['десерты', 'торты', 'день рождения'])

# db.add_recipe(rec)
# db.add_recipe(rec2)
# db.add_recipe(rec4)
# db.add_user('14g9ok8')
# db.add_user('668ud9')
# db.bot_make_user_admin('14g9ok8')
# db.bot_delete_favourite('668ud9', 2)
# db.bot_add_favourite('668ud9', 1)
# print(db.date_now())
# db.bot_find_recipes('668ud9', 'яйца, мука','масленица')
# db.download_image('https://eda.ru/img/eda/c620x415i/s2.eda.ru/StaticContent/Photos/120213175531/180415114517/p_O.jpg', r'тут путь сохранения')
#db.bot_select_by_category(['завтрак', 'на сковороде'])
#db.bot_select_by_ingredients(['мука','яйца','шоколад'])
db.bot_find_recipes('668ud9','мука, яйца', 'завтрак')
db.bot_find_recipes('668ud9','мука, яйца',None)
db.bot_find_recipes('668ud9',None,'день рождения')
