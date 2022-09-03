# 2022/09/03 EDITED

import json

with open("row_data.txt", 'r', encoding="UTF-8") as f:
    lines = f.readlines()
    result = {}

    for i,line in enumerate(lines):
        if 65 <= ord(line[0]) <= 90:
            pivot = line.find(' ')
            if pivot == -1:
                building_code = line.strip()
            else:
                building_code = line[:pivot]
        else:
            pivot = line.index('-')
            if len(line[:pivot].strip()) == 0:
                continue
            building_number = line[:pivot].strip()

            parent_building_code = list(result.keys())[-1].split('-')[0]
            building_code = parent_building_code + '-' + building_number

            result[parent_building_code]['child'].append(building_code)

        if pivot >= 0:
            info = line[pivot + 1:].strip()
            building_name_KR = info[:info.index('(') - 1]
            building_name_EN = info[info.index('(') + 1:info.index(')')]
        else:
            building_name_KR = building_name_EN = ""

        result[building_code] = {"KR": building_name_KR, "EN": building_name_EN, 'child':[]}

with open('building_names.json', 'w') as f:
    json.dump(result, f, indent=2)

'''for i in result:
    print(i, '/', result[i]['KR'], '/', result[i]['EN'])'''