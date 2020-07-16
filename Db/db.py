import sqlite3
from collections import Counter
from sqlite3 import Error
import model.recipe
from urllib.request import urlretrieve
import urllib
import sys
import model.recipe


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
        self.execute_query_with_value("""insert into products(pr_name) values(?);""", args)
        self.connection.commit()

    def add_category(self, category):
        args = (category,)
        self.execute_query_with_value("""insert into categories(c_name) values(?);""", args)
        self.connection.commit()

    def add_user(self, user_id, user_login):
        args = (user_id,)
        cursor = self.connection.cursor()
        cursor.execute("""select * from users where user_id = ?;""", args)
        row = cursor.fetchone()
        if row is None:
            self.connection.execute(self.insert_new_user, (user_id, user_login))
            self.connection.commit()

    def add_recipe(self, recipe):
        path = self.get_img_path(recipe.image)
        image = self.download_image(recipe.image, path)
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
        print(f'../photos/{name}')
        return f'../photos/{name}'

    def add_ingredients(self, ingr_list):
        self.execute_query(self.find_recept_id)
        r_id = int(str(self.cursor.fetchone())[1:-2])
        for i in ingr_list:
            self.cursor.execute("""select pr_id from products where pr_name = ?;""", (i,))
            row = self.cursor.fetchone()
            if row is None:
                self.add_product(i)
            self.execute_query_with_value("""select pr_id from products where pr_name = ?;""", (i,))
            ing_id = int(str(self.cursor.fetchone())[1:-2])
            args = (r_id, ing_id)
            self.execute_query_with_value(self.insert_ingredient_to_recipe, args)

    def add_categories(self, ceteg_list):
        self.execute_query(self.find_recept_id)
        r_id = int(str(self.cursor.fetchone())[1:-2])
        for c in ceteg_list:
            self.cursor.execute("""select * from categories where c_name = ?;""", (c,))
            row = self.cursor.fetchone()
            if row is None:
                self.add_category(c)
            self.execute_query_with_value("""select c_id from categories where c_name = ?;""", (c,))
            categ_id = int(str(self.cursor.fetchone())[1:-2])
            args = (str(r_id), str(categ_id))
            self.execute_query_with_value(self.insert_categoty_to_recipe, args)

    """
    ingr_diff_num задается пользователем
    является разрешимым допущением в различии кол-ва ингредиентов в рецепте
    если пользователю пофиг - равен -1
    """

    def bot_find_recipes(self, user_id, ingr_diff_num, str_ing=None, str_filt=None):
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
        elif str_ing is None and str_filt is None:
            return []
        elif str_ing is not None:
            final_result = ing_res
        else:
            return filt_res

        if ingr_diff_num != -1:
            final_result = self.find_recipe_without_diff(ingr_diff_num, len(ing_res), final_result)
        print(final_result)
        return final_result

    """
    в методе find_recipe_without_diff diff_num - разрешимая разница в количестве ингредиентов
    ingr_num - количество ингредиентов, введенных пользователем
    если разница между введенным пользователем количеством и суммой ингредиентов в рецепте 
    меньше diff_num, то принимаем рецепт
    """

    def find_recipe_without_diff(self, diff_num, ingr_num, recipes_list):
        result = []
        for rec in recipes_list:
            self.execute_query_with_value("""select count(pr_id) from ingredients 
                                                                where rec_id = ?;""", (rec,))
            rec_ingr = self.cursor.fetchone()
            if rec_ingr - ingr_num > diff_num:
                result.append(rec)
        return result

    def bot_find_recipes_by_name(self, str_name):
        self.execute_query_with_value("""select * from recipes 
                                                where rec_name like ?""", (str_name,))

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

    def bot_find_recipes_by_ingredients(self, ingr_list):
        recipes = self.bot_select_by_ingredients(ingr_list)
        result = []
        for r in recipes:
            result.append(self.make_recipe_object(r))
        return result

    def bot_find_recipes_by_categories(self, categ_list):
        recipes = self.bot_select_by_category(categ_list)
        result = []
        for r in recipes:
            result.append(self.make_recipe_object(r))
        return result

    def make_recipe_object(self, rec_id):
        name = str(self.cursor.execute(
            """select rec_name from recipes where rec_id = ?;""",
            (rec_id,)).fetchone())[1:-2]
        # нужно как-то раскодировать изображение
        image = str(self.cursor.execute(
            """select rec_image from recipes where rec_id = ?;""",
            (rec_id,)).fetchone())[1:-2]
        ingredients = self.cursor.execute(
            """select pr_name from products p 
         join ingredients i on i.pr_id=p.pr_id 
         and i.rec_id = ?;""", (rec_id,)).fetchall()
        ingr = []
        for i in ingredients:
             i = str(i)[2:-3]
             ingr.append(i)
        link = str(self.cursor.execute(
            """select rec_link from recipes where rec_id = ?;""",
            (rec_id,)).fetchone())[1:-2]
        description = str(self.cursor.execute(
            """select recipe from recipes where rec_id = ?;""",
            (rec_id,)).fetchone())[1:-2]
        calories = str(self.cursor.execute(
            """select rec_calories from recipes where rec_id = ?;""",
            (rec_id,)).fetchone())[1:-2]
        time_cooking = str(self.cursor.execute(
            """select rec_time from recipes where rec_id = ?;""",
            (rec_id,)).fetchone())[1:-2]
        categories = self.cursor.execute(
            """select c_name from categories c
         join categories_of_recipes i on i.c_id=c.c_id 
         and i.rec_id = ?;""", (rec_id,)).fetchall()
        categ = []
        for i in categories:
             i = str(i)[2:-3]
             categ.append(i)
        return model.recipe.Recipe(name, image, ingr, link, description, calories, time_cooking, categ)

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
         user_login TEXT NOT NULL,
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

    insert_new_user = """
       insert into users(user_id, user_login, user_admin, date_of_adding) values(?, ?, FALSE, date('now'));
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

    find_recept_id = """
    select max(rec_id) from recipes;
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
                               'http:\\eda.ru', 'тяп-ляп и готово', '700', '31 час',
                               ['десерты', 'торты', 'день рождения'])
