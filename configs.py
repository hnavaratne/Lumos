#word list which determines clarity
word_list = {
    'generalities': ['about', 'almost', 'bad', 'close', 'good', 'many', 'most', 'timely', 'more','like','less'],
    'incomplete' : ['tbd','tbs','tbe','tbc','tbr','not defined','not determined','but not limited to','as a minimum','appropriate']
}

#continuance words list
listings = [
    'following',
    'below',
    'follows',
    'listed',
    'follows',
    'in particular',
    'such as'
]

#word count per sentence
word_count = {
    'min' : 10,
    'max' : 25
}

#sentence count per desciption
sentence_count = {
    'min' : 3,
    'max' : 10
}

references = [
    {
        'word': 'like',
        'reference' : ['figure','table','example','note']
    }
]


#rules to be considered
word_rule = {
    "inclusions" : [
        {
            "word": "like",
            "corresponding_word": "example",
            "gap": 5
        }
    ],
    "exclusions" : [
        {
            "word": "may",
            "corresponding_word": "probably",
            "gap": 5
        }
    ]
}

max_scores = {
    "word_list": 25,
    "sentence_count": 30,
    "word_count": 20,
    "nouns": 15,
    "references": 10,
    "listings":10

}

dictionary = [
    "in case",
    "as a matter of fact"
]

nouns_followed_by = [
    "who",
    "which",
    "such"
]