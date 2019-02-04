import argparse
from handler import ParsingHandler


        
if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Извлечение атрибутов приговоров из указанной папки в .csv файл. Допустимые форматы: .txt, .doc, docx')
    parser.add_argument('--target_dir', default="test_txt")
    parser.add_argument('--result_path', default="result.csv")
    parser.add_argument('--error_log_path', default="error_log.csv")
    args = parser.parse_args()
    h = ParsingHandler(args)
    h.process_files()
    h.report()
    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(h.async_processor())
    





    