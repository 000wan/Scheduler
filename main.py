# =========================
#  'Scheduler' by 000wan
# =========================
# Description :
#    University Schedule Generator
# History :
#    2022/08/09 : Start development with python
#    2022/08/10 ~ 2022/08/14 : Complete search algorithm using dp
#    2022/08/15 ~ 2022/08/29 : Generate time-table image
#    2022/08/31 ~ 2022/09/07 : Enhance OOP
#    2022/09/07 ~ Current : Add new feature: distance among buildings

import matplotlib

import os
import time as current_time

# import data, result folder
import data
import result

line_string = "=========================\n"
day_label_KR = ['월', '화', '수', '목', '금', '토', '일']
day_label_EN = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
colors = matplotlib.cm.get_cmap('Pastel1').colors + matplotlib.cm.get_cmap('Pastel2').colors    # Pastel colors

lecture_list = {}  # 과목코드:Lecture 리스트
building_data = {}  # 건물번호:data

def class_building(classroom):
    if len(classroom):
        if classroom[0] == '(':
            building = classroom[1:classroom.index(')')]
            return building
    return ''

def time_stock(period):  # lecture time text to float list
    res = list()

    for p in period.split('\r\n'):
        if p:
            items = p.split(' ')
            day = day_label_KR.index(items[0])
            times = items[1].split('~')

            # day,time -> 00.00 ~ 7*24.00
            # 00:00~24:00 -> 00.00 ~ 24.00 (float)
            start = 24 * day + float(times[0].split(':')[0]) + float(times[0].split(':')[1]) / 60
            end = 24 * day + float(times[1].split(':')[0]) + float(times[1].split(':')[1]) / 60

            res.append((start, end))

    return res

def is_time_intersect(list1, list2):    # compare two time stock lists (can be tuple)
    for t1 in list1:
        for t2 in list2:
            if t1[0] <= t2[0] < t1[1] or t2[0] <= t1[0] < t2[1]: # whether two time stock intersects
                return True
    return False


class Lecture:
    color = None

    def __init__(self, code, lecture_name, credit, lecture_info):
        self.code = code  # 과목번호
        self.lecture_name = lecture_name  # 과목명
        self.credit = credit  # 학점 (z=학점+AU*i)
        self.classes = []  # 분반
        self.lecture_info = lecture_info

    def __str__(self):
        return self.code


class Class:
    def __init__(self, name, lecture_name, professor, capacity, enrolled, lecture_time, classroom, class_info):
        self.name = name  # 분반명
        self.lecture_name = lecture_name  # 강의명
        self.professor = professor  # 담당교수
        self.capacity = capacity  # 정원
        self.enrolled = enrolled  # 수강인원
        self.lecture_time = lecture_time  # 강의시간 (type:int list)
        self.classroom = classroom  # 강의실
        self.building = class_building(classroom)  # 강의실 건물
        self.class_info = class_info

    def __str__(self):
        if self.name == '': return 'Staff'
        else:   return self.name


class TimeTable:
    def __init__(self, time_table_dict):
        self.dict = time_table_dict
        credit = complex(0,0)
        for lec in time_table_dict:
            credit += lecture_list[lec].credit
        self.credit = credit

    def convert_to_Schedule(self):
        time_table = self.dict
        block_list = list()

        for lec_code in time_table:
            lec = lecture_list[lec_code]
            classes = time_table[lec_code]
            cls = classes[0]
            times = cls.lecture_time

            for timeStock in times:
                block = result.Block(time=timeStock, color=lec.color)

                if len(classes) == 1:
                    # 부제목: `{교수명} ({분반명})`
                    sub_title = cls.professor + ' (' + str(cls) + ')'

                    # get classroom number
                    clsroom = cls.classroom.strip()
                    try:
                        building_string = f'({ cls.building }){ building_data[cls.building]["KR"] }'

                        if clsroom.startswith(building_string):
                            room_number = clsroom[len(building_string):]

                            # Info: `{건물코드} {호수}`
                            info_text = cls.building + ' ' + room_number
                            if len(info_text) > 10 and not '\n' in info_text:   # break in ten characters
                                info_text = info_text[:10] + '\n' + info_text[10:].strip()
                        else:
                            raise
                    except:
                        info_text = cls.building
                else:
                    classes = list(map(str, time_table[lec_code]))
                    sub_title = '(' + (', '.join(classes)) + ')'
                    info_text = cls.building

                block.title = cls.lecture_name
                block.sub_title = sub_title
                block.info = info_text

                block_list.append(block)

        return result.Schedule(block_list)


# 상태:(남은 신청 과목(tuple), 이미 사용한 시간(tuple)) -> 결과:해당 상태에서 가능한 강의 조합 memoization
memo = {}

# dp 탐색 함수
def search(enroll_list, used_time, remain_credit, necessary_list, selected_classes):
    # enroll_list:tuple, used_time:tuple, remain_credit:int, necessary_list:list, selected_classes:list
    global memo
    if not enroll_list in memo.keys():
        memo[enroll_list] = {}
    if not used_time in memo[enroll_list].keys():
        memo[enroll_list][used_time] = []

    if len(memo[enroll_list][used_time]):
        return memo[enroll_list][used_time]  # memoization
    if len(enroll_list) == 0:
        if remain_credit <= 0:
            memo[enroll_list][used_time].append({})
            return memo[enroll_list][used_time]
        else:
            return 0

    res = []
    if remain_credit <= 0 and len(necessary_list) == 0:
        res.append({})

    lec = enroll_list[0]
    for cls in selected_classes[0][1]:
        if not is_time_intersect(used_time, cls.lecture_time):
            new_used_time = list(used_time) + cls.lecture_time
            new_used_time.sort()

            '''new_necessary_list = list(necessary_list)
            if lec in new_necessary_list:
                new_necessary_list.remove(lec)'''

            # next search
            successor = search(enroll_list[1:], tuple(new_used_time), remain_credit - lec.credit.real,
                               necessary_list[1:], selected_classes[1:])
            if isinstance(successor, list):
                for i in successor:
                    flag = True
                    for j in res:
                        if len(j):
                            recorded = dict(j)
                            rec_lec = recorded.pop(str(lec), None)

                            # check same-time and same-name classes
                            if recorded == i and not rec_lec is None:
                                if rec_lec[0].lecture_time == cls.lecture_time and rec_lec[0].lecture_name == cls.lecture_name:
                                    if cls not in rec_lec:
                                        j[str(lec)].append(cls)
                                    flag = False
                                    break
                    if flag:
                        # res = list( dict(lec: [classes]) )
                        new_res = dict(i)
                        new_res[str(lec)] = [cls]
                        res.append(new_res)
    # without lec search
    if lec not in necessary_list:
        successor = search(enroll_list[1:], used_time, remain_credit, necessary_list, selected_classes[1:])
        if isinstance(successor, list):
            res = res + successor

    memo[enroll_list][used_time] = res
    return memo[enroll_list][used_time]

#
# Ref : https://api.ncloud-docs.com/docs/
#       https://velog.io/@choonsik_mom/Naver-API%EB%A1%9C-%EA%B8%B8%EC%B0%BE%EA%B8%B0with-python
def find_route():
    pass


# load 'total courses' data
def load_lecture_data(data_folder):
    json_path = data_folder + "/lecture_list.json"

    if not os.path.exists(json_path):
        data.read_lecture_data("data")  # lecture_data_generator.py

    with open(json_path) as f:
        ldat = data.json.load(f)

    lecture_list = {}

    for code in ldat:
        # Lecture 생성
        lec = ldat[code]
        credit = complex(lec["credit"][0], lec["credit"][1])
        lecture_list[code] = Lecture(code, lec["lecture_name"], credit, lec["lecture_info"])

        for cls in lec["classes"]:
            # Class 생성
            lec_time = time_stock(cls["lecture_time"])
            new_cls = Class(cls["name"], cls["lecture_name"], cls["professor"], cls["capacity"], cls["enrolled"], lec_time, cls["classroom"], cls["class_info"])
            lecture_list[code].classes.append(new_cls)

    return lecture_list

# load campus building names (json)
def load_campus_data(data_folder):
    json_path = data_folder + "/building_data.json"

    if not os.path.exists(json_path):
        txt_path = data_folder + "/row_data.txt"
        if not os.path.exists(txt_path):
            raise Exception("Campus Data Not Found!")
        else:
            data.generate_json(data_folder, data.read_txt(txt_path))    # load_building_data.py

    with open(json_path) as f:
        building_list = data.json.load(f)

    return building_list


def choose_lectures(max_cnt=100):
    res = []
    cnt = 0
    while cnt < max_cnt:
        # input form: "MAS109" or "MAS109 A,C,E"
        inp = input().upper().split()

        if len(inp):
            try:
                lec = lecture_list[inp[0]]
                cls = list()
                if len(inp) > 1:
                    inp_cls = inp[1].split(',')
                    for i in inp_cls:
                        class_names = list(map(str, lec.classes))
                        cls.append(lec.classes[class_names.index(i)])
                else:
                    cls = lec.classes

                res.append((lec, cls))
                cnt += 1
            except:
                print("- Lecture not in the data list! Try again.")
        else:
            break

    return res


# main
if __name__ == '__main__':
    print(line_string + " 'Scheduler' by 000wan\n" + line_string)

    # load data; folder location: './data/lecture_data'
    lecture_list = load_lecture_data("data/lecture_data")
    building_data = load_campus_data("data/campus_data")

    # user_input
    minimum_credit = int(input("0. 최소 희망 학점: "))

    print('1. 필수 수강 과목번호 입력:')
    necessary_list = choose_lectures()

    print('2. 수강 희망 과목번호 입력')
    wish_list = choose_lectures()

    # lecture block color decision
    input_list = necessary_list + wish_list
    input_lectures = tuple(map(lambda x: x[0], input_list))
    necessary_lectures = tuple(map(lambda x: x[0], necessary_list))
    for i, lec in enumerate(input_lectures):
        lec.color = colors[i % len(colors)]

    # start search
    search_result = search(input_lectures, tuple(), minimum_credit, necessary_lectures, input_list)

    result_path = 'result/' + current_time.strftime('%Y-%m-%d %H_%M_%S')
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    if isinstance(search_result, list):
        for i, dict in enumerate(search_result):  # iterating time tables
            table = TimeTable(dict)
            schedule = table.convert_to_Schedule()
            schedule.save(result_path, str(i+1))

            info_data = [
                [int(table.credit.real), "학점"],
                [int(table.credit.imag), "AU"]
            ]

            schedule.print("{0}st Time Table".format(i+1), result_path, str(i+1), info_table=info_data, save=True, show=True)

            # print in terminal
            '''print("%dst Time Table:" % (i + 1))
            for lecture in dict:  # iterating lectures
                print(lecture, end='    ')
                for cls in dict[lecture]:
                    print(cls, end=',')
                print()
            print('\n')'''
    else:
        print('No Time Table available!')
