# ~/result/custom/create.py
#
#   Function: Create custom time-table image (Ex: exam schedule)
#
import result

if __name__ == '__main__':
    custom_file_name = '2022_Fall_Midterm'

    schedule = result.Schedule()
    schedule.load('.', custom_file_name)

    schedule.print('2022 Fall Midterm', '.', custom_file_name, info_table=[], save=True, show=True)
