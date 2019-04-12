#HTML Tags to be replaced
tags_replacer = {
    'li': '.1)',
    '/li': '.',
    '/p': '.\n',
    'p': ''
}

# Characters to be replaced
char_replacer = {
    ':': '.',
    ';': '.',
    '..': '.',
    '. .': '.',
    '\"': "\\'",
    '.\n.': '.\n'
}

#Special characters to be removed
spec_char_list = [
    '!',
    '$',
    '%',
    '^'
]

#Characters which needs a space to be added
space_check_lst = [
    '.',
    ',',
    ';',
    ':'
]