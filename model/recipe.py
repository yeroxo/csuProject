class Recipe:
    def __init__(self):
        self.name = None
        self.image = None
        self.ingredients = None
        self.link = None
        self.description = None
        self.calories = None
        self.time_cooking = None
        self.categories = None

    def __init__(self, name, image, ingredients, link, description, calories, time, categories):
        self.name = name
        self.image = image
        self.ingredients = ingredients
        self.link = link
        self.description = description
        self.calories = calories
        self.time_cooking = time
        self.categories = categories

    def __str__(self):
        return '({}, {}, {}, {}, {}, {}, {})'.format(self.name, self.image, self.ingredients, self.link, self.description,
                                                     self.calories, self.time_cooking, self.categories)
