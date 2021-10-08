from .utils import Position, TT, DIGITS, LETTERS, KEYWORDS
from .errors import Error, IllegalCharError, ExpectedCharError

LETTERS_DIGITS = LETTERS + DIGITS

class Token:
    def __init__(
        self,
        type: str,
        value=None,
        pos_start: Position = None,
        pos_end: Position = None,
    ):
        self.type = type
        self.value = value
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def matches(self, type, value):
        return self.type == type and self.value == value

    def __repr__(self):
        if self.value is not None:
            return f"{self.type}:{self.value}"
        return f"{self.type}"


class Lexer:
    def __init__(self, text: str, fn: str):
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = (
            self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
        )

    def make_tokens(self) -> tuple[list[Token], Error]:  # sourcery no-metrics
        tokens = []

        while self.current_char is not None:
            if self.current_char in " \t":
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char == "+":
                tokens.append(Token(TT.PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == "\"":
                string, error = self.make_string()
                if error:  # To avoid unlcosed strings
                    return [], error 
                tokens.append(string)
            elif self.current_char == "-":
                tokens.append(self.make_arrow_or_minus())
            elif self.current_char == "*":
                tokens.append(self.make_double_char_token(TT.MULT, TT.POW, "*"))
            elif self.current_char == "/":
                tokens.append(self.make_double_char_token(TT.DIV, TT.FDIV, "/"))
            elif self.current_char == "%":
                tokens.append(Token(TT.MODU, pos_start=self.pos))
            elif self.current_char == "(":
                tokens.append(Token(TT.LPAR, pos_start=self.pos))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(TT.RPAR, pos_start=self.pos))
                self.advance()
            elif self.current_char == ",":
                tokens.append(Token(TT.COMMA, pos_start=self.pos))
                self.advance()
            elif self.current_char == "!":
                tok, error = self.make_not_equals()
                if error: return [], error
                tokens.append(tok)
            elif self.current_char == "=":
                tokens.append(self.make_equals())
            elif self.current_char == "<":
                tokens.append(self.make_less_than())
            elif self.current_char == ">":
                tokens.append(self.make_greater_than())
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, f'"{char}"')

        tokens.append(Token(TT.EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self) -> Token:
        num_str = ""
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char in DIGITS + ".":
            if self.current_char == ".":
                if dot_count == 1:
                    break
                dot_count += 1
            num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT.INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT.FLOAT, float(num_str), pos_start, self.pos)

    def make_identifier(self):
        id_str = ""
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char in LETTERS_DIGITS:
            id_str += self.current_char
            self.advance()

        if id_str in KEYWORDS:
            tok_type = TT.KEYWORD
        elif id_str in {"true", "false"}:
            tok_type = TT.BOOL
            id_str = id_str == "true"
        else:
            tok_type = TT.IDENTIFIER

        return Token(tok_type, id_str, pos_start, self.pos)

    def make_not_equals(self) -> tuple[Token, Error]:
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            self.advance()
            return Token(TT.NE, pos_start=pos_start, pos_end=self.pos)

        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")

    def make_equals(self) -> tuple[Token, Error]:
        return self.make_double_char_token(TT.EQ, TT.EE, "=") 

    def make_less_than(self) -> tuple[Token, Error]:
        return self.make_double_char_token(TT.LT, TT.LTE, "=") 

    def make_greater_than(self) -> tuple[Token, Error]:
        return self.make_double_char_token(TT.GT, TT.GTE, "=") 

    def make_arrow_or_minus(self):
        return self.make_double_char_token(TT.MINUS, TT.ARROW, ">")

    def make_double_char_token(self, default_type, new_type, second_char):
        pos_start = self.pos.copy()
        self.advance()
        tok_type = default_type

        if self.current_char == second_char:
            self.advance()
            tok_type = new_type

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_string(self):
        string = ""
        pos_start = self.pos.copy()
        self.advance()

        escape_characters = {
            "n": "\n",
            "t": "\t",
        }

        while self.current_char != "\"" and self.current_char is not None:
            if self.current_char == "\\":
                self.advance()
                string += escape_characters.get(self.current_char, self.current_char)
            else:
                string += self.current_char
            self.advance()

            if self.current_char == "\"":
                break
        else:
            return [], ExpectedCharError(pos_start, self.pos, "'\"'")

        self.advance()
        return Token(TT.STRING, string, pos_start, self.pos), None
