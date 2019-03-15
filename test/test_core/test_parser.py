from palu.core.parser import parser


def test_parse_syntax_error():
    script = '''while 
    do 
    end
    '''
    result = parser.parse(script)
    print(result)


def test_parse_while():
    script = '''
    while true do
        something;
        dosomethingelse arg;
    end
    '''
    result = parser.parse(script)
    print(result)
