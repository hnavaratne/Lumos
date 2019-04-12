import textacy
import spacy
nlp = spacy.load('en_core_web_sm')
from textblob import TextBlob
import configs as cfg
import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

VOCABULARY = cfg.word_list

OUTPUT_MESSAGES = {
    'generalities': 'Generalities (i.e about, almost, bad, close, good, many, most, timely) weaken the specification. Higher the count, Lower the specification.',
    'incomplete': 'The specification of requirements is not fully developed or provides a basis for expansion or addition of new requirements at a later date. Higher the count, Lower the Specification Quality',
}

NEGATIVE_CATEGORIES = ['generalities', 'incomplete']

class TextUtils:

    def get_word_list_score(self, requirement):
        word_list_score = cfg.max_scores['word_list']
        words_list = []
        for category in VOCABULARY.keys():
            occurence, words = self.getCount(category,requirement)
            for i in range(occurence):
                word_list_score = word_list_score - 20
            words_list = words_list + words

        message = ''
        if len(words_list) > 0:
            words_str = ','.join(words_list)
            message = "Avoid using words such as (" + words_str + "), they tend to decrease the clarity of the requirement."

        if word_list_score < 0:
            word_list_score = 0
        elif word_list_score > cfg.max_scores['word_list']:
            word_list_score = cfg.max_scores['word_list']
        return word_list_score,"", message


    def getCount(self, category, requirement):
        wordList = []
        category_occurence = 0
        word_occur_pd = 0
        for word in VOCABULARY[category]:
            word_occur_pd = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), requirement.lower()))
            if word_occur_pd > 0:
                wordList.append(word)
                category_occurence = category_occurence + word_occur_pd
        print(str(category).upper())
        print(wordList)
        print(category_occurence)
        return category_occurence, wordList


    def get_word_count_rating(self,text=None):
        word_count_score = cfg.max_scores['word_count']
        min_word_count = cfg.word_count['min']
        max_word_count = cfg.word_count['max']

        text = self.skip_lists(text)
        sentences_ = self.get_sentences(text)
        word_counts = []
        short_sentences = []
        long_sentences = []
        sentence_count = 1
        for id, sentence in sentences_.items():
            text_stat = self.get_text_stats(sentence)
            word_count = text_stat.n_words
            word_rating = self.get_count_per_element(word_count, min_word_count, max_word_count)
            if word_rating == 0:
                short_sentences.append(sentence)
                sentence_count = sentence_count + 1
            elif word_rating == 1:
                long_sentences.append(sentence)
                sentence_count = sentence_count + 1
            if sentence_count > 4 or word_rating == 2 or len(sentences_.items()) < 4:
                word_counts.append(word_rating)

        for count in word_counts:
            if count == 0 or count == 1:
                word_count_score = word_count_score - 10
            else:
                word_count_score = word_count_score + 10
        message = ''
        if len(short_sentences) > 0:
            short_list = ','.join(short_sentences)
            message = "Some sentences such as ("+short_list+") contain too few words. Use longer sentences to clearly describe the requirement."
        if len(long_sentences) > 0:
            long_list = ','.join(long_sentences)
            message = message + "Sentences such as ("+long_list+") are too long. They could complicate the requirement and decrease clarity. Please use fewer words to clearly describe the requirement." \
                                  "Recommended to use between " + str(min_word_count) + " to " + str(
                        max_word_count) + " words per average sentence in the description."

        if word_count_score < 0:
            word_count_score = 0
        elif word_count_score > cfg.max_scores['word_count']:
            word_count_score = cfg.max_scores['word_count']
        return word_count_score, "", message
        # total_word_count_rating = sum(count for count in word_counts)
        # average_word_count_rating = total_word_count_rating / len(word_counts)
        #
        # message = ""
        # if 0 <= average_word_count_rating <= 1:
        #     if average_word_count_rating >= 0.5:
        #         message = "Too few words used per sentence in average. Use longer sentences to clearly describe the requirement."
        #     elif 0.5 < average_word_count_rating < 1:
        #         message = "Sentences used are too long. They could complicate the requirement and decrease clarity. Please use fewer words to clearly describe the requirement." \
        #                   "Recommended to use between " + str(min_word_count) + " to " + str(
        #             max_word_count) + " words per average sentence in the decription."
        #
        # print(average_word_count_rating)
        # average_word_count_rating = 5 if average_word_count_rating >= 1 else 1
        # return average_word_count_rating,"",message

    def skip_lists(self, text):
        results = re.findall('\d\).*?\.', text)
        if len(results) > 0:
            for sub_text in results:
                text = text.replace(sub_text, '')
        text = text.replace('\\n', ' ') if text.__contains__('\\n') else text
        text = text.replace('\\r', '') if text.__contains__('\\r') else text
        return text

    def sentence_count_rating(self, text=None):
        words_str = None
        message = []
        sentence_count_score = cfg.max_scores['word_count']

        min_sentence_count = cfg.sentence_count['min']
        max_sentence_count = cfg.sentence_count['max']

        text = self.skip_lists(text)
        #get sentence count in text
        text_stat = self.get_text_stats(text)
        sentence_count = text_stat.n_sents

        #get rating for sentence count
        sentence_count_rating = self.get_count_per_element(sentence_count,min_sentence_count,max_sentence_count)
        print(sentence_count_rating)

        message = ""
        if sentence_count_rating == 0:
            message = "Too few sentences used. The requirement tend to be less clear when described in a few lines."
        elif sentence_count_rating == 1:
            message = "Too many sentences will complicate the requirement. Use fewer sentences to improve clarity. Recommended to use between " + str(min_sentence_count) \
                + " to " + str(max_sentence_count) +" sentences for a decription."

        if sentence_count_rating == 0 or sentence_count_rating == 1:
            sentence_count_score = 0
        elif sentence_count_rating == 2:
            sentence_count_score = cfg.max_scores['sentence_count']

        return sentence_count_score,"",message
        # sentence_count_rating = 5 if sentence_count_rating == 2 else 1
        # return sentence_count_rating,"",message
        # message.append(self.get_sentence_message(sentence_count_range))
        # return overall_rating,words_str,message


    def count_references(self, text=None):
        references = cfg.references
        reference_score = cfg.max_scores['references']
        missing_refs = {}
        for reference_obj in references:
            word = reference_obj['word']
            reference = reference_obj['reference']
            if self.get_word_count(word, text) > 0:
                indices_ = self.get_word_index(word, text)
                for index in indices_:
                    temp_sentence = self.get_next_n_words(word, text[index:], n=5)
                    if len(temp_sentence) > 0 and not any(x in reference for x in temp_sentence[0]):
                        reference_score = reference_score - 10
                        missing_refs[word] = reference
        message = ''
        if len(missing_refs) > 0:
            ref_list = ','.join(list(missing_refs.values())[0])
            message = 'Missing references detected.For example words such as ('+str(list(missing_refs.keys())[0])+') could refer to some ('+ref_list+').'
        if reference_score < 0:
            reference_score = 0
        elif reference_score > cfg.max_scores['references']:
            reference_score = cfg.max_scores['references']
        return reference_score,"",message


    def count_listings(self, paragraph):
        # self.get_listing_texts(paragraph)
        listings = cfg.listings
        listing_score = cfg.max_scores['listings']
        missing_lists = []
        identified_lists = []
        prev_word = ''
        curr_word = ''
        for char_index, char in enumerate(paragraph):
            if char == ' ' or char == '.' or char == ',':
                if curr_word.lower() in listings:
                    if self.check_if_lists_added(paragraph[char_index + 1:]):
                        identified_lists.append(curr_word)
                        listing_score += 10
                    else:
                        missing_lists.append(curr_word)
                        listing_score -= 10
                    prev_word = curr_word
                    curr_word = ''
                elif (prev_word + ' ' + curr_word).lower() in listings:
                    if self.check_if_lists_added(paragraph[char_index + 1:]):
                        identified_lists.append(prev_word + ' ' + curr_word)
                        listing_score += 10
                    else:
                        missing_lists.append(prev_word + ' ' + curr_word)
                        listing_score -= 10
                    prev_word = curr_word
                    curr_word = ''
                else:
                    prev_word = curr_word
                    curr_word = ''
            else:
                curr_word = curr_word + char
        message = ''
        if len(missing_lists) > 0:
            message = 'Missing lists detected for listing words : ' + str(missing_lists)
        if listing_score > 0:
            listing_score = cfg.max_scores['listings']
        elif listing_score < 0:
            listing_score = 0
        return listing_score, "", message

    def check_if_lists_added(self, text):
        list_found = False
        is_space = False
        lists = []
        prev_text = ''
        curr_text = ''
        sub_text = ''
        sel_char = ''
        dot_counter = 0
        listings = cfg.listings
        for char_index, char in enumerate(text):
            if char == ' ' or char == '.' or char == ',':
                if curr_text.lower() in listings or (prev_text + ' ' + curr_text).lower() in listings:
                    break
                else:
                    if char == ' ':
                        is_space = True
                    else:
                        is_space = False
                    if curr_text == '&' or curr_text.lower() == 'and':
                        lists.append(sub_text)
                        txt = ''
                        sub_sub_index = char_index + 1
                        while sub_sub_index < len(text):
                            if text[sub_sub_index] != '.':
                                txt = txt + text[sub_sub_index]
                            else:
                                break
                            sub_sub_index += 1
                        lists.append(txt)
                        list_found = True
                        break
                    sub_text = sub_text + ' ' + curr_text
                    prev_text = curr_text
                    curr_text = ''
            else:
                is_space = False
            if not is_space:
                if char == '.' and char_index > 0 and not text[char_index - 1].isnumeric():
                    if dot_counter < 2:
                        dot_counter += 1
                    if dot_counter == 2:
                        break
                elif char == ',' and sel_char == '':
                    list_found = True
                    if dot_counter > 0:
                        dot_counter -= 1
                    sel_char = ','
                    lists.append(sub_text + ' ' + curr_text)
                    sub_text = ''
                elif char.isnumeric() and text[char_index + 1] == ')' and sel_char == '':
                    list_found = True
                    if dot_counter > 0:
                        dot_counter -= 1
                    sel_char = ')'
                    lists.append(sub_text + ' ' + curr_text)
                    sub_text = ''
                elif char.isnumeric() and text[char_index + 1] == '.' and sel_char == '':
                    list_found = True
                    if dot_counter > 0:
                        dot_counter -= 1
                    sel_char = '.'
                    lists.append(sub_text + ' ' + curr_text)
                    sub_text = ''
                elif char.isnumeric() and text[char_index + 1] == sel_char:
                    list_found = True
                    if dot_counter > 0:
                        dot_counter -= 1
                    lists.append(sub_text + ' ' + curr_text)
                    sub_text = ''
                elif char == sel_char:
                    list_found = True
                    if dot_counter > 0:
                        dot_counter -= 1
                    lists.append(sub_text + ' ' + curr_text)
                    sub_text = ''
                else:
                    curr_text = curr_text + char
        return list_found


    def count_nouns(self, text=None):
        tagged_words, tagged_words_count = self.get_pos_count(text)
        nouns_score = cfg.max_scores['nouns']
        allowed_dictionary = cfg.dictionary
        nouns = []
        allowed = []
        for idx, tagged_word in enumerate(tagged_words):
            print(tagged_word)
            noun_indices = self.get_word_index(tagged_word, text)
            for id, index in enumerate(noun_indices):
                temp_sentence = text[index:]
                if len(tagged_words) > idx + 1:
                    next_noun_indices = self.get_word_index(tagged_words[idx + 1],temp_sentence)
                    if len(next_noun_indices) > 0:
                        next_noun_index = next_noun_indices[0]
                        temp_sentence = temp_sentence[:next_noun_index]
                if len(temp_sentence) > 0 and ('1)' not in temp_sentence and '1.' not in temp_sentence) and tagged_word not in allowed and tagged_word not in nouns:
                    add_noun = True
                    for pre_allowed_word in allowed_dictionary:
                        if tagged_word in pre_allowed_word:
                            add_noun = False
                    if add_noun:
                        nouns.append(tagged_word)
                elif '1)' in temp_sentence or '1.' in temp_sentence:
                    nouns_score = nouns_score + 10
                    allowed.append(tagged_word)
                    if tagged_word in nouns:
                        nouns.remove(tagged_word)
        for noun in nouns:
            print(noun)
            nouns_score = nouns_score - 10
        message = ''
        if len(nouns) > 0:
            nouns_list = ','.join(nouns)
            message = "Entities such as ("+ nouns_list + ") could be defined further."

        if nouns_score < 0:
            nouns_score = 0
        elif nouns_score > cfg.max_scores['nouns']:
            nouns_score = cfg.max_scores['nouns']
        return nouns_score, "", message

    def get_text_stats(self,text):
        blob = TextBlob(text)
        total_sentences = len(blob.sentences)
        # print(total_sentences)
        requirement = textacy.preprocess_text(text, lowercase=True, no_urls=True)
        try:
            doc = textacy.Doc(requirement, lang='en_core_web_sm')
        except:
            doc = textacy.Doc(requirement, lang='en')
        text_stat = textacy.TextStats(doc)
        return text_stat


    def get_count_per_element(self,num,min,max):
        #split into ranges
        # range_ = max - min
        if min <= num <= max:
            return 2
        elif num < min:
            return 0
        elif num > max:
            return 1
        # range_arr_ = self.chunkIt(range(range_), 5)
        # index = self.in_range(num, range_arr_)
        # return index


    def get_sentences(self,text):
        sentence_count = 0
        sentence_map = {}
        text_sentences = nlp(text)
        for sentence in text_sentences.sents:
            sentence_map[sentence_count] = sentence.text
            sentence_count = sentence_count + 1
        return sentence_map


    def apply_rules(self,text, rule, inclusion=True):
        word = rule['word']
        corresponding_word = rule['corresponding_word']
        gap = rule['gap']

        if self.get_word_count(word,text) > 0:
            indices_ = self.get_word_index(word,text)
            for index in indices_:
                temp_sentence = self.get_next_n_words(word, text[index:], n=gap)
                if corresponding_word in temp_sentence[0]:
                    return True
        return False


    def get_next_n_words(self, word, text, n=5):
        words = re.compile(word+r'\s+((?:\w+(?:\s+|$)){1,'+str(n)+r'})').findall(text)
        return words

    def get_word_index(self,word, text):
        indices = []
        for char in ['@','#','$','+','=','(',')']:
            word = word.replace(char, '')
        if word.replace(' ', '') != '':
            for match in re.finditer(word, text.lower()):
                indices.append(match.start())
        return indices


    def get_word_count(self,word, text):
        word_occur_pd = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), text.lower()))
        return word_occur_pd


    def get_pos_count(self,text):
        tokenized_text = nltk.word_tokenize(text)
        tagged = nltk.pos_tag(tokenized_text)
        nouns_followed_by = cfg.nouns_followed_by
        tagged_words = []
        identified = []
        for id,word in enumerate(tagged):
            if word[1].startswith('NNP'):
                identified.append(word)
            if word[1].startswith('JJ') or word[1].startswith('VBN'):
                next_index = id + 1
                while next_index < len(tagged) and tagged[next_index][1].startswith('JJ'):
                    next_index = next_index + 1
                if next_index < len(tagged) and tagged[next_index][1].startswith('NN'):
                    identified.append(tagged[next_index][0])
            if word[1].startswith('NN'):
                next_index = id + 1
                while next_index < len(tagged) and tagged[next_index][1].startswith('JJ'):
                    next_index = next_index + 1
                if next_index < len(tagged) and tagged[next_index][1].startswith('NN'):
                    identified.append(tagged[next_index][0])
            if word[1].startswith('NN') and word[0] not in identified:
                noun = word[0]
                count = id
                while count+1 < len(tagged) and tagged[count+1][1].startswith('NN'):
                    noun = noun +' '+ str(tagged[count+1][0])
                    identified.append(str(tagged[count+1][0]))
                    identified.append(noun)
                    count = count+1
                if noun not in identified:
                    tagged_words.append(noun)
                    identified.append(noun)
        return tagged_words, len(tagged_words)


    def get_listing_texts(self, paragraph):
        listings = cfg.listings
        lists = []
        prev_word = ''
        curr_word = ''
        text = ''
        dot_counter = 0
        for char_index, char in enumerate(paragraph):
            if char == ' ':
                if curr_word.lower() in listings or (prev_word + ' ' + curr_word).lower() in listings:
                    text = paragraph[char_index + 1:]
                    selected_char = ''
                    sub_text = ''
                    sub_prev_word = ''
                    sub_curr_word = ''
                    for sub_index, sub_char in enumerate(text):
                        if sub_char == '.':
                            if dot_counter < 2:
                                dot_counter += 1
                            if dot_counter == 2:
                                break
                            else:
                                print(sub_text, '+++++++++')
                                sub_text = ''
                        elif sub_char == ',':
                            print(sub_text, '+++++++++')
                            sub_text = ''
                        else:
                            sub_text = sub_text + sub_char
                else:
                    prev_word = curr_word
                    curr_word = ''
            else:
                curr_word = curr_word + char

    # def chunkIt(self, seq, num):
    #     avg = len(seq) / float(num)
    #     out = []
    #     last = 0.0
    #     while last < len(seq):
    #         out.append(seq[int(last):int(last + avg)])
    #         last += avg
    #     return out
    #
    # def in_range(self, num_,range_arr_):
    #     index = 0
    #     is_in_range = False
    #     for x in range_arr_:
    #         if x.start < num_ <= x.stop:
    #             is_in_range = True
    #             return index
    #         index += 1
    #     return index if is_in_range else 1


if __name__ == '__main__':
    text = "A customer can request for a vehicle loan through the create loan module if he meets the preconditions defined. If the preconditions are satisfied, he shall be able to enter loan details otherwise he may not. An error message will appear if he doesn’t meet the criteria"
    text_utils= TextUtils()
    text_utils.measure_readability(text)

    # text = "A customer can request for a vehicle loan through the create loan module if he meets the preconditions defined. If the preconditions are satisfied, he shall be able to enter loan details otherwise he may not. An error message will appear if he doesn’t meet the criteria"
    word_rules =  cfg.word_rule
    inclusion_rules = word_rules['inclusions']
    exclusion_rules = word_rules['exclusions']
    for inclusion_rule in inclusion_rules:
        result = text_utils.apply_rules(text,inclusion_rule,inclusion=True)


