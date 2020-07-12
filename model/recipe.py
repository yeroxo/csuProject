class Recipe:
    def __init__(self, name, ingredients, link, description, calories, time_cooking, categories):
        self.name = name
        self.ingredients = ingredients
        self.link = link
        self.description = description
        self.calories = calories
        self.time_cooking = time_cooking
        self.categories = categories

    def __str__(self):
        return '({}, {}, {}, {}, {}, {}, {})'.format(self.name, self.ingredients, self.link, self.description,
                                                     self.calories, self.time_cooking, self.calories)
