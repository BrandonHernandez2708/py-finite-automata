class Letter:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'{self.value}'


class Append():
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __repr__(self):
        return f'({self.a}{self.b})'


class Or():
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __repr__(self):
        return f'({self.a}|{self.b})'


class Kleene():
    def __init__(self, a):
        self.a = a

    def __repr__(self):
        return f'({self.a}*)'


class Plus():
    def __init__(self, a):
        self.a = a

    def __repr__(self):
        return f'({self.a}+)'
