import glob
import argparse
import sys
import os
import docx
import logging 
from ner import prigovorParser

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(levelname)s %(funcName)s %(message)s')


def extract_text(filename, target_format="txt"):
    """ Получение текста из файла """
    if target_format=="doc"
        doc = docx.Document(filename)
        return '\n'.join([para.text for para in doc.paragraphs])
    except:
        with open(filename, encoding='utf-8') as file:
            return file.read() 
    
if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Извлечение атрибутов приговора в .csv файл')
    parser.add_argument('--target_dir', default="test_txt")
    args = parser.parse_args()
    
    for filename in os.listdir(args.target_dir):
        if filename.endswith(".txt"):
            target_format = "txt"
        if filename.endswith(".doc") or filename.endswith(".docx"):
            target_format = "doc"
        else:
            logger.critical("Target file format is not supported: {}, skipping file".format(filename))
            continue
        try: 
            text = txt_get_text(filename, target_format)
            p = prigovorParser(text)
            logger.info("Parsing result for {}:\n{}".format(filename, p.summary_dict))
        except BaseException as e:
            logger.error("Error while parsing {}: {}, skipping file".format(filename, e))