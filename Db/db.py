import sqlite3
from sqlite3 import Error


class SqliteRecipes:
    def __init__(self, path):
        self.connection = self.create_connection(path)
        self.cursor = self.connection.cursor()

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

    def add_product(self, product):
        self.execute_query_with_value(self.insert_new_product, product)
        self.connection.commit()

    def add_category(self, category):
        self.execute_query_with_value(self.insert_new_category, category)
        self.connection.commit()

    def add_user(self, user):
        cursor = self.connection.cursor()
        cursor.execute(self.find_exist_user, user)
        row = cursor.fetchone()
        if row is None:
            self.execute_query_with_value(self.insert_new_user, user)
            self.connection.commit()

    def add_recipe(self, recipe):
        self.connection.executemany(self.insert_new_recipe, (recipe.name, recipe.image, recipe.description,
                                                             recipe.link, recipe.calories, recipe.time_cooking))
        self.add_ingredients(recipe)
        self.add_categories(recipe)
        self.connection.commit()

    def add_ingredients(self, recipe):
        for i in recipe.ingredients:
            self.cursor.execute(self.find_exist_products, i)
            row = self.cursor.fetchone()
            if row is None:
                self.add_product(i)
            self.execute_query_with_value(self.insert_ingredient_to_recipe,
                                          (self.execute_query(self.find_recept_id),
                                           self.execute_query_with_value(self.find_ing_id, i)))

    def add_categories(self, recipe):
        for c in recipe.categories:
            self.cursor.execute(self.find_exist_category, c)
            row = self.cursor.fetchone()
            if row is None:
                self.add_category(c)
            self.execute_query_with_value(self.insert_categoty_to_recipe,
                                          (self.execute_query(self.find_recept_id),
                                           self.execute_query_with_value(self.find_categ_id, c)))

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
    values(?,?);
    """

    insert_categoty_to_recipe = """
    insert into categories(rec_id, c_id)
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
    select * from ingredients where ing_name = ?;
    """

    find_categ_id = """
    select * from categories where c_name = ?;
    """


db = SqliteRecipes("D:\\sqlite\example2.db")
db.execute_query(db.create_users_table)
db.execute_query(db.create_products_table)
db.execute_query(db.create_recipes_table)
db.execute_query(db.create_favourites_table)
db.execute_query(db.create_categories_table)
db.execute_query(db.create_categ_of_rec_table)
db.execute_query(db.create_ingredients_table)
