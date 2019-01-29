import csv
from typing import List

def write_csv(filename = "result.csv", parsed_doc_dicts: List):
    """ If csvfile is a file object, it should be opened with newline=''
    """
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ["Суд", "Дата приговора", "ФИО", "Судимость да/нет", "Отбывал ли ранее лишенеи свободы да/нет",
                      "Вид наркотика",	"Количество наркотика грамм", "Стоимость наркотика руб.", "Вид наказания (лишение свободы/ условное лишение свободы)",
                      "Срок наказания в месяцах", "Смягчающие обстоятельства", "Отягчающие обстоятельства", "Особый порядок да/нет", "Примечание"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for parsed_dict in parsed_doc_dicts:
            writer.writerow(parsed_dict)
        