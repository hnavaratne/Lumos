
import textacy
import spacy
nlp = spacy.load('en_core_web_sm')
from textblob import TextBlob
import configs as cfg
import re
import nltk

VOCABULARY = cfg.word_list

OUTPUT_MESSAGES = {
    'generalities': 'Generalities (i.e about, almost, bad, close, good, many, most, timely) weaken the specification. Higher the count, Lower the specification.',
    'incomplete': 'The specification of requirements is not fully developed or provides a basis for expansion or addition of new requirements at a later date. Higher the count, Lower the Specification Quality',
}

NEGATIVE_CATEGORIES = ['generalities', 'incomplete']

class TextUtils:

    def get_word_list_score(self, requirement):
        word_list_score = 0
        words_list = []
        for category in VOCABULARY.keys():
            occurence, words = self.getCount(category,requirement)
            for i in range(occurence):
                word_list_score = word_list_score - 20
            words_list = words_list + words

        message = ''
        if len(words_list) > 0:
            words_str = ','.join(words_list)
            message = "Avoid using words such as " + words_str + ", they end to decrease the clarity of the requirement."
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
        word_count_score = 0
        min_word_count = cfg.word_count['min']
        max_word_count = cfg.word_count['max']

        sentences_ = self.get_sentences(text)
        word_counts = []
        short_sentences = []
        long_sentences = []
        for id, sentence in sentences_.items():
            text_stat = self.get_text_stats(sentence)
            word_count = text_stat.n_words
            word_rating = self.get_count_per_element(word_count, min_word_count, max_word_count)
            word_counts.append(word_rating)
            if word_rating == 0:
                short_sentences.append(sentence)
            elif word_rating == 1:
                long_sentences.append(sentence)

        for count in word_counts:
            if count == 0 or count == 1:
                word_count_score = word_count_score - 5
        message = ''
        if len(short_sentences) > 0:
            short_list = ','.join(short_sentences)
            message = "Some sentences such as ("+short_list+") contain too few words. Use longer sentences to clearly describe the requirement."
        if len(long_sentences) > 0:
            long_list = ','.join(long_sentences)
            message = message + "Sentences such as ("+long_list+") are too long. They could complicate the requirement and decrease clarity. Please use fewer words to clearly describe the requirement." \
                                  "Recommended to use between " + str(min_word_count) + " to " + str(
                        max_word_count) + " words per average sentence in the description."

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

    def sentence_count_rating(self, text=None):
        words_str = None
        message = []
        sentence_count_score = 0

        min_sentence_count = cfg.sentence_count['min']
        max_sentence_count = cfg.sentence_count['max']

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
            sentence_count_score = -10

        return sentence_count_score,message
        # sentence_count_rating = 5 if sentence_count_rating == 2 else 1
        # return sentence_count_rating,"",message
        # message.append(self.get_sentence_message(sentence_count_range))
        # return overall_rating,words_str,message

    def count_references(self, text=None):
        references = cfg.references
        reference_score = 0
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
        return reference_score,"",message

    def count_nouns(self, text=None):
        tagged_words, tagged_words_count = self.get_pos_count(text, 'NN')
        nouns = []
        nouns_score = 0
        for tagged_word in set(tagged_words):
            print(tagged_word)
            count = self.get_word_count(tagged_word, text)
            if count < 2:
                nouns.append(tagged_word)

        for noun in nouns:
            print(noun)
            nouns_score = nouns_score - 10
        message = ''
        if len(nouns) > 0:
            nouns_list = ','.join(nouns)
            message = "Entities such as ("+ nouns_list + ") could be defined further."
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
        for match in re.finditer(word, text.lower()):
            indices.append(match.start())
        return indices

    def get_word_count(self,word, text):
        word_occur_pd = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), text.lower()))
        return word_occur_pd

    def get_pos_count(self,text, pos_tag):
        tokenized_text = nltk.word_tokenize(text)
        tagged = nltk.pos_tag(tokenized_text)
        tagged_words = []
        identified = []
        for id,word in enumerate(tagged):
            if word[1].startswith(pos_tag) and word[0] not in identified:
                noun = word[0]
                identified.append(noun)
                count = id
                while count+1 < len(tagged) and tagged[count+1][1].startswith(pos_tag):
                    noun = noun +' '+ str(tagged[count+1][0])
                    identified.append(str(tagged[count+1][0]))
                    count = count+1
                tagged_words.append(noun)
        return tagged_words, len(tagged_words)

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


