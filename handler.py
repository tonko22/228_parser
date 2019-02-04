import sys
import os
import docx
import logging 
from ner import EntityExtractor
import csv
from typing import Dict
import re
from aiofile import AIOFile

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(levelname)s %(funcName)s %(message)s')


def assert_228(text):
    ''' Содержит ли текст приговора 228 ч. 2 '''
    pattern = r"преступлени(.*)?предусмотренн(.*)?((ч([. ]*)?|часть.? )2 ст([\w\. ]*)?228|228 (ч([.\- ]*)?|часть.? )2|228\..?2)"
    assert re.search(pattern, text), "228.2 not found, skipping"

class ParsingHandler():   
    result_fieldnames = ["Ссылка", "Файл", 'Суд', 'Дата приговора', 'ФИО',
                      'Смягчающие обстоятельства', 'Вид наказания', 'Особый порядок',
                      'Отбывал ли ранее лишение свободы', 'Судимость', 'Наркотики',
                      'Главный наркотик', 'Размер', 'Срок наказания в месяцах',
                      'Отягчающие обстоятельства']
    error_log_fieldnames = ['filename', "extractor_errors", "ner_errors"]
    
    def __init__(self, args):
        self.skips_n_reasons = {}
        self.args = args
        
        self.filenames = os.listdir(self.args.target_dir)
        self.total_files = len(self.filenames)
        
        self.skipped_files = 0   
        
        if not os.path.isfile(self.args.error_log_path):
            self.write_error_log_header()
        if not os.path.isfile(self.args.result_path):
            self.write_result_header()
        
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
    
    def write_result_header(self):
        with open(self.args.result_path, mode='a', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.result_fieldnames)
            writer.writeheader()
    
    def write_error_log_header(self):
        with open(self.args.error_log_path, mode='a', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.error_log_fieldnames)
            writer.writeheader()    
            
    def write_result_csv(self, result):
        """ If csvfile is a file object, it should be opened with newline=''
        """            
        with open(self.args.result_path, mode='a', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.result_fieldnames)
            writer.writerow(result)
            
    def write_error_log(self, error_log):            
        with open(self.args.error_log_path, mode='a', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.error_log_fieldnames)
            writer.writerow(error_log)
    
    def process_files(self):
        for n, filename in enumerate(self.filenames):
            logger.info("Processing {}, ({}/{})".format(filename, n, self.total_files))
            
            error_dict = {
                "filename": filename,
                "extractor_errors": None,
                "ner_errors": None,
            }
            
            try:
                text = self.extract_text(filename)
                assert_228(text)
            except BaseException as e:
                msg = "Error while reading file {}, skipping".format(str(e))
                logger.warning(msg)
                error_dict["extractor_errors"] = msg
                self.skipped_files += 1
                self.write_error_log(error_dict)
                continue
                    
            ex = EntityExtractor(filename, text)
            self.write_result_csv(ex.summary_dict)
            if len(ex.errors)>0:
                error_dict["ner_errors"] = ex.errors    
            
            if error_dict["extractor_errors"] or error_dict["ner_errors"]:
                self.write_error_log(error_dict)
                    
    async def process_async(self):
        async with AIOFile(self.args.result_path, mode='a', encoding='utf-8') as f:
            for n, filename in enumerate(self.filenames):
                error_dict = {
                "filename": filename,
                "extractor_errors": None,
                "ner_errors": None,
                }
                
                try:
                    text = self.extract_text(filename)
                    assert_228(text)
                except BaseException as e:
                    msg = "Error while reading file {}, skipping".format(str(e))
                    logger.warning(msg)
                    error_dict["extractor_errors"] = msg
                    self.skipped_files += 1
                    self.write_error_log(error_dict)
                    continue
                
                ex = EntityExtractor(filename, text)
                values = [ex.summary_dict.get(k) for k in self.result_fieldnames]
                f.write(",".join(map(str, values))+"\n")
                #await afp.fsync()    
    
    def report(self):
        logger.info(
            "Files processed: {}, skipped: {}".format(
                self.total_files, self.skipped_files))

        