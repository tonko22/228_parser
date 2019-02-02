import csv
from typing import Dict
import os.path

def write_csv(result: Dict, filename="result.csv"):
    """ If csvfile is a file object, it should be opened with newline=''
    """
    with open(filename, 'a', newline='') as csvfile:
        if not os.path.isfile(fname):
            fieldnames = ["Суд", "Дата приговора", "ФИО"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
        writer.writerow(parsed_dict)
        