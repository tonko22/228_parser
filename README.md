# prigovor_parser
Случайной выборкой на официальных сайтах районных (городских) судов
общей юрисдикции было найдено и проанализировано 2389 приговоров по
части второй ст. 228 УК РФ за 2017–2018 годы в 46 субъектах РФ.
(см. файл result_analysis.ipynb)

Проект также содержит парсер атрибутов из обвинительных приговоров по статье 228 УК РФ. Проект предназначен для автоматизации сбора статистики.
Укажите путь к папке с файлами txt/doc/docx,
usage: parse.py [-h] [--target_dir /data] [--result_path [default: result.csv]] [--error_log_path [dafault: error_log.csv]]

