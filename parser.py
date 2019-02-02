import argparse
import sys
import os
import docx
import logging 
from ner import EntityExtractor
import csv
from typing import Dict

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(levelname)s %(funcName)s %(message)s')

class ParsingHandler():
    def __init__(self, args):
        self.skips_n_reasons = {}
        self.args = args
        
        self.succ_counter = 0
        self.error_counter = 0
        
        self.process_files()
        self.report()
        
    def extract_text(self, filename):
        """ Format detection and text extraction as a string """
        target_path = self.args.target_dir + "/" + filename

        if filename.endswith(".txt"):
            with open(target_path, encoding='utf-8') as file:
                return "".join(file.read())

        if filename.endswith(".doc") or filename.endswith(".docx"):
            doc = docx.Document(target_path)
            return '\n'.join([para.text for para in doc.paragraphs])
        
        msg = "Target file format is not supported: {}, skipping file".format(filename)
        logger.critical(msg)
        self.skips_n_reasons.update({filename: msg})
                
    def write_csv(self, result: Dict):
        """ If csvfile is a file object, it should be opened with newline=''
        """
        file_exists = os.path.isfile(file_path)        
        with open(file_path, 'a', newline='') as csvfile:
            fieldnames = ['Суд', 'Дата приговора', 'ФИО', 'Смягчающие обстоятельства', 'Вид наказания', 'Особый порядок',
                          'Отбывал ли ранее лишение свободы', 'Судимость', 'Наркотики', 'Срок наказания в месяцах',
                          'Отягчающие обстоятельства']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if file_exists:
                writer.writeheader()
            writer.writerow(result)
        
    def write_error_log(error_dict):
        file_exists = os.path.isfile(self.args.log_file)        
        with open(self.args.log_file, 'a', newline='') as csvfile:
            fieldnames = ['filename', "error"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if file_exists:
                writer.writeheader()
            writer.writerow(error_dict)
            
    def process_files(self):
        for filename in os.listdir(self.args.target_dir):
            try:
                text = self.extract_text(filename)
                ex = EntityExtractor(text)
                self.write_csv(ex.summary_dict)
                if args.log_file:
                    self.write_erorr_log()
                self.succ_counter += 1
            except BaseException as e:
                self.error_counter += 1
                logger.error("Error while processing {} file: {}".format())
                self.write_error_log({filename: str(e)+str(e.args)})
     
    def report(self):
        self.logger.info(
            "Files processed: {}, errors(skipped): {}".format(
                self.succ_counter, self.error_counter))
    
    
if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Извлечение атрибутов приговоров из указанной папки в .csv файл. Допустимые форматы: .txt, .doc, docx')
    parser.add_argument('--target_dir', default="test_txt")
    parser.add_argument('--dest_file', default="result.csv")
    parser.add_argument('--log_file', default="") # acts as false with if
    args = parser.parse_args()
    ParsingHandler(args)