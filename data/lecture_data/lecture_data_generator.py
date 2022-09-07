# 2022/09/07 EDITED
import json
import xlrd
import os

def read_lecture_data(data_folder):
    path = ""
    data_file = os.listdir(data_folder)

    if len(data_file):
        for i in range(len(data_file)):
            target_path = data_folder + '/' + data_file[i]
            if os.path.isfile(target_path) and target_path.endswith('.xls'):
                path = target_path

            if i == len(data_file) - 1 and path == "":
                raise Exception(
                    "Data File Not Found!\n\tFollow the instruction in 'data/README.md' to download the Data File.")
    else:
        raise Exception("Data File Not Found!\n\tFollow the instruction in 'data/README.md' to download the Data File.")

    wb = xlrd.open_workbook(path)
    ws = wb.sheet_by_index(0)

    lecture_list = {}

    for i in range(2, ws.nrows):
        row = ws.row_values(i)
        code = row[5]

        # Key:Lecture
        if not code in lecture_list.keys():
            credit = (float(row[11].split(':')[2]), int(row[10]))
            lecture_list[code] = {"code":code, "lecture_name":row[8], "credit":credit, "lecture_info":row[:7] + row[8:12]}
            lecture_list[code]["classes"] = []
        # Lecture:cls (list)
        cls = {"name":row[7].strip(), "lecture_name":row[8], "professor":row[12], "capacity":int(row[15]), "enrolled":int(row[16]), "lecture_time":row[17], "classroom":row[18], "class_info":row[12:]}
        lecture_list[code]["classes"].append(cls)

    with open(data_folder+'/lecture_data/lecture_list.json', 'w') as f:
        json.dump(lecture_list, f, indent=2)

if __name__ == "__main__":
    pass