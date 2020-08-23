import pyautogui
import time
import numpy as np
import cv2
import skimage.measure as skm
import logging
import os
import datetime
import traceback
import sys
import argparse

# parser = argparse.ArgumentParser()
# parser.add_argument("-t", dest="time", type=str, default="06:00:00")
# args = parser.parse_args()
#
# logging.basicConfig(filename="log.txt", level=logging.INFO, filemode="w",
#                     format="%(asctime)s,%(funcName)s,%(lineno)d,%(message)s")


class Rect():
    def __init__(self, start_c, start_r, end_c, end_r):
        self.start_c = start_c
        self.start_r = start_r
        self.end_c = end_c
        self.end_r = end_r
        center_r = start_r + (end_r - start_r) // 2
        center_c = start_c + (end_c - start_c) // 2
        self.center = (center_c//2, center_r//2)
        # this r-c is got by pyautogui.screenshot function
        # mac resolution: 800x1280
        # pyautogui screenshot: 1600x2560

    def patch_on_img(self, img):
        return img[self.start_r: self.end_r, self.start_c: self.end_c]


exit = Rect(2364, 40, 2490, 170)  # 4. 右上角的叉叉
reconnect = Rect(1378, 964, 1700, 1050)  # 重新连接
gap_time = 5 * 60  # 5 minutes
root = "/Users/deepmind/projects/firestone/auto"
reconnect_path = f"{root}{os.sep}guaji{os.sep}reconnect.png"
# reconnect_path = "/Users/deepmind/projects/firestone/auto/guaji/reconnect.png"  # absolute path
normal_path = f"{root}{os.sep}guaji{os.sep}normal.png"
normal_family_path = f"{root}{os.sep}guaji{os.sep}normal_family.png"
reconnect_times = 3
global_connect = 0


def click(rect, seconds=2.0):
    assert isinstance(rect, Rect)
    pyautogui.click(*rect.center)  # w, h
    time.sleep(seconds)


def screenshot_old():
    # bug
    # 在终端中运行的时候截屏出来的图全部为桌面的图
    # 在notebook中运行的时候截屏的图才为当前屏幕的图
    # 可能是获取屏幕权限的问题
    logging.info("获取当前屏幕截图")
    screen = pyautogui.screenshot()
    screen = np.array(screen)[..., :3]  # h, w, 4

    return screen


def screenshot():
    # cur_time = datetime.datetime.now()
    # h, m, s, ms = cur_time.hour, cur_time.minute, cur_time.second, cur_time.microsecond
    # screen_path = f"screen_{h}_{m}_{s}_{ms}.png"
    screen_path = f"{root}{os.sep}screen.png"
    os.system(f"screencapture -x {screen_path}")
    screen = cv2.imread(screen_path)[..., ::-1]

    return screen


class Family():
    def __init__(self):
        self.ride = Rect(1580, 485, 1980, 575)  # 1. 开始远征
        self.get = Rect(1580, 485, 1980, 575)  # 2. 领取,与开始远征位置yizhi
        self.confirm = Rect(1390, 990, 1770, 1090)  # 3. 领取之后的OKay
        # self.exit = Rect(2364, 40, 2490, 170)  # 4. 右上角的叉叉

    def back2main(self):
        logging.info("从远征界面返回挂机界面")
        # 当前位于远征界面
        click(exit)  # 1. 退出远征任务界面，进入工会主界面
        click(exit)  # 2. 退出工会主界面，进入城镇界面
        click(exit)  # 3. 退出城镇界面，进入挂机主界面

    def run_one(self):
        # 情形1: 任务刚刷新，没有正在执行的任务
        # Step 1: 领取一个远征任务
        click(self.ride)

    def run_two(self):
        logging.info("领取远征任务->OK->开始远征")
        # 情形2: 领取正在执行的任务
        # 可以覆盖情形1

        # 避免网络延迟出现
        click(self.get, 3)
        click(self.confirm)
        click(self.ride)

    def run(self):
        self.run_two()
        self.back2main()


class Library():
    def __init__(self):
        self.research = Rect(1100, 1064, 1463, 1200)  # 1. 研究
        self.full = Rect(2240, 300, 2260, 310)  # 2. 槽占满的空白处
        # case situation, case/1.png
        # self.case_1 = Rect(694, 760, 1230, 895)  # 1. 金币雨
        # self.case_2 = Rect(2000, 580, 2540, 720)  # 4. 伤害值属性
        # self.case_3 = Rect(1354, 760, 1890, 895)  # 5. 陨石风暴，在金币雨往右660位置
        # self.case_4 = Rect(2016, 941, 2529, 1062)  # 6. 敌人血肉

        # 4.png,右半部分科技
        r = 340
        c = 660
        self.case_1 = Rect(66, 582, 593, 722)  # 1. 伤害值属性
        self.case_2 = Rect(66, 582+r, 593, 722+r)  # 2. 敌人削弱
        self.case_3 = Rect(66+c, 582, 593+c, 722)  # 3. 守护者战力
        self.case_4 = Rect(66+c, 582+r, 593+c, 722+r)  # 4. Boss削弱
        self.case_5 = Rect(66+c*2, 582, 593+c*2, 722)  # 5. 生命值属性
        self.case_6 = Rect(66 + c*2, 582 + r, 593 + c*2, 722 + r)  # 6. 护甲值属性
        self.case_7 = Rect(2032, 410, 2550, 550)  # 7. 怒气型英雄
        self.case_8 = Rect(2032, 760, 2550, 900)  # 8. 法力型英雄
        self.case_9 = Rect(2032, 1110, 2550, 1250)  # 9. 能量型英雄

        # 用这个来可控调节
        self.point1 = self.case_8
        self.point2 = self.case_9

    def back2main(self):
        logging.info("从图书馆界面返回到挂机界面")
        click(exit)

    def test_points(self):
        # click_list = [eval("self.case_"+str(i)) for i in range(1, 10)]
        click_list =[self.case_1, self.case_2, self.case_3, self.case_4, self.case_5,
                     self.case_6, self.case_7, self.case_8, self.case_9]
        for point in click_list:
            click(point)
            click(self.research)
            click(self.full)  # 槽占满会多一道提示
            click(self.full)

    def run(self):
        logging.info("开始点击两个研究")
        # self.test_points()
        # return
        click(self.point1)
        click(self.research)
        click(self.full)  # 槽占满会多一道提示
        click(self.full)

        click(self.point2)
        click(self.research)
        click(self.full)
        click(self.full)

        self.back2main()


class Guard():
    def __init__(self):
        self.girl = Rect(1093, 1413, 1264, 1574)      # 守卫仙女
        self.dragon = Rect(1293, 1413, 1464, 1574)    # 守卫火龙
        self.training = Rect(1335, 1191, 1686, 1312)  # 训练

    def back2main(self):
        logging.info("从守卫界面返回到挂机界面")
        click(exit)

    def run(self):
        logging.info("守卫训练点击")
        click(self.dragon)
        click(self.training)

        self.back2main()


class Map():
    icon_root = f"{root}{os.sep}map{os.sep}icon"

    def __init__(self, refresh_time="06:00:00"):
        self.icon_num = range(1, 7)
        self.icon_imgs = [cv2.imread(f"{self.icon_root}{os.sep}icon_{i}.png", 0) for i in self.icon_num]
        self.h, self.w = 80, 100  # fixed icon shape
        self.pt_list_1 = [[], [], [], [], [], []]
        self.pt_list_2 = [[], [], [], [], [], []]
        self.pixels = 10  # nms
        self.threshold = 0.7  # template threshold
        self.safe_point = Rect(2355, 913, 2476, 980)  # 点击此处无意义
        self.down_pixels = 400
        self.point_get = Rect(170, 400, 280, 450)  # 领取任务点
        self.img_get = cv2.imread(f"{root}{os.sep}map{os.sep}get.png")[..., ::-1]
        self.point_ok = Rect(1110, 807, 1451, 875)  # 领取之后点击OK确认
        self.point_start = Rect(1085, 1309, 1461, 1395)  # 点击任务图标之后的弹窗

        self.img_start_1 = cv2.imread(f"{root}{os.sep}map{os.sep}start_mission.png")[..., ::-1]  # 情形1，开始任务
        self.img_start_2 = cv2.imread(f"{root}{os.sep}map{os.sep}already.png")[..., ::-1]   # 情形2，任务已开始
        self.img_start_3 = cv2.imread(f"{root}{os.sep}map{os.sep}lack.png")[..., ::-1]  # 情形3，缺乏足够小分队
        self.img_start_4 = cv2.imread(f"{root}{os.sep}map{os.sep}get_award.png")[..., ::-1]  # 情形4，任务已完成
        self.img_start_5 = cv2.imread(f"{root}{os.sep}map{os.sep}mission_limit.png")[..., ::-1]  # 情形5，任务打到上限
        self.ssim_t = 0.8

        # self.prior_tuple = [4, 2, 1, 0, 3, 5]  # 自定义优先级
        # self.prior_tuple = [0, 1, 2, 3, 4, 5]  # 最快的优先
        self.prior_tuple = [2, 1, 5, 4, 3, 0]
        self.click_list = []
        self.mission_length = len(self.click_list)
        self.mission_queues = 4  # 最大任务队列数量
        self.gap_row = 200  # 每一个领取点的上下间隔
        self.point_get_list = [Rect(170, 400+self.gap_row * i, 280, 450+self.gap_row * i)
                               for i in range(self.mission_queues)]

        self.mission_start_index = 0
        self.next_fresh_time = self.get_next_refresh_time(refresh_time=refresh_time)

    def get_next_refresh_time(self, cur=None, refresh_time="06:00:00"):
        if cur is None:
            cur = datetime.datetime.now()
        h, m, s = refresh_time.strip().split(":")
        h, m, s = int(h), int(m), int(s)
        seconds = (h * 60 + m) * 60 + s
        # TODO: fix cur problem
        dst = cur + datetime.timedelta(seconds=seconds)
        logging.info(f"下一次地图任务刷新时间为:\t{dst}")
        return dst

    def valid(self, p_list, pt, bonus=0):
        """nms,判断当前的任务框框是否有效"""
        if len(p_list) == 0:
            return True
        w, h = pt
        for (_w, _h) in p_list:
            if abs(_w - w) <= self.pixels and abs(_h - h - bonus) <= self.pixels:
                return False
        return True

    def screen_down(self):
        logging.info("将地图屏幕往下拉")
        pyautogui.drag(0, -self.down_pixels, 2, button='right')  # 向上拖动鼠标，相当于滚轮向下
        time.sleep(2)

    def get_pts(self):
        logging.info("获取地图上的任务点")
        self.get_pts_from_current_1()  # 截图第一次的处理
        self.screen_down()
        self.get_pts_from_current_2()  # 截图第二次的处理
        click(exit)
        logging.info(f"地图上屏的任务点为:\t{self.pt_list_1}")
        logging.info(f"地图下屏的任务点为:\t{self.pt_list_2}")

    def get_pts_from_current_1(self):
        logging.info("获取地图上屏上的任务点")
        screen = screenshot()
        gray = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
        for item, icon in enumerate(self.icon_imgs):
            res = cv2.matchTemplate(gray, icon, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= self.threshold)
            for pt in zip(*loc[::-1]):
                if self.valid(self.pt_list_1[item], pt):
                    self.pt_list_1[item].append(pt)

    def get_pts_from_current_2(self):
        logging.info("获取地图下屏上的任务点")
        screen = screenshot()
        gray = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
        for item, icon in enumerate(self.icon_imgs):
            res = cv2.matchTemplate(gray, icon, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= self.threshold)
            for pt in zip(*loc[::-1]):
                # 需要两个屏幕上都有效才算是有效点
                valid_1 = self.valid(self.pt_list_2[item], pt)
                # 因为pyautogui的2倍分辨率原因，需要乘以2
                valid_2 = self.valid(self.pt_list_1[item], pt, self.down_pixels * 2)
                if valid_1 and valid_2:
                    self.pt_list_2[item].append(pt)

    def order_pt(self):
        logging.info("按照优先级为任务点标序号，验证是否都检测出来了")
        pyautogui.press("M")
        click(self.safe_point)
        num = 0
        font = cv2.FONT_HERSHEY_SIMPLEX
        cur_time = datetime.datetime.now()
        day = cur_time.day
        th, m, s, ms = cur_time.hour, cur_time.minute, cur_time.second, cur_time.microsecond
        screen = screenshot()
        img = screen.copy()
        screen_folder = os.path.join(root, "screen_map")
        os.makedirs(screen_folder, exist_ok=True)

        num_list_1 = [[], [], [], [], [], []]
        num_list_2 = [[], [], [], [], [], []]
        for index in self.prior_tuple:
            for _ in range(len(self.pt_list_1[index])):
                num += 1
                num_list_1[index].append(num)
            for _ in self.pt_list_2[index]:
                num += 1
                num_list_2[index].append(num)

        # print(num_list_1)
        # print(num_list_2)
        # print(self.pt_list_1)
        # print(self.pt_list_2)

        for order_index, item_list in enumerate(self.pt_list_1):
            for j, (w, h) in enumerate(item_list):
                num_order = num_list_1[order_index][j]
                _center = (w + self.w//2, h+self.h//2)
                img = cv2.putText(img, str(num_order), _center, font, 1.2, (255, 0, 0), 10)
        cv2.imwrite(f"{screen_folder}{os.sep}{day}_{th}_{m}_{s}_{ms}_text_1.png", img[..., ::-1])
        self.screen_down()

        screen = screenshot()
        img = screen.copy()
        for order_index, item_list in enumerate(self.pt_list_2):
            for j, (w, h) in enumerate(item_list):
                num_order = num_list_2[order_index][j]
                _center = (w + self.w//2, h+self.h//2)
                img = cv2.putText(img, str(num_order), _center, font, 1.2, (255, 0, 0), 10)
        cv2.imwrite(f"{screen_folder}{os.sep}{day}_{th}_{m}_{s}_{ms}_text_2.png", img[..., ::-1])

        click(exit)

    def test_pts(self):
        # 测试上屏
        pyautogui.press("M")
        time.sleep(2)
        for _list in self.pt_list_1:
            for (w, h) in _list:
                rect = Rect(w, h, w+self.w, h+self.h)
                click(rect, 1)
                screen = screenshot()
                patch = self.point_start.patch_on_img(screen)
                status = self.get_misson_status(patch)
                click(self.safe_point, 1)

        # 测试下屏
        self.screen_down()
        for _list in self.pt_list_2:
            for (w, h) in _list:
                rect = Rect(w, h, w+self.w, h+self.h)
                click(rect, 1)
                click(self.safe_point, 1)

        click(exit)

    def get_misson_status(self, patch):
        """当前任务图标点击后，查看任务状态"""
        ssim_1 = skm.compare_ssim(patch, self.img_start_1, multichannel=True)
        ssim_2 = skm.compare_ssim(patch, self.img_start_2, multichannel=True)
        ssim_3 = skm.compare_ssim(patch, self.img_start_3, multichannel=True)
        ssim_4 = skm.compare_ssim(patch, self.img_start_4, multichannel=True)
        ssim_5 = skm.compare_ssim(patch, self.img_start_5, multichannel=True)
        logging.info(f"开始任务:{ssim_1:.4f}, 已经开始:{ssim_2:.4f}, 缺乏足够小分队:{ssim_3:.4f}, "
                     f"已经完成:{ssim_4:.4f}, 任务上限:{ssim_5:.4f}")
        if ssim_1 > self.ssim_t:
            return 1  # 开始任务
        elif ssim_2 > self.ssim_t:
            return 2  # 已经开始
        elif ssim_3 > self.ssim_t:
            return 3  # 缺乏足够小分队
        elif ssim_4 > self.ssim_t:
            return 4  # 已经完成
        elif ssim_5 > self.ssim_t:
            return 5  # 任务上限
        else:
            return 6  # 其它

    def get_click_list(self):
        """获取可供点击的任务队列，自定义优先级"""
        logging.info("获取点击的任务队列")
        _list = []
        for index in self.prior_tuple:
            for item in self.pt_list_1[index]:
                _list.append((False, item))
            for item in self.pt_list_2[index]:
                _list.append((True, item))
        logging.info(f"点击任务队列为:{_list}")

        return _list

    def click_mission(self, point_mission):
        """点击一个任务， 输入为对应图标"""
        # TODO: 优化这种点击方式
        logging.info("从地图界面返回到挂机界面,并再次进入地图界面点击任务图标")
        click(exit)
        pyautogui.press("m")
        click(self.safe_point)

        _status, (w, h) = point_mission
        if _status:
            self.screen_down()
        _rect = Rect(w, h, w+self.w, h+self.h)
        click(_rect)

    def get_mission_done_num(self):
        """获取当前有多少个任务已经完成"""
        screen = screenshot()
        num = 0
        for i in range(self.mission_queues):
            _point = self.point_get_list[i]
            patch = _point.patch_on_img(screen)
            ssim = skm.compare_ssim(patch, self.img_get, multichannel=True)
            # cv2.imwrite(f"{root}/patch_{i}.png", patch[..., ::-1])
            logging.info(f"第{i+1}个任务队列位置的ssim:\t{ssim:.4f}, 是否完成:{'是' if ssim>self.ssim_t else '否'}")
            num += ssim > self.ssim_t

        return num

    def click_get_mission(self, num):
        """领取任务奖励"""
        # num = self.get_mission_done_num()
        for i in range(num):
            logging.info(f"第[{i+1}/{num+1}]次领取任务奖励")
            click(self.point_get)  # 点击领取点
            click(self.point_ok)  # 点击OK确认
            click(self.safe_point)  # 点击安全点

    def click_start_mission_once(self):
        logging.info(f"点击第{self.mission_start_index}个任务图标")
        if self.mission_start_index >= self.mission_length:
            logging.info(f"异常!当前任务索引大于等于任务数,{self.mission_start_index}:{self.mission_length}")
            return False
        self.click_mission(self.click_list[self.mission_start_index])
        screen = screenshot()
        patch = self.point_start.patch_on_img(screen)
        status = self.get_misson_status(patch)
        status_dict = {1:"开始任务", 2:"已经开始", 3:"缺乏足够小分轨", 4:"已经完成", 5:"任务上限", 6:"其它"}
        logging.info(f"第{self.mission_start_index}个任务图标的状态为:\t{status_dict.get(status)}")
        # 实际上是先领取已经完成的任务，这里status不会取到4
        if status in [1, 2, 4, 6]:   # 1:开始任务;2:已经开始;4:已经完成;6:当前任务已经完成
            if status in [1, 4]:
                click(self.point_start)
            self.mission_start_index += 1
            click(self.safe_point)
            # 5个队列或者140级之后需要对于小队不够的往后移动
            return True

        click(self.safe_point)
        return False

    def init_missions(self):
        logging.info("初始化地图任务开始")
        click(self.safe_point)  # 进入安全点
        # 需初始化任务列表变量
        self.pt_list_1 = [[], [], [], [], [], []]
        self.pt_list_2 = [[], [], [], [], [], []]
        self.get_pts()
        self.order_pt()
        # self.test_pts()
        self.click_list = self.get_click_list()  # 获取可点击图标
        self.mission_length = len(self.click_list)  # 任务长度
        self.mission_start_index = 0  # 开始点击的位置为0
        logging.info(f"初始化地图任务结束，共有任务:{self.mission_length}, 开始点击位置为:{0}")

    def refresh_missions(self):
        """查看地图任务是否有更新"""
        logging.info("检验地图任务是否有更新")
        now = datetime.datetime.now()
        if now > self.next_fresh_time:
            logging.info("地图任务已经更新")
            self.init_missions()
            self.next_fresh_time = self.get_next_refresh_time()

    def run(self):
        """地图策略"""
        # 当前策略
        # 如果可领取队列为0，则退出
        # 如果可领取队列不为0, 则先领取任务，再开始任务
        logging.info("开始地图任务执行策略")
        self.refresh_missions()
        num = self.get_mission_done_num()
        self.click_get_mission(num)
        times = 0
        while times < self.mission_queues:
            mission_flag = self.click_start_mission_once()
            if mission_flag is False:
                break

        click(exit)


class Main():
    def __init__(self, map_next_refresh_time="06:00:00"):
        self.library = Library()
        self.family = Family()
        self.guard = Guard()
        # self.case = Case()
        self.map = Map(map_next_refresh_time)

        self.button_family = Rect(1870, 320, 2180, 570)  # 城镇界面中的工会按钮位置
        self.button_ride = Rect(237, 562, 495, 772)  # 工会界面中的远征按钮位置
        self.safe_area = Rect(2192, 1294, 2365, 1478)  # 城镇界面中的安全点击位置
        self.map_suggest = Rect(2470, 518, 2545, 580)  # 地图提示，表示地图有更新
        self.img_suggest = cv2.imread(f"{root}{os.sep}guaji{os.sep}map_suggest.png")[..., ::-1]
        self.reconnect_img = cv2.imread(reconnect_path, 0)
        self.normal_img = cv2.imread(normal_path, 0)
        self.normal_family_img = cv2.imread(normal_family_path, 0)
        self.ssim_t = 0.8

        self.exit_img = cv2.imread(f"{root}{os.sep}guaji{os.sep}exit.png")[..., ::-1]
        self.exit_max_times = 10
        self.exit_times = 1

    def is_guaji(self):
        pass

    def all_back2main(self):
        logging.info("异常场景恢复到挂机主界面")
        screen = screenshot()
        patch = exit.patch_on_img(screen)
        ssim_exit = skm.compare_ssim(patch, self.exit_img, multichannel=True)
        if ssim_exit < self.ssim_t:
            return
        if self.exit_times < self.exit_max_times:
            logging.info(f"第{self.exit_times}次退出当前界面")
            click(exit)
            self.exit_times += 1

    def run_guard(self):
        logging.info("从挂机界面进入守卫界面")
        pyautogui.press("G")
        time.sleep(2)

        self.guard.run()

    def run_library(self):
        logging.info("从挂机界面进入图书馆界面")
        pyautogui.press("L")
        time.sleep(2)

        self.library.run()

    def family_into_status(self):
        logging.info("判断是否出现重新连接的提示")
        screen = screenshot()
        gray = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
        patch = reconnect.patch_on_img(gray)
        ssim_reconnect = skm.compare_ssim(self.reconnect_img, patch)
        ssim_normal = skm.compare_ssim(self.normal_img, patch)
        ssim_family = skm.compare_ssim(self.normal_family_img, patch)
        logging.info(f"ssim normal:{ssim_normal:.4f}\t,ssim family:{ssim_family:.4f},\tssim reconnect:{ssim_reconnect:.4f}")
        if ssim_family > self.ssim_t:
            return 0  # 表示进入了工会界面
        elif ssim_reconnect > self.ssim_t:
            return 1  # 表示断线，出现重新连接
        elif ssim_normal > self.ssim_t:
            return 2  # 表示当前位于城镇界面
        else:
            return 3  # 其它异常情况

    def into_family(self):
        logging.info("判断是否网络连接正常")
        click(self.button_family)
        family_status = self.family_into_status()
        if family_status == 0:
            return True
        elif family_status == 1:
            global global_connect
            if global_connect > reconnect_times:
                return False
            global_connect += 1
            logging.info(f"第{global_connect}次进行重新连接")
            click(reconnect)
            time.sleep(5)
            status = self.family_into_status()
            if status == 2:
                return self.into_family()
            return False

        else:
            return False

    def run_family(self):
        logging.info("从挂机界面进入工会的远征界面")
        pyautogui.press("T")
        time.sleep(2)

        status = self.into_family()
        if status is True:
            click(self.button_ride)
            self.family.run()
        else:
            click(self.safe_area)  # 这里的点击取消弹窗
            click(exit)   # 重新连接的弹窗还在时需要点两次

    def press_delay(self):
        logging.info("按技能3过渡")
        _time = 3
        times = gap_time // _time
        while times > 0:
            pyautogui.press("3")
            time.sleep(_time)
            times -= 1

    def sleep_delay(self):
        logging.info("sleep过渡")
        time.sleep(gap_time)

    def get_map_suggest(self):
        screen = screenshot()
        patch = self.map_suggest.patch_on_img(screen)
        ssim = skm.compare_ssim(patch, self.img_suggest, multichannel=True)
        logging.info(f"地图任务提示:\t{ssim:.4f}")
        _map_threshold = 0.7  # 实测为0.7413
        return ssim > _map_threshold

    def run(self):
        iter = 1
        global global_connect
        global_connect = 0
        first_flag = True
        while True:
            logging.info(f"第{iter}次循环运行")
            self.exit_times = 1  # init
            self.all_back2main()
            click(reconnect)

            # 在地图前执行，避免背包或者升级打开遮挡住了地图提示
            self.run_guard()
            self.run_library()
            self.run_family()
            time.sleep(3)

            try:
                if first_flag:
                    pyautogui.press("M")
                    self.map.init_missions()
                    first_flag = False

                if self.get_map_suggest():
                    pyautogui.press("M")
                    self.map.run()
            except KeyboardInterrupt:
                sys.exit(0)
            except:
                print(traceback.print_exc())
                logging.info("map error")

            self.all_back2main()
            click(reconnect)  # 将鼠标返回到屏幕中间
            # self.sleep_delay()
            self.press_delay()
            iter += 1
