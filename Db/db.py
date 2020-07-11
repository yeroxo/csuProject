import sqlite3
from sqlite3 import Error


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")


def execute_query_with_value(connection, query, value):
    cursor = connection.cursor()
    try:
        cursor.execute(query, value)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


connection = create_connection("D:\\sqlite\example.db")


def add_product(product):
    cursor = connection.cursor()
    cursor.execute(find_exist_products, (product))
    row = cursor.fetchone()
    if row is None:
        execute_query_with_value(connection, insert_new_product, product)
        connection.commit()


def add_recipe(recipe):
    connection.commit()


create_products_table = """
CREATE TABLE IF NOT EXISTS products (
  pr_id INTEGER PRIMARY KEY AUTOINCREMENT,
  pr_name TEXT NOT NULL
);
"""

create_recipes_table = """
CREATE TABLE IF NOT EXISTS recipes (
  rec_id INTEGER PRIMARY KEY AUTOINCREMENT,
  rec_name TEXT NOT NULL,
  recipe TEXT NOT NULL,
  food_type TEXT,
  time TEXT,
  geography TEXT,
  diet TEXT
);
"""

create_ingredients_table = """
CREATE TABLE IF NOT EXISTS ingredients (
   rec_id INTEGER NOT NULL,
   pr_id INTEGER NOT NULL
);
"""

insert_new_product = """
insert into products(pr_name) values(?);
"""

find_exist_products = """
SELECT * FROM products WHERE (pr_name IS ?) 
"""

insert_new_recipe = """
insert into recipes(rec_name, recipe, food_type, time, geography, diet) 
values(?,?,?,?,?,?);
"""

insert_ingredient_to_recipe = """
insert into ingredients(rec_id, pr_id)
values(?,?);
"""