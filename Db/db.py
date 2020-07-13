import sqlite3
from sqlite3 import Error
import model.recipe


class SqliteRecipes:
    def __init__(self, path):
        self.connection = self.create_connection(path)
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

    def execute_read_query(self, query):
        result = None
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
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
        cursor.execute(self.find_exist_user, user)
        row = cursor.fetchone()
        if row is None:
            self.execute_query_with_value(self.insert_new_user, args)
            self.connection.commit()

    def add_recipe(self, recipe):
        self.connection.executemany(self.insert_new_recipe, ((recipe.name, recipe.image, recipe.description,
                                                              recipe.link, recipe.calories, recipe.time_cooking),))
        self.add_ingredients(recipe.ingredients)
        self.add_categories(recipe.categories)
        self.connection.commit()

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
            print(ing_id)
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

    def find_recipes(self, str_ing, filters_list=None):

        pass

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
      rec_calories TEXT,
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
         user_id INTEGER PRIMARY KEY,
         user_admin BOOLEAN NOT NULL
       );
       """

    create_favourites_table = """
        CREATE TABLE IF NOT EXISTS favourites (
           rec_id INTEGER NOT NULL,
           user_id INTEGER NOT NULL,
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
       insert into users(user_id, user_admin) values(?, FALSE);
       """

    delete_user = """
        delete from users where user_id = ?
    """

    insert_new_favourite = """
       insert into favourites(rec_id, user_id) values(?, ?);
       """

    delete_favourite = """
           delete from favourites 
           where user_id = ? and rec_id = ?
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
    select * from products where pr_name = ?;
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


db = SqliteRecipes("D:\\sqlite\example2.db")
rec = model.recipe.Recipe('Блинчики', 'img.jpg', ['яйца', 'мука', 'молоко', 'сахар', 'соль'],
                          'http:\\eda.ru', 'все смешать и на сковороду', '200', '30 минут', ['масленица',
                                                                                             'на сковороде'])
rec2 = model.recipe.Recipe('Оладушки с шоколадом', 'img2.jpg', ['яйца', 'мука', 'кефир', 'сахар', 'шоколад',
                                                                'масло подсолнечное'], 'http:\\eda.ru',
                           'все смешать и на сковороду пуньк-пуньк', '300',
                           '10 минут', ['быстрые рецепты', 'на сковороде', 'завтрак'])
#db.add_recipe(rec)
#db.add_recipe(rec2)
#db.execute_query_with_value(db.find_rec_filter, (3,))