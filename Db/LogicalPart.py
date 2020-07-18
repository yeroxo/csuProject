from collections import Counter
import model.recipe
from Db.db import SqliteRecipes as DataBase


class LogicalPart:
    def __init__(self):
        self.db = DataBase()

    def bot_find_recipes(self, user_id, ingr_diff_num, str_ing=None, str_filt=None):
        filt_res = []
        ing_res = []
        if str_filt is not None:
            filters_list = str_filt.split(', ')
            filt_res = self.select_by_category(filters_list)

        if str_ing is not None:
            ing_list = str_ing.split(', ')
            ing_res = self.select_by_ingredients(ing_list)

        self.add_to_history(user_id, str_ing, str_filt)
        self.db.connection.commit()
        if str_ing is not None and str_filt is not None:
            result = list((Counter(ing_res) & Counter(filt_res)).elements())
        elif str_ing is None and str_filt is None:
            result = []
        elif str_ing is not None:
            result = ing_res
        else:
            result = filt_res

        if ingr_diff_num != -1:
            result = self.find_recipe_without_diff(ingr_diff_num, len(ing_res), result)
        print(result)
        final_result = []
        for r in result:
            final_result.append(self.make_recipe_object(r))
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
            self.db.connection.execute("""select count(pr_id) from ingredients 
                                                                   where rec_id = ?;""", (rec,))
            rec_ingr = self.db.cursor.fetchone()
            if rec_ingr[0] - ingr_num > diff_num:
                result.append(rec)
        return result

    def bot_find_recipes_by_name(self, str_name):
        recipes = self.db.cursor.execute("""select * from recipes 
                                                   where rec_name like ?""", (str_name,))
        result = []
        for r in recipes:
            result.append(self.make_recipe_object(r))
        return result

    def bot_find_recipes_by_ingredients(self, ingr_list):
        recipes = self.select_by_ingredients(ingr_list)
        result = []
        for r in recipes:
            result.append(self.make_recipe_object(r))
        return result

    def bot_find_recipes_by_categories(self, categ_list):
        recipes = self.select_by_category(categ_list)
        result = []
        for r in recipes:
            result.append(self.make_recipe_object(r))
            print(r)
        return result

    def sql_find_with_categories(self, elem):
        self.db.cursor.execute("""SELECT distinct c1.rec_id FROM categories_of_recipes c1 
                               join categories c2 on c1.c_id = c2.c_id and c2.c_name LIKE ?""", (elem,))
        return self.db.cursor.fetchall()

    def select_by_category(self, categ_list):
        final_result = self.sql_find_with_categories(categ_list[0])
        if len(categ_list) != 1:
            for categ in categ_list:
                res = self.sql_find_with_categories(categ)
                final_result = list((Counter(res) & Counter(final_result)).elements())
        for i in final_result:
            final_result.remove(i)
            i = i[0]
            final_result.insert(0, i)
        return final_result

    def sql_find_with_ingredients(self, elem):
        self.db.cursor.execute("""SELECT distinct c1.rec_id FROM ingredients c1 
                               join products c2 on c1.pr_id = c2.pr_id and c2.pr_name LIKE ?""", (elem,))
        return self.db.cursor.fetchall()

    def select_by_ingredients(self, ingr_list):
        final_result = self.sql_find_with_ingredients(ingr_list[0])
        if len(ingr_list) != 1:
            for ingr in ingr_list:
                res = self.sql_find_with_ingredients(ingr)
                final_result = list((Counter(res) & Counter(final_result)).elements())
        for i in final_result:
            final_result.remove(i)
            i = i[0]
            final_result.insert(0, i)
        return final_result

    def make_recipe_object(self, rec_id):
        name = str(self.db.cursor.execute(
            """select rec_name from recipes where rec_id = ?;""",
            (rec_id,)).fetchone())[1:-2]
        # нужно как-то раскодировать изображение
        image = str(self.db.cursor.execute(
            """select rec_image from recipes where rec_id = ?;""",
            (rec_id,)).fetchone())[1:-2]
        ingredients = self.db.cursor.execute(
            """select pr_name from products p 
         join ingredients i on i.pr_id=p.pr_id 
         and i.rec_id = ?;""", (rec_id,)).fetchall()
        ingr = []
        for i in ingredients:
            i = str(i)[2:-3]
            ingr.append(i)
        link = str(self.db.cursor.execute(
            """select rec_link from recipes where rec_id = ?;""",
            (rec_id,)).fetchone())[1:-2]
        description = str(self.db.cursor.execute(
            """select recipe from recipes where rec_id = ?;""",
            (rec_id,)).fetchone())[1:-2]
        calories = str(self.db.cursor.execute(
            """select rec_calories from recipes where rec_id = ?;""",
            (rec_id,)).fetchone())[1:-2]
        time_cooking = str(self.db.cursor.execute(
            """select rec_time from recipes where rec_id = ?;""",
            (rec_id,)).fetchone())[1:-2]
        categories = self.db.cursor.execute(
            """select c_name from categories c
         join categories_of_recipes i on i.c_id=c.c_id 
         and i.rec_id = ?;""", (rec_id,)).fetchall()
        categ = []
        for i in categories:
            i = str(i)[2:-3]
            categ.append(i)
        return model.recipe.Recipe(name, image, ingr, link, description, calories, time_cooking, categ)

    def bot_get_history(self, user_id):
        self.db.cursor.execute("""select * from history where user_id like ?""", (user_id,))

    def add_to_history(self, user_id, products, categories):
        self.db.cursor.execute("""insert into history (user_id, products, categories, date_of_adding) 
           values(?,?,?,?);""", (user_id, products, categories, self.date_now()))

    def bot_get_categories(self):
        self.db.cursor.execute("""select * from categories;""")

    def bot_get_favourites(self, user_id):
        self.db.cursor.execute("""select * from favourites where user_id like ?""", (user_id,))

    def bot_add_favourite(self, user_id, rec_id):
        self.db.cursor.execute("""select * from favourites where user_id like ? and rec_id = ?""",
                               (user_id, str(rec_id)))
        row = self.db.cursor.fetchone()
        if row is None:
            self.db.cursor.execute(
                """insert into favourites(rec_id, user_id, date_of_adding) values(?, ?, ?);""",
                (rec_id, user_id, self.date_now()))

    def bot_delete_favourite(self, user_id, rec_id):
        self.db.execute_query_with_value("""delete from favourites where user_id like ? and rec_id = ?""",
                                      (user_id, rec_id))

    def date_now(self):
        self.db.connection.execute("""SELECT date('now');""")
        return str(self.db.cursor.fetchone())[1:-2]

    def bot_make_user_admin(self, user_login):
        self.db.cursor.execute("""UPDATE users SET user_admin = TRUE WHERE user_login like ? """, (user_login,))

    def bot_delete_user_admin(self, user_login):
        self.db.cursor.execute("""UPDATE users SET user_admin = FALSE WHERE user_login like ? """, (user_login,))

# lg = LogicalPart()
# lg.bot_find_recipes_by_categories('завтрак')
# lg.bot_find_recipes_by_name('Торт')
# lg.sql_find_with_ingredients('мука')