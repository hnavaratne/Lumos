from flask import Flask, jsonify, request, Blueprint
from flask_restful import Resource, Api
from urllib.parse import unquote
from pre_processing import pre_process_text
from text_utils import TextUtils
import json
import csv
import os

blue_print = Blueprint('rci-calculator', __name__, url_prefix='/api/v1')
app = Flask(__name__)
api = Api(blue_print)
app.register_blueprint(blue_print)

# Class to catch the requests
class RQ_Metrics(Resource):
    def get(self):
        return jsonify({'RQ_Metrics' : 'OK'})
    def post(self):
        if not request.data:
            return jsonify({'RQ_Metrics' : ''})
        data = json.loads(request.data.decode('utf-8'))
        text = ''
        if data and data['content']:
            text = unquote(data['content'])
        else:
            text = ''
        pre_process = pre_process_text()
        text = pre_process.replace_required_tags(text=text)         #replacing pre-defined html tags with pre-defined texts
        text = pre_process.remove_html_tags(text=text)              #remove html tags
        text = pre_process.remove_special_characters(text=text)     #remove pre-defined set of characters
        text = pre_process.replace_required_characters(text=text)   #replace pre-defined characters with pre-defined characters
        text = pre_process.space_checker(text=text)                 #removes unwanted spaces before and after in a set of pre-defined characters

        if text == '' or len(text.split()) <= 1:
            return jsonify({'RQ_Metrics' : ''})
        result = {}
        score = 0
        text_utils = TextUtils()

        sentence_count_score = text_utils.sentence_count_rating(text)
        result['sentence_count_score'] = sentence_count_score
        if sentence_count_score[0] == 0:
            word_count_score = text_utils.get_word_count_rating(text)
            word_list_score = text_utils.get_word_list_score(text)
            word_count_score = [0,"", word_count_score[2]]
            word_list_score = [0,"", word_list_score[2]]
            result['word_list_score'] = word_list_score
            result['word_count_score'] = word_count_score
        else:
            word_list_score = text_utils.get_word_list_score(text)
            result['word_list_score'] = word_list_score
            word_count_score = text_utils.get_word_count_rating(text)
            result['word_count_score'] = word_count_score

        listings_score = text_utils.count_listings(text)
        result['listing_score'] = listings_score

        noun_score = text_utils.count_nouns(text)
        result['noun_score'] = noun_score

        sigma_score = word_list_score[0] + word_count_score[0] + sentence_count_score[0] + listings_score[0] + \
                      noun_score[0]
        total_score = score + sigma_score

        result['overall_score'] = total_score
        overall_rating = 0
        if total_score >= 90:
            overall_rating = 5
        elif 50 <= total_score < 90:
            overall_rating = 4
        elif 40 <= total_score < 50:
            overall_rating = 3
        elif 20 <= total_score < 40:
            overall_rating = 2
        elif total_score < 20:
            overall_rating = 1

        if overall_rating == 5:
            for res in result:
                string = str(result[res])
                intX = 0
                if len(string) <= 3:
                    intX = int(string[0:len(string)])
                    result[res] = intX
                elif string[2] == ',':
                    intX = int(string[1:2])
                    result[res] = (intX, "", "")
                else:
                    intX = int(string[1:3])
                    result[res] = (intX, "", "")

        result['overall_rating'] = overall_rating
        write_to_csv(text, sentence_count_score[0], word_list_score[0], word_count_score[0], listings_score[0], noun_score[0], overall_rating, total_score)
        return jsonify({'RQmetrics': result})


#writing data to a csv file
def write_to_csv(text, sen_count_score, word_list_score, word_count_score, list_score, noun_score, rating, total):
    if text != '':
        sen_count_score = 0 if sen_count_score is None else sen_count_score
        word_list_score = 0 if word_list_score is None else word_list_score
        word_count_score = 0 if word_count_score is None else word_count_score
        list_score = 0 if list_score is None else list_score
        noun_score = 0 if noun_score is None else noun_score
        rating = 0 if rating is None else rating
        total = 0 if total is None else total

        file_path = 'rule_classifier.csv'
        try:
            if not os.path.exists(file_path):
                file = open(file_path, mode='a', encoding='UTF-8')
                csv_writer = csv.writer(file)
                row = ['Description', 'Sentence Count Score', 'Word List Score', 'Word Count Score', 'Listing Score',
                       'Noun Score', 'Overall Rating', 'Total Score']
                csv_writer.writerow(row)
                file.close()
        except:
            print("Error occured finding the path!")

        with open(file_path, mode='a', encoding='UTF-8') as file:
            try:
                csv_writer = csv.writer(file)
                row = [text, sen_count_score, word_list_score, word_count_score, list_score, noun_score, rating, total]
                csv_writer.writerow(row)
            except TypeError as te:
                print("Error occured while writng to CSV : " + te)
            finally:
                file.close()


# Class to shutdown the server
class Shutdown(Resource):
    def post(self):
        shutdown()

def shutdown():
    shutdown_server()
    return 'Server shutting down...'

def shutdown_server():
    func =request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running without the Werkzeug server...')
    func()

api.add_resource(RQ_Metrics, '/RQmetrics')
api.add_resource(Shutdown, '/shutdown')

if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=9154, debug=True)