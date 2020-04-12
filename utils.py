from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO
import re

from math import *

sectionRE = re.compile('section\s+(?:\d+|[A-Z]+)\s+', re.IGNORECASE)
asDefinedRe = re.compile('\as defined in section\s+\d*\D*\)', re.IGNORECASE)
moneyRE = re.compile('(\(\D{0,3}\$*[\d,]+\))', re.IGNORECASE)
section_number_re = re.compile('\D+\s+(\d{1,2})', re.IGNORECASE)

exclusionBag = ['notcovered', 'exclusion', 'notcover']
start = ['other than', 'not include', 'except', 'excluding', 'unless']
end = [')']
removeNounsFromDesc = ['airport']



class Utils():

    @staticmethod
    def similarity_matrix_score(lines, bag, model):
        bag = [Utils.clean_text_for_embedding(i) for i in bag]
        lines = [Utils.clean_text_for_embedding(i) for i in lines]
        embed_set1 = model.embed_sentences(bag)
        embed_set2 = model.embed_sentences(lines)
        score = cosine_similarity(embed_set2, embed_set1)
        return score



    @staticmethod
    def merge_dict(dict_1, dict_2):
        for key, value in dict_1.items():
            if key in dict_2:
                dict_2[key].extend(value)
            else:
                dict_2[key] = value
        return dict_2

    @staticmethod
    def deep_clean(item):
        if isinstance(item, str):
            return item.replace(' ', '').replace('\n', '').replace('\t', '').lower()
        elif isinstance(item, list):
            return [txt.replace(' ', '').replace('\n', '').replace('\t', '').lower() for txt in text]



    @staticmethod
    def create_tokenizer_score(train_series, new_series, model):
        train_tfidf = model.embed_sentences(train_series)
        new_tfidf = model.embed_sentence(new_series)

        score = cosine_similarity(new_tfidf, train_tfidf)[0]
        return score

    @staticmethod
    def create_tokenizer_score_tfidf(train_series, new_series, tokenizer):
        train_tfidf = tokenizer.transform(train_series)
        new_tfidf = tokenizer.transform([new_series])
        score = cosine_similarity(new_tfidf, train_tfidf)[0]
        return score
    @staticmethod
    def clean_text_for_embedding(text):
        text = text.replace('/', ' ')
        tokens = word_tokenize(text)
        # convert to lower case
        tokens = [w.lower() for w in tokens]
        # remove punctuation from each word
        table = str.maketrans('', '', string.punctuation)
        stripped = [w.translate(table) for w in tokens]
        # remove remaining tokens that are not alphabetic
        words = [word for word in stripped if word.isalpha()]
        # filter out stop words
        stop_words = set(stopwords.words('english'))
        words = [w for w in words if not w in stop_words]
        cleanedText = ' '.join(words)
        return (cleanedText.replace('\n', ''))

    @staticmethod
    def splitter(n, s):
        pieces = s.split()
        return (" ".join(pieces[i:i + n]) for i in range(0, len(pieces), n))

    @staticmethod
    def pdf_to_html(path, codec='utf-8'):
        rsrc_mgr = PDFResourceManager()
        ret_str = BytesIO()
        la_params = LAParams()
        device = HTMLConverter(rsrc_mgr, ret_str, codec=codec, laparams=la_params)
        fp = open(path, 'rb')
        interpreter = PDFPageInterpreter(rsrc_mgr, device)
        caching = True
        pge_no = set()
        for page in PDFPage.get_pages(fp, pge_no, maxpages=0, password='', caching=caching,
                                      check_extractable=True):
            interpreter.process_page(page)

        text = ret_str.getvalue().decode()
        fp.close()
        device.close()
        ret_str.close()
        return text

    @staticmethod
    def text_2_int(text_num, num_words={}):
        if not num_words:
            units = [
                "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
                "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
                "sixteen", "seventeen", "eighteen", "nineteen",
            ]

            tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

            scales = ["hundred", "thousand", "million", "billion", "trillion"]

            for idx, word in enumerate(units):  num_words[word] = (1, idx)
            for idx, word in enumerate(tens):       num_words[word] = (1, idx * 10)
            for idx, word in enumerate(scales): num_words[word] = (10 ** (idx * 3 or 2), 0)

        ordinal_words = {'first': 1, 'second': 2, 'third': 3, 'fifth': 5, 'eighth': 8, 'ninth': 9, 'twelfth': 12}
        ordinal_endings = [('ieth', 'y'), ('th', '')]

        text_num = text_num.replace('-', ' ')

        current = result = 0
        cur_string = ""
        on_number = False
        for word in text_num.split():
            if word in ordinal_words:
                scale, increment = (1, ordinal_words[word])
                current = current * scale + increment
                if scale > 100:
                    result += current
                    current = 0
                on_number = True
            else:
                for ending, replacement in ordinal_endings:
                    if word.endswith(ending):
                        word = "%s%s" % (word[:-len(ending)], replacement)

                if word not in num_words:
                    if on_number:
                        cur_string += repr(result + current) + " "
                    cur_string += word + " "
                    result = current = 0
                    on_number = False
                else:
                    scale, increment = num_words[word]

                    current = current * scale + increment
                    if scale > 100:
                        result += current
                        current = 0
                    on_number = True

        if on_number:
            cur_string += repr(result + current)

        return cur_string





