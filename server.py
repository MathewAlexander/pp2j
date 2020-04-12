
from flask import Flask, request, send_file, send_from_directory
import os
import json
from utils import Utils as Ut


from load import *


# import utils
# from utils import *
from io import StringIO
from bs4 import BeautifulSoup
from tika import parser
import itertools
from itertools import chain


from benefits import Htmltojson as Hj


app = Flask(__name__)
UPLOAD_FOLDER = 'Files'
PRODUCT_FILES = 'ProductFiles'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PRODUCT_FILES'] = PRODUCT_FILES
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists(app.config['PRODUCT_FILES']):
    os.makedirs(app.config['PRODUCT_FILES'])

global model
model = init()


def main(file_path):

    html = Ut.pdf_to_html(file_path, 'html')

    doc_dict = Hj.get_json(html, model)

    return json.dumps(doc_dict)


if __name__ == "__main__":

    app.run(debug=True, host='0.0.0.0', port=9080)
