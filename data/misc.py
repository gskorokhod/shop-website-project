from uuid import uuid4


def generate_uuid():
    return str(uuid4())


class Rating:
    def __init__(self, ratings):
        self.ratings = ratings

    def get_avg(self):
        if self.ratings:
            return round(sum(self.ratings) / len(self.ratings), 2)
        else:
            return 0

    def get_n_with_value(self, val):
        return self.ratings.count(val)

    def get_n_total(self):
        return len(self.ratings)

    def get_percent_with(self, val):
        if self.ratings:
            return (self.get_n_with_value(val) / self.get_n_total()) * 100
        else:
            return 0
