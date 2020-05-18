import pyparsing as pp


class SearchParser:
    def __init__(self):
        COLON, EQUAL, COMMA = map(pp.Literal, ":=,")
        SCOLON, SEQUAL, SCOMMA = map(pp.Suppress, ":=,")
        LPAREN, RPAREN = map(pp.Suppress, "()")
        word_strict = pp.Regex(r"[^\s'\":=]+")
        sgl_quoted_string = pp.QuotedString("'", escChar="\\")
        dbl_quoted_string = pp.QuotedString('"', escChar="\\")
        word = sgl_quoted_string | dbl_quoted_string | word_strict

        date = pp.pyparsing_common.iso8601_date.copy()
        date.setParseAction(pp.pyparsing_common.convertToDate())
        date_expr = date + SCOMMA + date | COMMA + date | date + COMMA
        date_range = LPAREN + date_expr + RPAREN

        filtr_delim = COLON | EQUAL
        filtr_delim_suppress = SCOLON | SEQUAL
        filtr = pp.Group(word_strict + filtr_delim_suppress + date_range) | pp.Group(
            word_strict + filtr_delim + word
        )
        query_patt = pp.Dict(filtr) | word

        self.__expr = query_patt() * (1,)

    def parse_query(self, query: str):
        parsed_query = self.__expr.parseString(query)
        terms = list(filter(lambda t: isinstance(t, str), parsed_query.asList()))
        filters = parsed_query.asDict()

        return terms, filters
