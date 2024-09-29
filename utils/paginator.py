import math

class Paginator:
    def __init__(self, array: list, page: int = 1, per_page: int = 1):
        self.array = array
        self.per_page = per_page
        self.page = page
        self.len = len(self.array)
        self.pages = math.ceil(self.len / self.per_page) if self.len > 0 else 1

    def get_slice(self):
        start = (self.page - 1) * self.per_page
        stop = start + self.per_page
        return self.array[start:stop]

    def get_page(self):
        """Возвращает элементы текущей страницы."""
        return self.get_slice()

    def has_next(self):
        """Проверяет, есть ли следующая страница."""
        return self.page < self.pages

    def has_previous(self):
        """Проверяет, есть ли предыдущая страница."""
        return self.page > 1

    def get_next(self):
        """Получает элементы следующей страницы, если она существует."""
        if self.has_next():
            next_page = self.page + 1
            return Paginator(self.array, next_page, self.per_page).get_page()
        raise IndexError('Next page does not exist. Use has_next() to check before.')

    def get_previous(self):
        """Получает элементы предыдущей страницы, если она существует."""
        if self.has_previous():
            previous_page = self.page - 1
            return Paginator(self.array, previous_page, self.per_page).get_page()
        raise IndexError('Previous page does not exist. Use has_previous() to check before.')