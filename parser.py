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
    log_path = "log.csv"
    def __init__(self, args):
        self.skips_n_reasons = {}
        self.args = args
        
        self.skipped_files = 0
        
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
                
    def write_result_csv(self, result: Dict):
        """ If csvfile is a file object, it should be opened with newline=''
        """
        file_exists = os.path.isfile(self.args.csv_path)        
        with open(self.args.csv_path, 'a', newline='') as csvfile:
            fieldnames = ["Ссылка", "Файл", 'Суд', 'Дата приговора', 'ФИО', 'Смягчающие обстоятельства', 'Вид наказания', 'Особый порядок',
                          'Отбывал ли ранее лишение свободы', 'Судимость', 'Наркотики', 'Срок наказания в месяцах',
                          'Отягчающие обстоятельства']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(result)
        
    def write_error_log(self, error_dict):
        file_exists = os.path.isfile(self.log_path)        
        with open(self.log_path, 'a', newline='') as csvfile:
            fieldnames = ['filename', "extractor_errors", "ner_errors"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(error_dict)
            
    def process_files(self):
        filenames = os.listdir(self.args.target_dir)
        self.total_files = len(filenames)
        for n, filename in enumerate(filenames):
            logger.info("Processing {}, ({}/{})".format(filename, n, self.total_files))
            
            error_dict = {"filename": filename,
            "extractor_errors": None,
            "ner_errors": None}
            
            try:
                text = self.extract_text(filename)
            except BaseException as e:
                logger.error("Error while extracting {}, skipping".format(e))
                error_dict["extractor_errors"] = e
                self.skipped_files += 1
                continue
                    
            ex = EntityExtractor(filename, text)
            if ex.errors:
                error_dict["ner_errors"] = e
                
            self.write_result_csv(ex.summary_dict)
            
            if self.args.write_logs:
                    self.write_error_log(error_dict)
                    
    def report(self):
        logger.info(
            "Files processed: {}, skipped: {}".format(
                self.total_files, self.error_counter))
    
    
if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Извлечение атрибутов приговоров из указанной папки в .csv файл. Допустимые форматы: .txt, .doc, docx')
    parser.add_argument('--target_dir', default="test_txt")
    parser.add_argument('--csv_path', default="result.csv")
    parser.add_argument('--write_logs', action="store_false")
    args = parser.parse_args()
    ParsingHandler(args)