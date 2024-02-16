import csv
import os

folder_path = r'D:\Code\convertible_bond\Convertible_bonds\data1'
input_path = r'D:\Code\convertible_bond\Convertible_bonds\data2'
for file_name in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file_name)
    input_file_path = os.path.join(input_path, file_name)

    with open(file_path, 'r', encoding='utf-8') as infile, open(input_file_path, 'w', newline='',
                                                                encoding='utf-8') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        for row in reader:
            new_row = [cell if cell != '--' else 'null' for cell in row]
            writer.writerow(new_row)
