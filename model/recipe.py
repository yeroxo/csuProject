class Recipe:
    def __init__(self):
        self.name = None
        self.ingredients = None
        self.link = None
        self.description = None
        self.calories = None
        self.time_cooking = None
        self.categories = None

    def __str__(self):
        return '({}, {}, {}, {}, {}, {}, {})'.format(self.name, self.ingredients, self.link, self.description,
                                                     self.calories, self.time_cooking, self.calories)
