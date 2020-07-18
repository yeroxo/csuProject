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

        self.add_to_history(user_id, None, str_ing, str_filt)
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

    def bot_find_recipes_by_name(self, user_id, str_name):
        recipes = self.db.cursor.execute("""select * from recipes 
                                                   where rec_name like ?""", (str_name,))
        result = []
        for r in recipes:
            result.append(self.make_recipe_object(r))
        self.add_to_history(user_id, str_name, None, None)
        return result

    def bot_find_recipes_by_ingredients(self, user_id, str_ing, ingr_diff_num):
        ing_list = str_ing.split(', ')
        recipes = self.select_by_ingredients(ing_list)
        result = []
        for r in recipes:
            result.append(self.make_recipe_object(r))
        if(ingr_diff_num!=-1):
            result = self.find_recipe_without_diff(ingr_diff_num, len(ing_list), result)
        self.add_to_history(user_id, None, str_ing, None)
        return result

    def bot_find_recipes_by_categories(self, user_id, str_categ):
        categ_list = str_categ.split(', ')
        recipes = self.select_by_category(categ_list)
        result = []
        for r in recipes:
            result.append(self.make_recipe_object(r))
            print(r)
        self.add_to_history(user_id, None, None, str_categ)
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
        return model.recipe.Recipe(name, image, ingr, link, description, calories, time_cooking, categ, rec_id)

    def bot_get_history(self, user_id):
        self.db.cursor.execute("""select * from history where user_id like ?""", (user_id,))
        return self.db.cursor.fetchall()

    def bot_get_new_users_week(self):
        s_date = self.date_now()
        res = []
        for i in range(7):
            self.db.cursor.execute("""select count(user_id) from users where date_of_adding = date(?)""", (s_date,))
            count = str(self.db.cursor.fetchone())[1:-2]
            res.append(count)
            self.db.cursor.execute("""select date(?,'-1 days');""",(s_date,))
            s_date = str(self.db.cursor.fetchone())[1:-2]
        return res

    def bot_get_new_users_month(self):
        s_date = self.date_now()
        res = []
        for i in range(30):
            self.db.cursor.execute("""select count(user_id) from users where date_of_adding = date(?)""", (s_date,))
            count = str(self.db.cursor.fetchone())[1:-2]
            res.append(count)
            self.db.cursor.execute("""select date(?,'-1 days');""", (s_date,))
            s_date = str(self.db.cursor.fetchone())[1:-2]
        return res

    def bot_get_active_users_week(self):
        s_date = self.date_now()
        res = []
        for i in range(7):
            self.db.cursor.execute("""select distinct count(user_id) from history where date_of_adding = date(?)""", (str(s_date),))
            count = str(self.db.cursor.fetchone())[1:-2]
            print(count)
            res.append(count)
            self.db.cursor.execute("""select date(?,'-1 days');""", (s_date,))
            s_date = str(self.db.cursor.fetchone())[1:-2]
        return res

    def bot_get_active_users_month(self):
        s_date = self.date_now()
        res = []
        for i in range(30):
            self.db.cursor.execute("""select distinct count(user_id) from history where date_of_adding = date(?)""", (str(s_date),))
            count = str(self.db.cursor.fetchone())[1:-2]
            print(count)
            res.append(count)
            self.db.cursor.execute("""select date(?,'-1 days');""", (s_date,))
            s_date = str(self.db.cursor.fetchone())[1:-2]
        return res

    def add_to_history(self, user_id, name, products, categories):
        self.db.cursor.execute("""insert into history (user_id, name, products, categories, date_of_adding) 
           values(?,?,?,?);""", (user_id, name, products, categories, self.date_now()))

    def bot_get_categories(self):
        self.db.cursor.execute("""select * from categories;""")

    def bot_get_favourites(self, user_id):
        self.db.cursor.execute("""select * from favourites where user_id like ?""", (user_id,))
        result = self.db.cursor.fetchall()
        if result:
            return result
        return None

    def bot_add_favourite(self, user_id, rec_id):
        self.db.cursor.execute("""select * from favourites where user_id like ? and rec_id = ?""",
                               (user_id, str(rec_id)))
        row = self.db.cursor.fetchone()
        if row is None:
            self.db.cursor.execute(
                """insert into favourites(rec_id, user_id, date_of_adding) values(?, ?, ?);""",
                (rec_id, user_id, self.date_now()))
            self.db.connection.commit()

    def bot_delete_favourite(self, user_id, rec_id):
        self.db.execute_query_with_value("""delete from favourites where user_id like ? and rec_id = ?""",
                                         (user_id, rec_id))

    def date_now(self):
        self.db.execute_query("""SELECT date('now');""")
        res = str(self.db.cursor.fetchone())[2:-3]
        return res

    def bot_make_user_admin(self, user_login):
        self.db.cursor.execute("""UPDATE users SET user_admin = TRUE WHERE user_login like ? """, (user_login,))

    def bot_make_user_root_admin(self, user_login):
        self.db.cursor.execute("""UPDATE users SET user_root_admin = TRUE WHERE user_login like ? """, (user_login,))

    def bot_delete_user_admin(self, user_login):
        self.db.cursor.execute("""UPDATE users SET user_admin = FALSE WHERE user_login like ? """, (user_login,))

    def bot_delete_user_root_admin(self, user_login):
        self.db.cursor.execute("""UPDATE users SET user_root_admin = FALSE WHERE user_login like ? """, (user_login,))

    def bot_add_user(self, user_id, user_login):
        args = (user_id,)
        cursor = self.db.connection.cursor()
        cursor.execute("""select * from users where user_id = ?;""", args)
        row = cursor.fetchone()
        if row is None:
            res = self.db.connection.execute(self.insert_new_user, (user_id, user_login))
            print(str(res))
            self.db.connection.commit()

    def bot_check_is_admin(self, user_id):
        args = (user_id,)
        cursor = self.db.connection.cursor()
        cursor.execute("""select user_admin from users where user_id = ?;""", args)
        row = cursor.fetchone()
        if row is not None:
            row = str(row)[1:-2]
            if row == '1':
                return True
        else:
            return False

    def bot_check_is_root_admin(self, user_id):
        args = (user_id,)
        cursor = self.db.connection.cursor()
        cursor.execute("""select user_root_admin from users where user_id = ?;""", args)
        row = cursor.fetchone()
        if row is not None:
            row = str(row)[1:-2]
            if row == '1':
                return True
        else:
            return False

    insert_new_user = """
       insert into users(user_id, user_login, user_admin, user_root_admin, date_of_adding) values(?, ?, FALSE, FALSE, date('now'));
       """

lg = LogicalPart()
lg.bot_find_recipes_by_name('молоко')
lg.bot_get_active_users_week()