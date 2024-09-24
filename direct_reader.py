from tokens import Token, TokenType

LETTERS = 'abcdefghijklmnopqrstuvwxyz01234567890.'

class DirectReader:

    def __init__(self, string: str):
        # Inicializa el lector directo con una cadena de entrada
        self.string = iter(string.replace(' ', ''))
        self.input = set()
        self.rparPending = False
        self.Next()

    def Next(self):
        # Avanza al siguiente carácter en la cadena de entrada
        try:
            self.curr_char = next(self.string)
        except StopIteration:
            self.curr_char = None

    def CreateTokens(self):
        # Genera tokens a partir de la cadena de entrada
        while self.curr_char != None:

            if self.curr_char in LETTERS:
                self.input.add(self.curr_char)
                yield Token(TokenType.LETTER, self.curr_char)

                self.Next()

                # Finalmente, verifica si necesitamos agregar un token de concatenación
                if self.curr_char != None and \
                        (self.curr_char in LETTERS or self.curr_char == '('):
                    yield Token(TokenType.APPEND, '.')

            elif self.curr_char == '|':
                yield Token(TokenType.OR, '|')

                self.Next()

                if self.curr_char != None and self.curr_char not in '()':
                    yield Token(TokenType.LPAR)

                    while self.curr_char != None and self.curr_char not in ')*+?':
                        if self.curr_char in LETTERS:
                            self.input.add(self.curr_char)
                            yield Token(TokenType.LETTER, self.curr_char)

                            self.Next()
                            if self.curr_char != None and \
                                    (self.curr_char in LETTERS or self.curr_char == '('):
                                yield Token(TokenType.APPEND, '.')

                    if self.curr_char != None and self.curr_char in '*+?':
                        self.rparPending = True
                    elif self.curr_char != None and self.curr_char == ')':
                        yield Token(TokenType.RPAR, ')')
                    else:
                        yield Token(TokenType.RPAR, ')')

            elif self.curr_char == '(':
                self.Next()
                yield Token(TokenType.LPAR)

            elif self.curr_char in (')*+?'):

                if self.curr_char == ')':
                    self.Next()
                    yield Token(TokenType.RPAR)

                elif self.curr_char == '*':
                    self.Next()
                    yield Token(TokenType.KLEENE)

                elif self.curr_char == '+':
                    self.Next()
                    yield Token(TokenType.PLUS)

                elif self.curr_char == '?':
                    self.Next()
                    yield Token(TokenType.QUESTION)

                if self.rparPending:
                    yield Token(TokenType.RPAR)
                    self.rparPending = False

                # Finalmente, verifica si necesitamos agregar un token de concatenación
                if self.curr_char != None and \
                        (self.curr_char in LETTERS or self.curr_char == '('):
                    yield Token(TokenType.APPEND, '.')

            else:
                raise Exception(f'Entrada inválida: {self.curr_char}')

        yield Token(TokenType.APPEND, '.')
        yield Token(TokenType.LETTER, '#')

    def GetSymbols(self):
        # Devuelve el conjunto de símbolos encontrados en la cadena de entrada
        return self.input
