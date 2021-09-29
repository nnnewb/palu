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
        $.mod,
        $.declare,
        $.external,
        $.while,
        $.if,
        $.return,
        $.func,
        $.type_alias,
        $.expr
      ),
    empty: ($) => ";",
    mod: ($) => seq("mod", field("name", $.ident)),
    expr: ($) =>
      choice(
        $.ident_expr,
        $.binary_expr,
        $.unary_expr,
        $.cond_expr,
        $.call_expr,
        $.parenthesized_expr,
        $.assignment_expr,
        $.number_literal,
        $.string_literal,
        $.true_lit,
        $.false_lit,
        $.null_lit
      ),
    parenthesized_expr: ($) => seq("(", field("expr", $.expr), ")"),

    assignment_expr: ($) =>
      prec.right(
        PREC.ASSIGNMENT,
        seq(
          field("left", $.ident_expr),
          field(
            "operator",
            choice(
              "=",
              "*=",
              "/=",
              "%=",
              "+=",
              "-=",
              "<<=",
              ">>=",
              "&=",
              "^=",
              "|="
            )
          ),
          field("right", $.expr)
        )
      ),

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

    call_expr: ($) =>
      prec(
        PREC.CALL,
        seq(field("func_name", $.ident_expr), field("args", $.argument_list))
      ),
    argument_list: ($) =>
      seq("(", optional(seq($.expr, optional(repeat(seq(",", $.expr))))), ")"),

    // let ident [: type_ident] [= expr]
    declare: ($) =>
      seq(
        "let",
        field("typed_ident", $.typed_ident),
        "=",
        field("initial", $.expr)
      ),

    // external ident : type
    external: ($) => choice($.external_variable, $.external_function),
    external_variable: ($) =>
      seq("external", field("typed_ident", $.typed_ident)),
    external_function: ($) =>
      seq(
        "external",
        "fn",
        field("func_name", $.ident),
        field("params", $.params),
        "->",
        field("returns", $.ident_expr)
      ),

    func: ($) =>
      seq(
        "fn",
        field("func_name", $.ident),
        field("params", $.params),
        "->",
        field("returns", $.ident_expr),
        field("body", $.codeblock)
      ),

    // while expr stmt
    while: ($) =>
      seq("while", field("condition", $.expr), field("body", $.codeblock)),
    // if expr stmt
    if: ($) =>
      seq(
        "if",
        field("condition", $.expr),
        field("consequence", $.codeblock),
        field("alternative", optional($.codeblock))
      ),
    // return expr
    return: ($) => seq("return", field("returns", $.expr)),

    // do stmt [...stmt] end
    codeblock: ($) => seq("do", optional(repeat($.stmt)), "end"),

    type_alias: ($) =>
      seq(
        "type",
        field("ident", $.ident),
        "=",
        field("typing", choice($.pointer, $.ident_expr))
      ),

    // =======================================================
    // identifier
    // =======================================================
    ident: ($) => /[a-zA-Z_]\w*/,
    typed_ident: ($) =>
      seq(
        field("ident", $.ident),
        optional(seq(":", field("typing", choice($.pointer, $.ident_expr))))
      ),
    pointer: ($) => seq("*", field("underlying", $.ident_expr)),
    params: ($) =>
      seq(
        "(",
        choice(
          "void",
          "...",
          seq(
            $.typed_ident,
            optional(repeat(seq(",", $.typed_ident))),
            optional(seq(",", "..."))
          )
        ),
        ")"
      ),

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
