import glob
import argparse
import sys
import os
import io
import docx

from ner import prigovorParser

def docx_get_text(filename):
    """ Получение текста из файла docx """
    try:
        doc = docx.Document(filename)
        return '\n'.join([para.text for para in doc.paragraphs])
    except:
        # open file and read contents
        with io.open(filename, encoding='utf-8') as file:
            text = file.read()

        # return text
        return text

def txt_get_text(filename):
    """ Получение содержимого текстового файла """

    # open file and read contents
    with io.open(filename, encoding='utf-8') as file:
        text = file.read()

    # return text
    return text

def is_valid_doc(filename):
    return True
    
if __name__=="__main__":

    # iterate all files in directory
    for filename in os.listdir("."):

        # if it is text file
        if filename.endswith(".txt"):
           
            # get text file
            text = txt_get_text(filename)

        # if it is docx file
        elif filename.endswith(".doc"):

            # get docx content
            text = docx_get_text(filename)

        # no way, continue search
        else: continue

        # parse text
        p = prigovorParser(text)

        # print entities
        print(p.summary_dict)