import configurations as configs
from bs4 import BeautifulSoup as bsoup
import re

class pre_process_text:

    def replace_required_tags(self, text):
        required_tags = configs.tags_replacer
        for index, tag in enumerate(required_tags):
            # text = text.lower().replace(tag, required_tags[tag])
            results = re.findall('<' + tag + '.*?>', text.lower())
            if len(results) > 0:
                for sub_index, sub_text in enumerate(results):
                    text = text.replace(sub_text, required_tags[tag])
        return text

    def remove_html_tags(self, text):
        text = bsoup(text, 'html.parser').text
        return text

    def remove_special_characters(self, text):
        special_chars = configs.spec_char_list
        for char in special_chars:
            text = text.lower().replace(char, '')
        text = self.remove_escape_characters(text=text)
        return text

    def remove_escape_characters(self, text):
        sentences = text.split('.')
        text = ''
        for sentence in sentences:
            if (sentence.__contains__('\\n') or sentence.__contains__('\\r')) and (
                    sentence.__contains__('#') or sentence.__contains__('*')):
                sentence = sentence.replace('\\n', ' ') if sentence.__contains__('\\n') else sentence
                sentence = sentence.replace('\\r', '') if sentence.__contains__('\\r') else sentence
                sentence = sentence.replace('#', '1)') if sentence.__contains__('#') else sentence
                sentence = sentence.replace('*', '1)') if sentence.__contains__('*') else sentence
                if sentence.count('1)') > 1:
                    sub_sentence = ''
                    for chr_idx, chr in enumerate(sentence):
                        if chr.isnumeric() and sentence[chr_idx + 1] == ')':
                            if sub_sentence != '':
                                sub_sentence = sub_sentence + '.1'
                            else:
                                sub_sentence = '1'
                        else:
                            sub_sentence = sub_sentence + chr
                    sentence = sub_sentence
            text = text + sentence + '.' if text != '' else sentence + '.'
        return text

    def replace_required_characters(self, text):
        required_chars = configs.char_replacer
        for index, chr in enumerate(required_chars):
            text = text.lower().replace(chr, required_chars[chr])
        return text

    def space_checker(self, text):
        space_check_list = configs.space_check_lst
        new_text = ''
        curr_word = ''
        cap_text = True
        for char_index, char in enumerate(text):
            if char in space_check_list:
                if curr_word != '':
                    cap_text = True
                    if new_text != '' and new_text[len(new_text) - 1] == ' ':
                        new_text = new_text + curr_word + char
                    elif new_text != '' and new_text[len(new_text) - 1] != ' ':
                        new_text = new_text + ' ' + curr_word + char
                    else:
                        new_text = curr_word + char
                    curr_word = ''
                else:
                    new_text = new_text + '. '
            elif char == ' ':
                if curr_word != '':
                    if new_text == '':
                        new_text = curr_word
                    else:
                        if new_text[len(new_text) - 1] == ' ':
                            new_text = new_text + curr_word
                        else:
                            new_text = new_text + ' ' + curr_word
                    curr_word = ''
            else:
                curr_word = curr_word + char
                if cap_text and curr_word != '':
                    cap_text = False
                    curr_word = curr_word[0].upper() + curr_word[1:]
                if char_index == len(text) - 1:
                    if new_text != '' and new_text[len(new_text) - 1] == ' ':
                        new_text = new_text + curr_word
                    elif new_text != '' and new_text[len(new_text) - 1] != ' ':
                        new_text = new_text + ' ' + curr_word
                    else:
                        new_text = curr_word
        print(new_text)
        return new_text