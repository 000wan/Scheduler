# =========================
#  'Scheduler' by 000wan
# =========================
# Description :
#    University Schedule Generator with probabilities
# History :
#    2022/08/09 : Development starts with python
#    2022/08/10 ~ 2022/08/14 : Search algorithm using dp complete
#

import xlrd

line_string = "=========================\n"
days = ['월', '화', '수', '목', '금', '토', '일']


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
    def __init__(self, code, name, credit, info):
        self.code = code  # 과목번호
        self.name = name  # 과목명
        self.credit = credit  # 학점 (z=학점+AU*i)
        self.classes = []  # 분반
        self.info = info

    def __str__(self):
        return self.code


class Class:
    def __init__(self, name, professor, capacity, enrolled, time, classroom, info):
        self.name = name  # 분반명
        self.professor = professor  # 담당교수
        self.capacity = capacity  # 정원
        self.enrolled = enrolled  # 수강인원
        self.time = time  # 강의시간 (type:int list)
        self.classroom = classroom  # 강의실
        self.info = info

    def __str__(self):
        return self.name


# 상태:(남은 신청 과목(tuple), 이미 사용한 시간(tuple)) -> 결과:해당 상태에서 가능한 강의 조합 memoization
memo = {}

# dp 탐색 함수
def search(enroll_list, used_time, remain_credit):
    # enroll_list:tuple, used_time:tuple, remain_credit:int
    global memo
    if not enroll_list in memo.keys():
        memo[enroll_list] = {}
    if not used_time in memo[enroll_list].keys():
        memo[enroll_list][used_time] = []

    if len(memo[enroll_list][used_time]):
        return memo[enroll_list][used_time] # memoization
    if len(enroll_list) == 0:
        if remain_credit <= 0:
            memo[enroll_list][used_time].append({})
            return memo[enroll_list][used_time]
        else:
            return 0

    res = []
    if remain_credit <= 0:
        res.append({})

    lec = enroll_list[0]
    for cls in lec.classes:
        if len(set(used_time) & set(cls.time)) == 0:
            new_used_time = list(set(used_time) | set(cls.time))
            new_used_time.sort()
            #next search
            successor = search(enroll_list[1:], tuple(new_used_time), remain_credit - lec.credit.real)
            if successor:
                for i in successor:
                    flag = True
                    for j in res:
                        if len(j):
                            recorded = dict(j)
                            rec_lec = recorded.pop(str(lec), None)

                            if recorded == i and not rec_lec is None:
                                if rec_lec[0].time == cls.time: # check same-time classes
                                    if cls not in rec_lec:
                                        j[str(lec)].append(cls)
                                    flag = False
                                    break
                    if flag:
                        # res = list( dict(lec: [classes]) )
                        new_res = dict(i)
                        new_res[str(lec)] = [cls]
                        res.append(new_res)
    #without lec search
    successor = search(enroll_list[1:], used_time, remain_credit)
    if successor:
        res = res + successor

    memo[enroll_list][used_time] = res
    return memo[enroll_list][used_time]


# main
if __name__ == '__main__':
    print(line_string + " 'Scheduler' by 000wan\n" + line_string)

    lecture_list = {}  # 과목코드:Lecture 리스트
    wb = xlrd.open_workbook('data/2022_가을학기_전체개설과목.xls')
    ws = wb.sheet_by_index(0)
    for i in range(2, ws.nrows):
        row = ws.row_values(i)
        code = row[5]

        # Lecture 생성
        if not code in lecture_list.keys():
            credit = complex(float(row[11].split(':')[2]), int(row[10]))
            lecture_list[code] = Lecture(code, row[8], credit, row[:7] + row[8:12])
        # Class 생성
        time = time_stock(row[17])
        cls = Class(row[7], row[12], int(row[15]), int(row[16]), time, row[18], row[12:])
        lecture_list[code].classes.append(cls)

    '''# test
    for i in lecture_list.values():
        print(i.code, i.name, i.credit)
        for j in i.classes:
            print(j.name, j.professor, j.capacity, j.enrolled, j.time, j.classroom)'''

    # user_input
    minimum_credit = int(input("최소 희망 학점: "))

    input_list = []
    print('수강 희망 과목번호 입력(중요도 내림차순)')
    cnt = 0
    while cnt < 100:
        inp = input()
        if inp:
            if inp in lecture_list.keys():
                input_list.append(lecture_list[inp])
                #for i in lecture_list[inp].classes:
                #    print(inp, i.name, i.professor, i.time)
                cnt += 1
            else:
                print("- Code not in data list! Try again.")
        else:
            break

    input_tuple = tuple(input_list)
    result = search(input_tuple, tuple(), minimum_credit)
    for i, table in enumerate(result): # iterating time tables
        print("%dst Time Table:" % (i+1))
        for lecture in table: # iterating lectures
            print(lecture, end='    ')
            for cls in table[lecture]:
                print(cls, end=',')
            print()
        print('\n')