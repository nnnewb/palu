const PREC = {
  PAREN_DECLARATOR: -10,
  ASSIGNMENT: -1,
  CONDITIONAL: -2,
  DEFAULT: 0,
  LOGICAL_OR: 1,
  LOGICAL_AND: 2,
  INCLUSIVE_OR: 3,
  EXCLUSIVE_OR: 4,
  BITWISE_AND: 5,
  EQUAL: 6,
  RELATIONAL: 7,
  SIZEOF: 8,
  SHIFT: 9,
  ADD: 10,
  MULTIPLY: 11,
  CAST: 12,
  UNARY: 13,
  CALL: 14,
  FIELD: 15,
  SUBSCRIPT: 16,
};

module.exports = grammar({
  name: "palu",

  rules: {
    source_file: ($) => repeat(choice($.stmt)),
    stmt: ($) =>
      choice(
        $.empty,
        $.declare,
        $.external,
        $.expr,
        $.while,
        $.if,
        $.else,
        $.return
      ),
    empty: ($) => ";",
    expr: ($) =>
      choice(
        $.ident_expr,
        $.binary_expr,
        $.unary_expr,
        $.cond_expr,
        $.call_expr,
        $.lambda,
        $.parenthesized_expr,
        $.number_literal,
        $.string_literal,
        $.true_lit,
        $.false_lit,
        $.null_lit
      ),
    parenthesized_expr: ($) => seq("(", $.expr, ")"),

    ident_expr: ($) =>
      prec(PREC.FIELD, seq($.ident, optional(repeat(seq(".", $.ident))))),

    cond_expr: ($) =>
      prec.right(
        PREC.CONDITIONAL,
        seq(
          field("condition", $.expr),
          "?",
          field("consequence", $.expr),
          ":",
          field("alternative", $.expr)
        )
      ),

    unary_expr: ($) =>
      prec.left(
        PREC.UNARY,
        seq(
          field("operator", choice("!", "~", "-", "+")),
          field("argument", $.expr)
        )
      ),

    binary_expr: ($) => {
      const table = [
        ["+", PREC.ADD],
        ["-", PREC.ADD],
        ["*", PREC.MULTIPLY],
        ["/", PREC.MULTIPLY],
        ["%", PREC.MULTIPLY],
        ["||", PREC.LOGICAL_OR],
        ["&&", PREC.LOGICAL_AND],
        ["|", PREC.INCLUSIVE_OR],
        ["^", PREC.EXCLUSIVE_OR],
        ["&", PREC.BITWISE_AND],
        ["==", PREC.EQUAL],
        ["!=", PREC.EQUAL],
        [">", PREC.RELATIONAL],
        [">=", PREC.RELATIONAL],
        ["<=", PREC.RELATIONAL],
        ["<", PREC.RELATIONAL],
        ["<<", PREC.SHIFT],
        [">>", PREC.SHIFT],
      ];

      return choice(
        ...table.map(([operator, precedence]) => {
          return prec.left(
            precedence,
            seq(
              field("left", $.expr),
              field("operator", operator),
              field("right", $.expr)
            )
          );
        })
      );
    },

    call_expr: ($) => prec(PREC.CALL, seq($.ident_expr, $.argument_list)),
    argument_list: ($) =>
      seq("(", optional(seq($.expr, optional(repeat(seq(",", $.expr))))), ")"),

    // let ident [: type_ident] [= expr]
    declare: ($) =>
      seq("let", $.typed_ident, optional(seq("=", $.expr))),

    // external ident : type
    external: ($) => seq("external", $.typed_ident),

    // ([ident [, ident]]): type => (codeblock | expr)
    lambda: ($) => seq($.func_signature, "=>", choice($.codeblock, $.expr)),

    // while expr stmt
    while: ($) => seq("while", $.expr, $.codeblock),
    // if expr stmt
    if: ($) => seq("if", $.expr, $.codeblock),
    // else stmt
    else: ($) => seq("else", choice($.codeblock, $.if)),
    // return expr
    return: ($) => seq("return", $.expr),

    // do stmt [...stmt] end
    codeblock: ($) => seq("do", optional(repeat($.stmt)), "end"),

    // =======================================================
    // identifier
    // =======================================================
    ident: ($) => /[a-zA-Z_]\w*/,
    typed_ident: ($) => seq($.ident, $.typing),
    typing: ($) => seq(":", choice($.ident, $.func_signature)),
    func_signature: ($) => seq($.params, $.typing),
    params: ($) => seq("(", seq($.typed_ident, optional(seq(",", $.typed_ident))), ")"),

    // =======================================================
    // literals
    // =======================================================
    true_lit: ($) => "true",
    false_lit: ($) => "false",
    null_lit: ($) => "null",

    string_literal: ($) =>
      choice(
        seq(
          "'",
          repeat(
            choice(token.immediate(prec(1, /[^\\'\n]+/)), $.escape_sequence)
          ),
          "'"
        ),
        seq(
          '"',
          repeat(
            choice(token.immediate(prec(1, /[^\\"\n]+/)), $.escape_sequence)
          ),
          '"'
        )
      ),
    escape_sequence: ($) =>
      token(
        prec(
          1,
          seq(
            "\\",
            choice(
              /[^xuU]/,
              /\d{2,3}/,
              /x[0-9a-fA-F]{2,}/,
              /u[0-9a-fA-F]{4}/,
              /U[0-9a-fA-F]{8}/
            )
          )
        )
      ),

    number_literal: ($) => {
      const separator = "'";
      const hex = /[0-9a-fA-F]/;
      const decimal = /[0-9]/;
      const hexDigits = seq(repeat1(hex), repeat(seq(separator, repeat1(hex))));
      const decimalDigits = seq(
        repeat1(decimal),
        repeat(seq(separator, repeat1(decimal)))
      );
      return token(
        seq(
          optional(/[-\+]/),
          optional(choice("0x", "0b")),
          choice(
            seq(
              choice(
                decimalDigits,
                seq("0b", decimalDigits),
                seq("0x", hexDigits)
              ),
              optional(seq(".", optional(hexDigits)))
            ),
            seq(".", decimalDigits)
          ),
          optional(seq(/[eEpP]/, optional(seq(optional(/[-\+]/), hexDigits)))),
          repeat(choice("u", "l", "U", "L", "f", "F"))
        )
      );
    },
    // http://stackoverflow.com/questions/13014947/regex-to-match-a-c-style-multiline-comment/36328890#36328890
    comment: ($) =>
      token(
        choice(
          seq("//", /(\\(.|\r?\n)|[^\\\n])*/),
          seq("/*", /[^*]*\*+([^/*][^*]*\*+)*/, "/")
        )
      ),
  },
});
