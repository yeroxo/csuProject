import sqlite3
from sqlite3 import Error
import model.recipe
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

    def add_recipe(self, recipe):
        image = self.convert_image(recipe.image)
        self.connection.executemany(self.insert_new_recipe, ((recipe.name, image, recipe.description,
                                                              recipe.link, recipe.calories, recipe.time_cooking),))
        self.add_ingredients(recipe.ingredients)
        self.add_categories(recipe.categories)
        self.connection.commit()

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

    def date_now(self):
        self.execute_query("""SELECT date('now');""")
        return str(self.cursor.fetchone())[1:-2]

    def read_image(self, img_path):

        try:
            er = 1
            fin = open(img_path, "rb")
            er = 2
            img = fin.read()
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
         user_root_admin BOOLEAN NOT NULL,
         date_of_adding DATE NOT NULL
       );
       """

    create_history_table = """
       CREATE TABLE IF NOT EXISTS history (
         user_id TEXT NOT NULL,
         name TEXT,
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
