 =========================
#  'Scheduler' by 000wan
# =========================
# Description :
#    University Schedule Generator
# History :
#    2022/08/09 : Start development with python
#    2022/08/10 ~ 2022/08/14 : Complete search algorithm using dp
#    2022/08/15 ~ 2022/08/29 : Generate ime-table image
#    2022/08/31 ~ 2022/09/07 : Enhance OOP
#    2022/09/07 ~ Current : Add new feature: distance among buildings
#

import matplotlib
import matplotlib.pyplot as plt

# Korean Font 'malgun gothic' loaded
from matplotlib import font_manager, rc
font_path = "C:/Windows/Fonts/malgun.ttf"
try:    font = font_manager.FontProperties(fname=font_path).get_name()
except: raise Exception("Korean Font 'Malgun Gothic' required in 'C:/Windows/Fonts/malgun.ttf'")
rc('font', family=font)

import os
import time as current_time

# import data folder
import data

line_string = "=========================\n"
days = ['월', '화', '수', '목', '금', '토', '일']
colors = matplotlib.cm.get_cmap('Pastel1').colors + matplotlib.cm.get_cmap('Pastel2').colors    # Pastel colors

lecture_list = {}  # 과목코드:Lecture 리스트
building_data = {}  # 건물번호:data

def class_building(classroom):
    if len(classroom):
        if classroom[0] == '(':
            building = classroom[1:classroom.index(')')]
            return building
    return ''

def time_stock(period):  # lecture time text to int list
    result = list()
    for p in period.split('\r\n'):
        if p:
            items = p.split(' ')
            day = days.index(items[0])
            times = items[1].split('~')
            # 00:00~24:00 -> 0~48 one-to-one mapping
            start = 2 * int(times[0].split(':')[0]) + int(times[0].split(':')[1]) // 30
            end = 2 * int(times[1].split(':')[0]) + int(times[1].split(':')[1]) // 30

            for t in range(start, end):
                result.append(48 * day + t)  # day,time -> 0~7*48

    result.sort()
    return result


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

    def print_table(self, count, result_path):
        # time table matplotlib
        # Ref: https://masudakoji.github.io/2015/05/23/generate-timetable-using-matplotlib/en/

        time_table = self.dict
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        times = list()
        for i in range(16, 49):
            if i % 2 == 0:
                times.append(i // 2)
            else:
                times.append('')

        # fig = plt.figure(figsize=(15, 15)) # 10*15:time-table + 5*15:info
        fig, axs = plt.subplots(1, 2, figsize=(15, 15), gridspec_kw={'width_ratios': [2, 1]})

        # Set Axis
        ax = axs[0]
        ax.yaxis.grid(linestyle='--', color='gray')
        ax.set_xlim(0.5, len(days) + 0.5)
        ax.set_ylim(24.1, 7.9)
        ax.set_xticks(range(1, len(days) + 1))
        ax.set_yticks(list(map(lambda x: x / 2, range(16, 49))))
        ax.set_xticklabels(days)
        ax.set_yticklabels(times)

        # Set Second Axis
        ax2 = ax.twiny().twinx()
        ax2.set_xlim(ax.get_xlim())
        ax2.set_ylim(ax.get_ylim())
        ax2.set_xticks(ax.get_xticks())
        ax2.set_yticks(ax.get_yticks())
        ax2.set_xticklabels(days)
        ax2.set_yticklabels(times)

        for lec_code in time_table:
            lec = lecture_list[lec_code]
            cls = time_table[lec_code][0]
            times = cls.lecture_time

            pivot = 0
            for t in range(len(times)):
                if t < len(times) - 1:
                    if times[t + 1] - times[t] == 1 and times[t] // 48 == times[t + 1] // 48:
                        continue  # connected time

                day = times[pivot] // 48 + 1  # 1,2,3,4,5 -> M,T,W,T,F
                start = (times[pivot] % 48) * 0.5 + 0.05
                end = (times[t] % 48 + 1) * 0.5 - 0.05

                # plot time block
                axs[0].fill_between([day - 0.48, day + 0.48], [start, start], [end, end], color=lec.color,
                                    edgecolor='k', linewidth=0.5)
                if len(lec.classes) == 1:
                    # only title
                    # axs[0].text(day, (start + end) * 0.5, cls.lecture_name, ha='center', va='center', fontsize=15)
                    axs[0].text(day, (start + end) * 0.5 - 0.15, cls.lecture_name, ha='center', va='center',
                                fontsize=15)
                    sub_title = '(' + cls.professor + ')'
                    axs[0].text(day, (start + end) * 0.5 + 0.15, sub_title, ha='center', va='center', fontsize=11)
                else:
                    axs[0].text(day, (start + end) * 0.5 - 0.15, cls.lecture_name, ha='center', va='center',
                                fontsize=15)
                    classes = list(map(str, time_table[lec_code]))
                    sub_title = '(' + (', '.join(classes)) + ')'
                    axs[0].text(day, (start + end) * 0.5 + 0.15, sub_title, ha='center', va='center', fontsize=12)

                # class location
                '''bottom_title = '(' + cls.building + ')'
                if cls.building in building_data.keys():
                    bottom_title += building_data[cls.building]['KR']''' # KR building name
                axs[0].text(day - 0.45, end - 0.03, cls.building, va='bottom', fontsize=12)

                pivot = t + 1

        axs[0].set_title("{0}st Time Table".format(count), y=1.07, fontsize=21)

        # Info table
        table_data = [
            [int(self.credit.real), "학점"],
            [int(self.credit.imag), "AU"]
        ]
        table = axs[1].table(cellText=table_data, cellLoc='center', loc='center', edges='open')
        table.set_fontsize(18)
        table.scale(0.5, 2)
        axs[1].axis('off')
        axs[1].axis('tight')

        '''if not os.path.exists(result_path):
            os.makedirs(result_path)
        plt.savefig(result_path+'/{0}.png'.format(count), dpi=200)'''
        plt.show()


# 상태:(남은 신청 과목(tuple), 이미 사용한 시간(tuple)) -> 결과:해당 상태에서 가능한 강의 조합 memoization
memo = {}


# dp 탐색 함수
def search(enroll_list, used_time, remain_credit, necessary_list):
    # enroll_list:tuple, used_time:tuple, remain_credit:int, necessary_list:list
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
    for cls in lec.classes:
        if len(set(used_time) & set(cls.lecture_time)) == 0:
            new_used_time = list(set(used_time) | set(cls.lecture_time))
            new_used_time.sort()

            new_necessary_list = list(necessary_list)
            if lec in new_necessary_list:
                new_necessary_list.remove(lec)

            # next search
            successor = search(enroll_list[1:], tuple(new_used_time), remain_credit - lec.credit.real, new_necessary_list)
            if successor:
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
        successor = search(enroll_list[1:], used_time, remain_credit, necessary_list)
        if successor:
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
        inp = input()
        if inp:
            if inp in lecture_list.keys():
                res.append(lecture_list[inp])
                cnt += 1
            else:
                print("- Code not in the data list! Try again.")
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
    for i, lec in enumerate(input_list):
        lec.color = colors[i % len(colors)]

    # start search
    result = search(tuple(input_list), tuple(), minimum_credit, necessary_list)

    result_path = 'result/' + current_time.strftime('%Y-%m-%d %H_%M_%S')
    if result:
        for i, dict in enumerate(result):  # iterating time tables
            table = TimeTable(dict)
            table.print_table(i+1, result_path)

            # print in terminal
            '''print("%dst Time Table:" % (i + 1))
            for lecture in table:  # iterating lectures
                print(lecture, end='    ')
                for cls in table[lecture]:
                    print(cls, end=',')
                print()
            print('\n')'''
    else:
        print('No Time Table available!')
