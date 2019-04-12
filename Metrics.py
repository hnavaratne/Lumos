from flask import Flask, jsonify, request, abort, redirect, Blueprint
from flask_restful import Resource, Api
import re
from urllib.parse import unquote
import json
import textacy
from textblob import TextBlob
import configs as cfg
from text_utils import TextUtils

bp = Blueprint('rci-calculator', __name__, url_prefix='/api/v1')

app = Flask(__name__)
api = Api(bp)
app.register_blueprint(bp)


VOCABULARY = cfg.word_list

OUTPUT_MESSAGES = {
    'generalities': 'Generalities (i.e about, almost, bad, close, good, many, most, timely) weaken the specification. Higher the count, Lower the specification.',
    'imperatives': 'An explicit specification will have most of its counts high in the IMPERATIVE list (i.e. shall, must, required). Higher the count, Higher the Specification Quality',
    'continuance': 'Extensive use of continuances indicate multiple, complex requirements that may not be adequately factored into development. Higher the count, Higher the Specification Complexity',
    'directives': 'The implication is the higher the number of Total DIRECTIVES the more precisely the requirements are defined. Higher the count, Higher the Specification Quality',
    'weak_phrases': 'WEAK PHRASE total is indication of the extent that the specification is ambiguous and incomplete. Higher the count, Lower the Specification Quality',
    'incomplete': 'The specification of requirements is not fully developed or provides a basis for expansion or addition of new requirements at a later date. Higher the count, Lower the Specification Quality',
    'options': 'This type of statement loosens the specification, reduces the acquirers control over the final product. Higher the count, lower the specification.'
}

POSTIVE_CATEGORTIES=['imperatives','directives', 'continuance']
NEGATIVE_CATEGORIES=['generalities','weak_phrases','incomplete','options']

def getCount(category, requirement):
    wordList = []
    category_occurence = 0
    word_occur_pd = 0
    for word in VOCABULARY[category]:
        word_occur_pd = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), requirement.lower()))
        # word_occur_pd = data_frame['content'].values[0].count(word)
        if word_occur_pd > 0:
            wordList.append(word)
            category_occurence = category_occurence + word_occur_pd
    print(str(category).upper())
    print(wordList)
    print(category_occurence)
    seperator = '\',\' '
    words_str = ''
    if category in NEGATIVE_CATEGORIES and category_occurence >= 1 and len(wordList) > 0:
        words_str = 'Use less '+category+'(i.e \'' + seperator.join(wordList) + '\' ) to improve clarity of the requirement. Extensive use make requirements more complex. Minimise the use as much as possible : \'' + seperator.join(VOCABULARY[category]) + '\''
    elif category in POSTIVE_CATEGORTIES and category_occurence <=2 and len(wordList) > 0:
        words_str = 'Too few '+category+' used.Used '+category+' are \'' + seperator.join(wordList) + '\' , use more of it .They clarify the requirement more.ex:- \'' + seperator.join(VOCABULARY[category]) + '\''
    message = OUTPUT_MESSAGES[category]
    index = category_occurence
    if category_occurence >= 5:
        index = 5
    return index, message, words_str


class RQmetrics(Resource):
    def get(self):
        return jsonify({'RQmetrics': 'OK'})
    def post(self):
        if not request.data:
            return jsonify({'RQmetrics': ""})
        data = json.loads(request.data.decode('utf-8'))
        # data = request.get_json()
        if data and data['content']:
            requirement = unquote(data['content'])
            requirement = requirement.replace('<p>','')
            requirement = requirement.replace('</p>', '')
        else:
            requirement = ""
        if len(requirement) == 0 or len(requirement.split()) <=1:
            return jsonify({'RQmetrics': ""})
        result = {}
        text_utils = TextUtils()
        result['sentence_rating'] = text_utils.sentence_count_rating(text=requirement)
        result['word_rating'] = text_utils.get_word_count_rating(text=requirement)
        for category in VOCABULARY.keys():
            dict_key = ''.join([category, '_rating'])
            index, message, words_str = getCount(category,requirement)
            if index > 0:
                result[dict_key] = [index, message, words_str]

        sigma_positive_rating = 0
        sigma_negative_rating = 0

        negative_categories_found = 0
        positive_categories_found = 0

        sentence_rating = round(result['sentence_rating'][0])
        print('sentence_rating:' + str(sentence_rating))
        word_rating = round(result['word_rating'][0])
        print('word_rating:' + str(word_rating))

        if 'imperatives_rating' in result:
            imperatives_rating = result['imperatives_rating'][0]
            print('imperatives_rating:' + str(imperatives_rating))
            sigma_positive_rating = sigma_positive_rating + imperatives_rating
            positive_categories_found = positive_categories_found + 1
        if 'continuance_rating' in result:
            continuance_rating = (result['continuance_rating'][0])
            print('continuance_rating:' + str(continuance_rating))
            sigma_positive_rating = sigma_positive_rating + continuance_rating
            positive_categories_found = positive_categories_found + 1
        if 'directives_rating' in result:
            directives_rating = result['directives_rating'][0]
            print('directives_rating:' + str(directives_rating))
            sigma_positive_rating = sigma_positive_rating + directives_rating
            positive_categories_found = positive_categories_found + 1

        if positive_categories_found == 0:
            average_sigma_positive_rating = 0
        else:
            average_sigma_positive_rating = round(sigma_positive_rating / positive_categories_found)

        print('average_sigma_positive_rating')
        print(average_sigma_positive_rating)

        average_positive_rating = (5*sentence_rating + 3*word_rating + 2*average_sigma_positive_rating)/10

        print('average_positive_rating')
        print(average_positive_rating)


        if 'weak_phrases_rating' in result:
            weak_phrases_rating = (result['weak_phrases_rating'][0])
            print('weak_phrases_rating:' + str(weak_phrases_rating))
            sigma_negative_rating = sigma_negative_rating + weak_phrases_rating
            negative_categories_found = negative_categories_found + 1
        if 'incomplete_rating' in result:
            incomplete_rating = (result['incomplete_rating'][0])
            print('incomplete_rating:' + str(incomplete_rating))
            sigma_negative_rating = sigma_negative_rating + incomplete_rating
            negative_categories_found = negative_categories_found + 1
        if 'options_rating' in result:
            options_rating = (result['options_rating'][0])
            print('options_rating:' + str(options_rating))
            sigma_negative_rating = sigma_negative_rating + options_rating
            negative_categories_found = negative_categories_found + 1
        if 'generalities_rating' in result:
            generalities_rating = (result['generalities_rating'][0])
            print('generalities_rating:' + str(generalities_rating))
            sigma_negative_rating = sigma_negative_rating + generalities_rating
            negative_categories_found = negative_categories_found + 1

        if negative_categories_found == 0:
            average_sigma_negative_rating = 0
        else:
            average_sigma_negative_rating = round(sigma_negative_rating / negative_categories_found)

        print('average_sigma_negative_rating')
        print(average_sigma_negative_rating)

        average_overall_rating = round(abs(average_positive_rating*7 - average_sigma_negative_rating*3 )/ 10)


        # sigma_weighed_rating = readability_rating + imperatives_rating + continuance_rating + directives_rating + incomplete_rating + options_rating + generalities_rating + weak_phrases_rating
        # print('WEIGHTED:' + str(sigma_weighed_rating))
        # weighed_rating = sigma_weighed_rating / len(result)
        result['overall_rating'] = average_overall_rating if not average_overall_rating == 0 else 1
        print('OVERALL:' + str(result['overall_rating']))
        return jsonify({'RQmetrics': result})

class Shutdown(Resource):
    def post(self):
        shutdown()

def shutdown():
    shutdown_server()
    return 'Server shutting down...'

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

api.add_resource(RQmetrics, '/RQmetrics')
api.add_resource(Shutdown, '/shutdown')

if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=5000, debug=True)