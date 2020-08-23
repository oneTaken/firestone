import tkinter as tk
import datetime
from functools import partial
import xlrd
from collections import Counter
from main import Main


class TimePrompt():
    def __init__(self, master):
        self.root = master
        self.ui_list = []
        self.create_ui()

    def add_time(self, _label, _entry):
        _cur = datetime.datetime.now()
        try:
            minute = int(_entry.get().strip())
            assert minute <= 360
        except:
            _entry.config(fg="red")
            return
        _delta = datetime.timedelta(seconds=minute * 60)
        _dst = _cur + _delta
        _label.set(f"{_dst.hour}:{_dst.minute}")
        _entry.config(fg="black")
    
    def clear(self, _label, _entry):
        _label.set("00:00")
        _entry.delete(0, tk.END)
    
    def base_ui(self, root_frame):
        entry = tk.Entry(root_frame)
        entry.place(relx=0, relwidth=0.2)
    
        label_str = tk.StringVar(value="00:00")
        label = tk.Label(root_frame, textvariable=label_str)
        label.place(relx=0.8, relwidth=0.2)

        _len = len(self.ui_list)
        self.ui_list.append([label_str, entry])
    
        add_command = partial(self.add_time, self.ui_list[_len][0], self.ui_list[_len][1])
        tk.Button(root_frame, command=add_command, text="添加", fg="blue").place(relx=0.3, relwidth=0.2)
        clear_command = partial(self.clear, self.ui_list[_len][0], self.ui_list[_len][1])
        tk.Button(root_frame, command=clear_command, text="清除", fg="blue").place(relx=0.55, relwidth=0.2)
    
    def create_ui(self):
        # 探险地图
        f1 = tk.Frame(self.root)
        f1.place(relx=0, rely=0, relwidth=1, relheight=0.25)
        tk.Label(f1, text="探险").place(relx=0, relwidth=0.2)
        f1_child = tk.Frame(f1)
        f1_child.place(relx=0.2, relwidth=0.8, rely=0, relheight=1)
        self.base_ui(f1_child)
    
        # 陨石研究
        f2 = tk.Frame(self.root)
        f2.place(relx=0, rely=0.25, relwidth=1, relheight=0.5)
        tk.Label(f2, text="陨石").place(relx=0, relwidth=0.2)
        f2_child = tk.Frame(f2)
        f2_child.place(relx=0.2, relwidth=0.8, rely=0, relheight=1)
        f2_first = tk.Frame(f2_child)
        f2_first.place(relx=0, relwidth=1, rely=0, relheight=0.5)
        f2_second = tk.Frame(f2_child)
        f2_second.place(relx=0, relwidth=1, rely=0.5, relheight=0.5)
    
        self.base_ui(f2_first)
        self.base_ui(f2_second)
    
        # 远征
        f3 = tk.Frame(self.root)
        f3.place(relx=0, rely=0.75, relwidth=1, relheight=0.25)
        tk.Label(f3, text="远征").place(relx=0, relwidth=0.2)
        f3_child = tk.Frame(f3)
        f3_child.place(relx=0.2, relwidth=0.8, rely=0, relheight=1)
        self.base_ui(f3_child)


class LevelUp():
    def __init__(self, master):
        self.root = master
        self.update_data = self.parse_data()
        self.create_ui()
        self.math_flag = True

    def parse_data(self):
        path = "/Users/deepmind/projects/firestone/data/gold.xlsx"
        data = xlrd.open_workbook(path)
        table = data.sheet_by_index(1)
        update_data = []
        start_row = 8
        end_row = 732
        start_col = 0
        end_col = 5
        for i in range(start_row, end_row):
            lv, desc, buff, _, cost = [table.cell(i, j).value for j in range(start_col, end_col)]
            update_data.append((lv, desc, buff, cost))

        return update_data

    def create_ui(self):
        r1 = tk.Frame(self.root)
        r1.place(relx=0, rely=0, relwidth=1, relheight=0.1)
        r3 = tk.Frame(self.root)
        r3.place(relx=0, rely=0.1, relwidth=1, relheight=0.1)
        r2 = tk.Frame(self.root)
        r2.place(relx=0, rely=0.3, relwidth=1, relheight=0.6)

        def percent(_value):
            return f"+{int(_value * 100)}%"

        def big_to_math_str(x):
            # x must be > 0
            str_num = str(x)
            if "e+" in str_num:
                # already big num
                a, b = str_num.split("e+")
                if "." not in a:
                    return str(x)
                pre, post = a.split(".")
                return f"{pre}.{post[0]}e+{b}"
            str_num = str(int(x))  # small num remove ".0"
            num_10 = Counter(str_num)["0"]
            valid_num = len(str_num) - num_10
            if valid_num == 1:
                return f"{str_num[0]}e+{num_10}"
            else:  # >1, round
                tail = "" if str_num[1] == "0" else f".{str_num[1]}"
                return f"{str_num[0]}{tail}e+{len(str_num) - 1}"

        def math_str_to_chr(_str):
            a, b = _str.split("e+")
            a, b = float(a), int(b)
            if b < 15:
                return _str
            delta = (b - 15) // 3
            da = delta // 26
            db = delta - delta // 26 * 26
            prefix = a * 10 ** (b - b // 3 * 3)
            prefix = round(prefix, 1)
            return str(prefix) + chr(97 + da) + chr(97 + db)

        def show_num(x):
            math_str = big_to_math_str(x)
            _value = math_str if self.math_flag else math_str_to_chr(math_str)
            _value = _value.replace("e+", "e")
            return _value

        def query():
            str_level = r1_entry.get()
            if str_level == "":
                return
            try:
                num_level = float(str_level)
                assert num_level == int(num_level)
                num_level = int(num_level)
            except:
                return
            total = 0
            for i in range(5):
                lv, desc, buff, cost = self.update_data[num_level + i]
                lv = str(int(lv))
                buff = percent(buff)
                # if i == 0:
                #     total = -cost
                total += cost
                text_list[i * 5 + 0].set(lv)
                text_list[i * 5 + 1].set(desc)
                text_list[i * 5 + 2].set(buff)
                text_list[i * 5 + 3].set(show_num(cost))
                text_list[i * 5 + 4].set("0" if total == 0 else show_num(total))

        def rb1_change():
            self.math_flag = True
            query()

        def rb2_change():
            self.math_flag = False
            query()

        # r1
        tk.Label(r1, text="等级").place(relx=0, rely=0, relwidth=0.15, relheight=1)
        r1_entry = tk.Entry(r1)
        r1_entry.place(relx=0.2, rely=0, relwidth=0.2, relheight=1)
        r1_button = tk.Button(r1, text="查询接下来5级", command=query, fg="blue")
        r1_button.place(relx=0.5, rely=0, relwidth=0.4, relheight=1)

        # r3
        rb1 = tk.Radiobutton(r3, text="科学计数法", value=1, command=rb1_change)
        rb1.place(relx=0.3, rely=0, relwidth=0.3, relheight=1)
        rb2 = tk.Radiobutton(r3, text="字符计数法", value=2, command=rb2_change)
        rb2.place(relx=0.6, rely=0, relwidth=0.3, relheight=1)
        rb1.select()

        text_list = []
        num_row = 6
        num_col = 5
        str_list = ["等级", "作用", "提升", "费用", "累计"]
        for j in range(num_col):
            b = 0 / num_row
            d = 1 / num_row
            a = j / num_col
            c = 1 / num_col
            tk.Label(r2, text=str_list[j]).place(relx=a, rely=b, relwidth=c, relheight=d)

        for i in range(1, num_row):
            b = i / num_row
            d = 1 / num_row
            for j in range(num_col):
                a = j / num_col
                c = 1 / num_col
                _variable = tk.StringVar(value="")
                tk.Label(r2, textvariable=_variable).place(relx=a, rely=b, relwidth=c, relheight=d)
                text_list.append(_variable)


class Auto():
    def __init__(self, master):
        self.root = master
        self.script = Main()

        frame = tk.Frame(self.root)
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        button = tk.Button(frame, text="run", command=self.run, fg="blue")
        button.place(relx=0, rely=0, relwidth=1, relheight=1)

    def run(self):
        self.script.run()


class GUI():
    def __init__(self):
        self.root = tk.Tk()
        # w, h = 320, 320
        w, h = 400, 400
        self.root.geometry(f"{w}x{h}")
        self.root.resizable(0, 0)
        self.root.title("倒计时")
        self.cur_frame = None

        # 菜单栏
        # menu = tk.Menu(self.root, tearoff=0)
        # fileMenu = tk.Menu(menu)
        # # fileMenu.add_command(label="again", command=self.again)
        # fileMenu.add_command(label="forget", command=self.forget)
        # menu.add_cascade(label="编辑", menu=fileMenu)
        # self.root.config(menu=menu)

        self.frame_time = tk.Frame(self.root)
        self.frame_level = tk.Frame(self.root)
        self.frame_auto = tk.Frame(self.root)

        self.frame_button = tk.Frame(self.root)
        self.frame_button.place(relx=0, rely=0, relwidth=1, relheight=0.1)
        button_auto = tk.Button(self.frame_button, text="auto", command=partial(self.place_frame, self.frame_auto),
                                fg="blue")
        button_auto.place(relx=0, relwidth=0.2, rely=0, relheight=1)

        button_level = tk.Button(self.frame_button, text="level", command=partial(self.place_frame, self.frame_level),
                                fg="blue")
        button_level.place(relx=0.3, relwidth=0.2, rely=0, relheight=1)

        button_time = tk.Button(self.frame_button, text="time", command=partial(self.place_frame, self.frame_time),
                                fg="blue")
        button_time.place(relx=0.6, relwidth=0.2, rely=0, relheight=1)

        TimePrompt(self.frame_time)
        LevelUp(self.frame_level)
        Auto(self.frame_auto)

        self.cur_frame = self.frame_level
        self.place_frame(self.cur_frame)
        self.root.mainloop()

    def place_frame(self, dst_frame):
        if dst_frame == self.cur_frame:
            return

        self.cur_frame.place_forget()
        self.cur_frame = dst_frame
        self.cur_frame.place(relx=0, rely=0.1, relwidth=1, relheight=1)


if __name__ == "__main__":
    gui = GUI()
