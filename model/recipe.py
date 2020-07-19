class Recipe:
    def __init__(self, name=None, image=None, ingredients=None, link=None, description=None, calories=None, time=None, categories=None, id=None):
        self.id = id
        self.name = name
        self.image = image
        self.ingredients = ingredients
        self.link = link
        self.description = description
        self.calories = calories
        self.time_cooking = time
        self.categories = categories

    def __str__(self):
        return '({}, {}, {}, {}, {}, {}, {}, {})'.format(self.id, self.name, self.image, self.ingredients, self.link, self.description,
                                                     self.calories, self.time_cooking, self.categories)
