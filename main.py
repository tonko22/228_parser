import argparse
from handler import ParsingHandler
import asyncio

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Извлечение атрибутов приговоров из указанной папки в .csv файл. Допустимые форматы: .txt, .doc, docx')
    parser.add_argument('--target_dir', default="data/part2")
    parser.add_argument('--result_path', default="result.csv")
    parser.add_argument('--error_log_path', default="error_log.csv")
    parser.add_argument('--async', action="store_true") # default false
    args = parser.parse_args()
    h = ParsingHandler(args)
    if args.async:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(h.process_async())
    else:
        h.process_files()
        h.report()
