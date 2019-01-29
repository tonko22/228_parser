import csv
from typing import List

def write_csv(parsed_doc_dicts: List, filename="result.csv"):
    """ If csvfile is a file object, it should be opened with newline=''
    """
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ["Суд", "Дата приговора", "ФИО"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for parsed_dict in parsed_doc_dicts:
            writer.writerow(parsed_dict)
        