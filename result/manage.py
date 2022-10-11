import matplotlib.pyplot as plt
import json

day_label_KR = ['월', '화', '수', '목', '금', '토', '일']
day_label_EN = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']

class Block:
    def __init__(self, title='', sub_title='', info='', color='', time=(0, 0)):
        self.title = title
        self.sub_title = sub_title
        self.info = info
        self.color = color
        self.time = time

class Schedule:
    def __init__(self, block_list=[]):
        self.list = block_list

    def save(self, result_path, file_name):
        with open('{0}/{1}.json'.format(result_path, file_name), 'w') as f:
            json.dump(list(map(lambda block: block.__dict__, self.list)), f, indent=2)

    def load(self, result_path, file_name):
        with open('{0}/{1}.json'.format(result_path, file_name)) as f:
            self.list = json.load(f)

    def print(self, image_title, result_path, file_name, info_table=[], save=False, show=True):
        # time table matplotlib
        # Ref: https://masudakoji.github.io/2015/05/23/generate-timetable-using-matplotlib/en/

        time_label = list()
        for i in range(16, 49):
            if i % 2 == 0:
                time_label.append(i // 2)
            else:
                time_label.append('')

        if info_table:
            # 10*15:time-table + 5*15:info
            fig, axs = plt.subplots(1, 2, figsize=(15, 15), gridspec_kw={'width_ratios': [2, 1]})
            ax = axs[0]

            # stands for plot.text, plot.fill_between, etc..
            plot = ax
            plot.set_title(image_title, y=1.07, fontsize=21)

            # Info table
            table = axs[1].table(cellText=info_table, cellLoc='center', loc='center', edges='open')
            table.set_fontsize(18)
            table.scale(0.5, 2)
            axs[1].axis('off')
            axs[1].axis('tight')
        else:
            # 10*15:time-table
            fig = plt.figure(figsize=(10, 15))
            ax = plt.axes()

            # stands for plot.text, plot.fill_between, etc..
            plot = plt
            plot.title(image_title, y=1.07, fontsize=21)

        # Set Axis
        ax.yaxis.grid(linestyle='--', color='gray')
        ax.set_xlim(0.5, len(day_label_EN) + 0.5)
        ax.set_ylim(24.1, 7.9)
        ax.set_xticks(range(1, len(day_label_EN) + 1))
        ax.set_yticks(list(map(lambda x: x / 2, range(16, 49))))
        ax.set_xticklabels(day_label_EN)
        ax.set_yticklabels(time_label)

        # Set Second Axis
        ax2 = ax.twiny().twinx()
        ax2.set_xlim(ax.get_xlim())
        ax2.set_ylim(ax.get_ylim())
        ax2.set_xticks(ax.get_xticks())
        ax2.set_yticks(ax.get_yticks())
        ax2.set_xticklabels(day_label_EN)
        ax2.set_yticklabels(time_label)

        for block in self.list:
            '''lec = lecture_list[lec_code]
            classes = time_table[lec_code]
            cls = classes[0]
            times = cls.lecture_time

            for timeStock in times:'''
            day = block.time[0] // 24 + 1  # 1,2,3,4,5 -> M,T,W,T,F
            start = block.time[0] % 24 + 0.05
            end = block.time[1] % 24 - 0.05

            # plot time block
            plot.fill_between([day - 0.48, day + 0.48], [start, start], [end, end], color=block.color,
                                edgecolor='k', linewidth=0.5)
            '''if len(classes) == 1:
                # only title
                # plot.text(day, (start + end) * 0.5, cls.lecture_name, ha='center', va='center', fontsize=15)
                sub_title = cls.professor + ' (' + str(cls) + ')'
                clsroom = cls.classroom.strip()
                try:
                    building_string = f'({ cls.building }){ building_data[cls.building]["KR"] }'
                    if clsroom.startswith(building_string):
                        room_number = clsroom[len(building_string):]
                        info_text = cls.building + ' ' + room_number
                        if len(info_text) > 10 and not '\n' in info_text:
                            info_text = info_text[:10] + '\n' + info_text[10:].strip()
                    else:
                        raise
                except:
                    info_text = cls.building
            else:
                classes = list(map(str, time_table[lec_code]))
                sub_title = '(' + (', '.join(classes)) + ')'
                info_text = cls.building'''

            plot.text(day, (start + end) * 0.5 - 0.15, block.title, ha='center', va='center',
                        fontsize=15)
            plot.text(day, (start + end) * 0.5 + 0.15, block.sub_title, ha='center', va='center', fontsize=11)

            plot.text(day - 0.45, end - 0.25, block.info, va='top', fontsize=12)

        if save:
            plt.savefig('{0}/{1}.png'.format(result_path, file_name), dpi=200)
        if show:
            plt.show()