import glob
import argparse
import sys
import os
import docx
import logging 
from ner import prigovorParser
import csv
from typing import Dict

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(levelname)s %(funcName)s %(message)s')


def extract_text(filename, target_format="txt"):
    """ Получение текста из файла """
    if target_format=="doc":
        doc = docx.Document(filename)
        return '\n'.join([para.text for para in doc.paragraphs])
    if target_format=="txt":
        with open(filename, encoding='utf-8') as file:
            return file.read()

        
def write_csv(result: Dict, file_path="result.csv"):
    """ If csvfile is a file object, it should be opened with newline=''
    """
    write_header = False
    if not os.path.isfile(file_path):
        write_header = True
            
    with open(file_path, 'a', newline='') as csvfile:
        fieldnames = ['Суд', 'Дата приговора', 'ФИО', 'Смягчающие обстоятельства', 'Вид наказания', 'Особый порядок',
                      'Отбывал ли ранее лишение свободы', 'Судимость', 'Наркотики', 'Срок наказания в месяцах',
                      'Отягчающие обстоятельства']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(result)
    
    
if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Извлечение атрибутов приговора в .csv файл')
    parser.add_argument('--target_dir', default="test_txt")
    args = parser.parse_args()
    
    skips_n_reasons = {}
    for filename in os.listdir(args.target_dir):
        target_path = args.target_dir + "/" + filename
        if filename.endswith(".txt"):
            target_format = "txt"
        elif filename.endswith(".doc") or filename.endswith(".docx"):
            target_format = "doc"
        else:
            logger.critical("Target file format is not supported: {}, skipping file".format(filename))
            skips_n_reasons.update({filename: "unsupported format"})
            continue

        try: 
            text = extract_text(target_path, target_format)
            parser = prigovorParser(text)
            logger.info("Parsing result for {}:\n{}".format(filename, parser.summary_dict))
            write_csv(parser.summary_dict)
        except BaseException as e:
            logger.error("Error while parsing {}: {}, skipping file".format(filename, e))
            skips_n_reasons.update({filename: e})
            
    logger.info("Skipped {} files: {}".format(len(skips_n_reasons.keys()), skips_n_reasons))