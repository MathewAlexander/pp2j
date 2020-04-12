
from bs4 import BeautifulSoup
import re
import numpy as np
from statistics import mode, mean
from utils import Utils as Ut


sectionRE = re.compile('Section\s+(?:\d+|[A-Z]+)\s+')
sectionRECaps = re.compile('SECTION\s+(?:\d+|[A-Z]+)\s+')

pointsRE = re.compile('(\s*\([a-z]{1,3}\))')
alphabetcheckRE = re.compile('[a-z]', re.IGNORECASE)

footnote_char = ['TM', 'page']
bag_subhead = ['notcover', 'notpay', 'exclusion', 'condition']
bag = ["Related Work", "Introduction", " Conclusion", "Experiments"]


class Htmltojson():

    @staticmethod
    def get_json(html, model):
        # LossRE=re.compile(LossRE_string,re.IGNORECASE )
        soup = BeautifulSoup(html, 'html5lib')
        font_dict = {}

        for divs in soup.findAll('div'):
            for j in divs.find_all('span'):
                j_string = str(j)
                font_size_list = re.findall(r'font-size:(\d*)px">', j_string)
                if font_size_list:
                    font_size = int(font_size_list[0])

                r_j_string = j_string[j_string.rfind('font-family:')+15:]
                stylej = r_j_string[:r_j_string.find(';')-1]

                if j.text.isupper():
                    upper = True
                else:
                    upper = False
                font_spec = (font_size, stylej, upper)

                clean_text = Ut.deep_clean(j.text)
                if font_spec not in font_dict:
                    font_dict[font_spec] = []
                elif clean_text and len(clean_text) > 5:
                    font_dict[font_spec].append(j.text)

        font_num_dict = {key: len(value) for key, value in font_dict.items() if len(value) < 600}
        keys_relevant = list(font_num_dict.keys())
        font_dict = {key: value for key, value in font_dict.items() if key in keys_relevant and value}
        score_dict = {}

        for key, value in font_dict.items():
            score = Ut.similarity_matrix_score(value, bag, model)
            score = score.flatten()
            l = len(score)
            tot_score = np.sum(score)/l

            if key[2]:
                tot_score = tot_score+0.01

            score_dict[key] = tot_score

        max_key = max(score_dict, key=score_dict.get)

        Benefit_dict = {}
        current_head = ''
        k = 0
        Bold = False
        prev_font_size = 8
        sub_head = None
        prev_head = 'not a heading'
        for divs in soup.findAll('div'):
            for j in divs.find_all('span'):
                k += 1

                j_string = str(j)

                font_size_list = re.findall(r'font-size:(\d*)px">', j_string)
                if font_size_list:
                    font_size = int(font_size_list[0])

                r_j_string = j_string[j_string.rfind('font-family:')+15:]
                style_j = r_j_string[:r_j_string.find(';')-1]
                text = j.text

                if j.text.isupper():
                    upper = True
                else:
                    upper = False

                if 'Bold' in str(j):
                    Bold = True
                else:
                    Bold = False
                font_spec = (font_size, style_j, upper)
                clean_text = Ut.deep_clean(text)
                sub_head_flags = list(filter(lambda x: x in clean_text, bag_subhead))

                if max_key == font_spec and not sub_head_flags:
                    current_head = text

                    if prev_head not in current_head:

                        sub_head = current_head

                    if current_head not in Benefit_dict:
                        Benefit_dict[current_head] = {sub_head: []}
                    else:
                        current_head = current_head+str(k)
                        Benefit_dict[current_head] = {sub_head: []}
                    prev_head = current_head

                if font_size > prev_font_size and Bold and current_head and current_head != text and len(Ut.deep_clean(text)) > 6:
                    print(sub_head)

                    sub_head = text

                if sub_head:
                    if sub_head not in Benefit_dict[current_head]:
                        Benefit_dict[current_head][sub_head] = []

                if current_head and Ut.deep_clean(text) and sub_head:
                    try:

                        Benefit_dict[current_head][sub_head].append(text)
                    except:

                        pass

                prev_font_size = font_size

        for section, value in Benefit_dict.items():
            for subhead, sent_list in value.items():
                sent = (' ').join(sent_list)
                sent = Ut.text_2_int(sent.replace('/n', '.').replace(';', '.').replace(':', '.'))
                sent = re.sub(pointsRE, '.', sent)
                sent = sent.split('.')
                value[subhead] = sent

        prev_head = 'not a heading'
        to_delete = []
        for head, value in Benefit_dict.items():
            if prev_head in head:
                Benefit_dict[prev_head] = Ut.merge_dict(Benefit_dict[prev_head], value)
                to_delete.append(head)
            prev_head = head
        [Benefit_dict.pop(key) for key in to_delete]
        # Benefit_dict={key:value for key,value in Benefit_dict.items() if len(LossRE.findall(key.replace('\n',' ').replace('  ',' ').replace('\t',' '))) > 0 }

        return Benefit_dict
