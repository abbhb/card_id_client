import atexit
import base64
import json
import os
import threading
import time
import random
from datetime import datetime
import uuid
import time
import cv2
import numpy
# from picamera2 import Picamera2
# import face_recognition
import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QUrl, pyqtSignal, QThread, QTimer, QDateTime, QProcess, QByteArray
from PyQt5.QtGui import QPixmap
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
import requests
import serial

from PyQt5.QtWidgets import *

import sys

from config import search_uri, server_port, java_server_ip,secert,service_id
from consul_service import ConsulService
from card_panel import SuccessDataPanel, noDataPanel, ErrorDataPanel, loadingDataPanel
from card_data_lite import CardData
from flask_server import app as _app
face_tip_text = "欢迎您使用人脸签到系统!"
print("注意：ip必须为10段，且网关必须为10.15.247.254！！！")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
# lunxun update
shared_variable = {
    'all_card_list': [],
    'all_card_ext': {},
}


serial_port = serial.Serial(
    port='/dev/ttyS0',
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
)


# 创建一个锁，用于确保在访问共享变量时的线程安全性
shared_variable_lock = threading.Lock()


def get_filename_without_extension(file_path):
    file_name_with_extension = os.path.basename(file_path)
    file_name_without_extension = os.path.splitext(file_name_with_extension)[0]
    return file_name_without_extension


def list_image_files(directory):
    image_files = []
    # 遍历目录中的所有文件和子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 拼接文件的绝对路径
            file_path = os.path.join(root, file)
            image_files.append(file_path)
    return image_files

def detect_faces_in_image(type='file_stream', file_stream=None, imgn=None):
    pass

'''
def detect_faces_in_image(type='file_stream', file_stream=None, imgn=None):
    # Load the uploaded image file
    img = []
    if type == 'file_stream':
        img = face_recognition.load_image_file(file_stream)
    elif type == 'img':
        img = imgn
    else:
        img = imgn
    # Get face encodings for any faces in the uploaded image
    unknown_face_encodings = face_recognition.face_encodings(img, model='large')

    face_data = []
    with shared_variable_lock:
        copy_faces = shared_variable["all_face_list"]
        copy_faces_ext = shared_variable["all_face_ext"]
    if len(unknown_face_encodings) > 0:
        face_found = True
        # See if the first face in the uploaded image matches the known face of Obama
        try:
            print(copy_faces)
            match_results,weizhi = face_recognition.compare_faces(copy_faces, unknown_face_encodings[0], 0.35)
            print(weizhi)
            if match_results is False:
                return {"msg": '未找到人脸', "code": -1, "username": ""}
            zhegeface = copy_faces[weizhi]
            # Return the result as json
            print(zhegeface)
            print(face_data)

            result = {
                "code": 1,
                "msg": '找到脸了',
                "username": copy_faces_ext[tuple(zhegeface)]['username'],
                "student_id": copy_faces_ext[tuple(zhegeface)]['student_id']
            }
            return result
        except Exception as e:

            print(e)
            return {"msg": 'wufashibie', "code": -2, "username": ""}


    else:
        return {"msg": 'wufashibie', "code": -1, "username": ""}
'''



class MainPanel(QWidget):
    def __init__(self):
        super(MainPanel, self).__init__()

        # 获取显示器分辨率
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.screenheight = self.screenRect.height()
        self.screenwidth = self.screenRect.width()

        print("Screen height {}".format(self.screenheight))
        print("Screen width {}".format(self.screenwidth))

        self.height = int(self.screenheight * 0.7)
        self.width = int(self.screenwidth * 0.7)

        self.resize(self.width, self.height)

        # self.resize(800, 600)
        # mainPanel_layout = QHBoxLayout()
        self.mainPanel_layout = QGridLayout()
        # 预览四个边都预留20pixs的边界
        self.mainPanel_layout.setContentsMargins(20, 20, 20, 20)
        # 网格之间设置10pixs的间隔
        self.mainPanel_layout.setSpacing(10)
        self.button_layout = QGridLayout()
        self.mainPanel_layout.addLayout(self.button_layout, 0, 1)


        # must init after
        self.init_button_ui()
        self.init_user_info_ui()

        self.one = onePanel()
        self.two = twoPanel()
        self.three = initDataPanel()
        self.successFaceWidget = successFaceWidget()
        self.qls = QStackedLayout()
        self.qls.addWidget(self.one)
        self.qls.addWidget(self.two)
        self.qls.addWidget(self.three)
        self.qls.addWidget(self.successFaceWidget)

        self.mainPanel_layout.addLayout(self.qls, 0, 0)

        self.setLayout(self.mainPanel_layout)
        # init
        self.qls.setCurrentIndex(2)

        self.initDataWorkerThread = initDataWorkerThread()
        self.initDataWorkerThread.init_jindu_signal.connect(self.updateInitJindu)
        self.initDataWorkerThread.start()
        # 识别进程在数据初始化进度为100%时再启动,这个是人脸的代码
        # self.captureThread = CaptureWorkerThread()
        # self.captureThread.update_shibie_signal.connect(self.updateImage)
        # self.captureThread.update_video_frame_signal.connect(self.updateFrameUser)
        # self.captureThread.success_qiandao.connect(self.updateSuccessFace)
        # 读卡进程
        self.cardReadWorkerThread = CardReadWorkerThread()
        self.cardReadWorkerThread.update_shibie_signal.connect(self.guocheng)
        self.cardReadWorkerThread.success_qiandao.connect(self.shibiechenggong)
        # 热更新人脸识别线程
        self.update_card_data = UpdataCardDataThread()
        #flask service thread
        # self.flask_process = QProcess(self)
        # self.flask_process.readyReadStandardOutput.connect(self.read_output)
        # self.flask_process.start('python', ['flask_server.py'])
        # 注册设备到consul，并注册ip和端口，和设备id

    def read_output(self):
        output = self.flask_process.readAllStandardOutput().data().decode()
        if 'Running on' in output:
            print(output)
        else:
            print("-----------------")
            print(output)

    # def read_output(self):
    #     output = self.flask_process.readAllStandardOutput().data().decode()
    #     if 'Running on' in output:
    #         QMessageBox.information(self, 'Flask启动成功', output)
    def init_button_ui(self):
        self.button_layout.setContentsMargins(20, 20, 20, 20)
        # 网格之间设置10pixs的间隔
        self.button_layout.setSpacing(10)
        select_Panel1_button = QPushButton("panel1")
        select_Panel2_button = QPushButton("panel2")
        select_Panel3_button = QPushButton("panel3")
        select_Panel4_button = QPushButton("panel4")
        self.qlabel = QLabel()
        self.qlabel.setStyleSheet("QLabel{background:white;}"
                                      "QLabel{color:block;font-size:20px;font-weight:bold;font-family:宋体;}"
                                      )
        # 动态显示时间在label上
        self.qlabel.setText(face_tip_text)
        self.qlabel.setFixedWidth(200)
        # 创建一个定时器
        self.succcess_timer = QTimer(self)
        self.succcess_timer.timeout.connect(self.success_executeAfterDelay)
        self.succcess_timer.setSingleShot(True)  # 设置为单次触发

        # qlabel.setMinimumSize(self.width * 0.1, self.height)
        # self.button_layout.addWidget(select_Panel1_button,4, 0)
        # self.button_layout.addWidget(select_Panel2_button, 5, 0)
        # self.button_layout.addWidget(select_Panel3_button, 6, 0)
        # self.button_layout.addWidget(select_Panel4_button, 7, 0)
        self.button_layout.addWidget(self.qlabel, 3, 0)
        select_Panel1_button.clicked.connect(lambda: self.buttonIsClicked(select_Panel1_button))
        select_Panel2_button.clicked.connect(lambda: self.buttonIsClicked(select_Panel2_button))
        select_Panel3_button.clicked.connect(lambda: self.buttonIsClicked(select_Panel3_button))
        select_Panel4_button.clicked.connect(lambda: self.buttonIsClicked(select_Panel4_button))

        self.init_time_ui()

    def init_time_ui(self):
        self.time_label = QLabel(self)
        self.time_label.setFixedWidth(300)
        self.time_label.move(90, 80)
        self.time_label.setStyleSheet("QLabel{background:white;}"
                                      "QLabel{color:rgb(300,300,300,120);font-size:20px;font-weight:bold;font-family:宋体;}"
                                      )
        self.time_label.setFixedHeight(200)
        # 动态显示时间在label上
        timer = QTimer(self)

        timer.timeout.connect(self.update_time_v)

        timer.start(1000)
        self.button_layout.addWidget(self.time_label, 0, 0)

    def init_user_info_ui(self):
        self.user_info = QStackedLayout()

        self.success_info = SuccessDataPanel()
        self.error_info = ErrorDataPanel()
        self.default_info = noDataPanel()
        self.loading_info = loadingDataPanel()
        self.user_info.addWidget(self.default_info)
        self.user_info.addWidget(self.success_info)
        self.user_info.addWidget(self.error_info)
        self.user_info.addWidget(self.loading_info)
        self.button_layout.addLayout(self.user_info,1,0)
        self.user_info.setCurrentIndex(0)

    def success_executeAfterDelay(self):
        self.qlabel.setStyleSheet("QLabel{background:white;}"
                                  "QLabel{color:block;font-size:20px;font-weight:bold;font-family:宋体;}"
                                  )
        self.qlabel.setText(face_tip_text)

    def update_time_v(self):
        datetime = QDateTime.currentDateTime()
        text = datetime.toString()
        self.time_label.setText("     " + text)

    def buttonIsClicked(self, button):
        dic = {
            "panel1": 0,
            "panel2": 1,
            "panel3": 2,
            "panel4": 3,
        }
        index = dic[button.text()]
        self.qls.setCurrentIndex(index)

    def updateInitJindu(self, jindu: int):
        self.qls.setCurrentIndex(2)

        self.three.updateJindu(jindu)

        if jindu == 100:
            self.initDataWorkerThread.quit()
            self.qls.setCurrentIndex(0)
            # todo:需要
            self.cardReadWorkerThread.start()

            self.update_card_data.start()

    def shibiechenggong(self, status:bool,obj: object):
        if status:
            self.success_info.updateData(obj["school_id"],obj["name"],obj["thumbnail"])
            self.user_info.setCurrentIndex(1)
        else:
            self.error_info.showMsg(obj["card_status"])
            self.user_info.setCurrentIndex(2)

        # self.qls.setCurrentIndex(0)
        # self.one.updateFrame(base64)
        # self.update_user_face()
        pass
    # def update_user_face(self,base64:str):



    def guocheng(self, shifoushibie: bool):
        # shifoushibie 为true就是在识别否则就是切换默认视图
        if shifoushibie:
            self.user_info.setCurrentIndex(0)
        else:
            self.user_info.setCurrentIndex(3)
        # self.two.update(base64)
        # self.qls.setCurrentIndex(1)

    def updateSuccessFace(self,status,yunbase64:str,username):
        self.succcess_timer.stop()
        if status:
            self.qlabel.setStyleSheet("QLabel{background:white;}"
                                      "QLabel{color:green;font-size:20px;font-weight:bold;font-family:宋体;}"
                                      )
            self.qlabel.setText("["+username+"]签到成功！")
            self.user_info_web_view.page().runJavaScript("success('" + yunbase64 + "')")
        else:
            self.user_info_web_view.page().runJavaScript("error_s()")
            self.qlabel.setStyleSheet("QLabel{background:white;}"
                                      "QLabel{color:red;font-size:20px;font-weight:bold;font-family:宋体;}"
                                      )
            self.qlabel.setText("签到失败，请重试！")


        self.succcess_timer.start(3000)
        pass


class onePanel(QWidget):
    def __init__(self):
        super(onePanel, self).__init__()
        self.setStyleSheet('''QWidget{background-color:#66CCFF;}''')

        self.onePanel_layout = QHBoxLayout()

        self.webview = QWebEngineView()

        self.webview.load(QUrl("https://webvpn.beihua.edu.cn"))

        # self.qlabel = QLabel("wait!!!!!!!!!!!!!!!!!")
        self.onePanel_layout.addWidget(self.webview)
        self.setLayout(self.onePanel_layout)

    def updateFrame(self, base64):
        # height, width, channel = frame.shape
        # bytesPerLine = 3 * width
        # qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
        # pixmap = QPixmap.fromImage(qImg)
        # self.qlabel.setPixmap(pixmap)

        self.webview.page().runJavaScript("showframe('" + base64 + "')")


class twoPanel(QWidget):
    def __init__(self):
        super(twoPanel, self).__init__()
        self.setStyleSheet('''QWidget{background-color:#66ffcc;}''')

        twoPanel_layout = QHBoxLayout()
        self.webview = QWebEngineView()

        twoPanel_layout.addWidget(self.webview)
        self.webview.load(QUrl("file://"+search_uri))
        self.setLayout(twoPanel_layout)

    def update(self, base64: str):
        # print(base64)
        self.webview.page().runJavaScript("document.getElementById('needImage').src = '" + base64 + "'")
        pass


class successFaceWidget(QWidget):
    def __init__(self):
        super(successFaceWidget, self).__init__()
        self.setStyleSheet('''QWidget{background-color:#66ffcc;}''')

        successFace_layout = QHBoxLayout()
        self.webview = QWebEngineView()
        self.webview.setFixedWidth(1600)
        self.webview.setFixedHeight(1080)
        successFace_layout.addWidget(self.webview)
        self.webview.load(QUrl("file://"+search_uri))
        self.setLayout(successFace_layout)

    def update(self, base64: str):
        # print(base64)
        self.webview.page().runJavaScript("document.getElementById('needImage').src = '" + base64 + "'")
        pass

# init data time show
class initDataPanel(QWidget):
    def __init__(self):
        super(initDataPanel, self).__init__()
        # self.setStyleSheet('''QWidget{background-color:#ee0000;}''')

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.progressBar = QtWidgets.QProgressBar()

        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        # threePanel_layout = QHBoxLayout()
        self.qlabel = QLabel("init ...")

        self.verticalLayout.addWidget(self.qlabel)
        self.verticalLayout.addWidget(self.progressBar)
        self.statusbar = QtWidgets.QStatusBar()
        self.statusbar.setObjectName("statusbar")
        self.verticalLayout.addWidget(self.statusbar)
        # threePanel_layout = QHBoxLayout()
        # self.qlabel = QLabel("init ...")
        # threePanel_layout.addWidget(self.qlabel)

        self.setLayout(self.verticalLayout)

    def updateJindu(self, jindu: int):
        print(jindu)
        # self.qlabel.setText("init "+str(jindu)+"%")
        self.progressBar.setProperty("value", jindu)
        pass

class CardReadWorkerThread(QThread):
    update_shibie_signal = pyqtSignal(bool)
    success_qiandao = pyqtSignal(bool, object)

    def deal_card(self,card_id):
        print(f"读取到卡号：{card_id}")
        obj = {
            "code": 0,# 失败
            "card_status": "欢迎回来",
            "name": "",
            "class": "未知",
            "school_id": "",
            "room": "未知",
            "card_num": card_id,
            "thumbnail": ""
        }
        # 取数据
        with shared_variable_lock:
            copy_cards = shared_variable["all_card_list"]
            copy_cards_ext = shared_variable["all_card_ext"]
        if str(card_id) in copy_cards_ext:

            try:
                ids = uuid.uuid4()
                current_time = datetime.now()
                current_local_datetime = current_time.strftime("%Y-%m-%d %H:%M:%S")
                json_data = {"id": str(ids),
                             "studentId": copy_cards_ext[str(card_id)]["student_id"],
                             "signinTime": current_local_datetime,
                             "signinDeviceId": service_id,
                             "signinWay": "card",
                             }
                headers = {"Content-Type": "application/json", "signin_secret": secert}

                response = requests.post("http://" + java_server_ip + ":55550/api/signin_log/add_log_device_plus",
                                         json=json_data, headers=headers)
                if response.status_code == 200:
                    asddqwr = response.json()
                    if str(asddqwr["code"])=='1':

                        # 正常
                        obj = {
                            "code": 1,
                            "card_status": "欢迎回来",
                            "name": copy_cards_ext[str(card_id)]["username"],
                            "class": "未知",
                            "school_id": copy_cards_ext[str(card_id)]["student_id"],
                            "room":  asddqwr["data"]["deptName"],
                            "card_num": card_id,
                            "thumbnail": asddqwr["data"]["avatarUrl"]
                        }
                    else:
                        obj["code"] = 0
                        obj["card_status"] = asddqwr["msg"]

            except Exception as e:
                print(e)
        else:
            obj["code"] = 0
            obj["card_status"] = "卡不存在!"
            print("卡不存在!")
        # 尝试发送签到请求，成功才提示成功




        print(obj)
        serial_port.flushInput()
        return obj
    def run(self):
        while True:
            try:
                if serial_port.inWaiting() > 0:
                    # 不管如何到最后等待3s后发送更新视图取更新回默认视图
                    data = serial_port.readline().strip()
                    print(f"读取到数据：{data}")
                    s = data.decode("utf-8")[2:]
                    if s:
                        self.update_shibie_signal.emit(True)
                        objk = self.deal_card(int(s, 16))
                        if objk["code"]==0:
                            # 失败
                            self.success_qiandao.emit(False,objk)
                        elif objk["code"]==1:
                            # 成功
                            self.success_qiandao.emit(True,objk)
            except Exception as exception_error:
                print(f"程序发生错误，错误信息：{str(exception_error)}")



# init Data
class initDataWorkerThread(QThread):
    # 定义一个带有参数的信号
    init_jindu_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def run(self):
        dangqianjindu = 1
        self.init_jindu_signal.emit(dangqianjindu)
        all_card_list = []
        all_card_ext = {}
        card_data = CardData()
        all_users_rows = card_data.list_all_user()
        self.init_jindu_signal.emit(dangqianjindu)

        for user in all_users_rows:
            # jindu + item_jindu
            # user_face is face
            try:
                card_data_ = numpy.array(json.loads(user[0]))

            except Exception as e:
               continue
            all_card_list.append(card_data_)
            all_card_ext[str(card_data_)] = {
                'username': user[2],
                'student_id': user[1],
            }

        # print("数据库数据-------------------")
        # print(all_users_face_rows)
        # jindu + 1
        dangqianjindu += 5
        self.init_jindu_signal.emit(dangqianjindu)

        with shared_variable_lock:
            shared_variable["all_card_list"] = all_card_list
            shared_variable["all_card_ext"] = all_card_ext
            print("写成功")
        self.init_jindu_signal.emit(99)
        # finish,100% jiu shi wan cheng le
        card_data.__del__()
        self.init_jindu_signal.emit(100)


class UpdataCardDataThread(QThread):
    # 定义一个带有参数的信号

    def __init__(self):
        super().__init__()


    def run(self):
        while True:
            time.sleep(20)
            print("20s update")
            # every 10 min update face data once
            all_card_list = []
            all_card_ext = {}
            card_data = CardData()
            all_users_rows = card_data.list_all_user()
            for user in all_users_rows:
                # jindu + item_jindu
                # user_face is face
                try:
                    card_data_ = numpy.array(json.loads(user[0]))

                except Exception as e:
                    continue
                all_card_list.append(card_data_)
                all_card_ext[str(card_data_)] = {
                    'username': user[2],
                    'student_id': user[1],
                }
            with shared_variable_lock:
                shared_variable["all_card_list"] = all_card_list
                shared_variable["all_card_ext"] = all_card_ext



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainPanel()
    main.show()
    consulasd = ConsulService()


    def cleanup():
        print("Python程序即将退出")
        # 在这里执行清理操作，例如关闭文件、释放资源等
        consulasd.clean()


    atexit.register(cleanup)
    kwargs = {'host': '0.0.0.0', 'port': server_port, 'threaded': True, 'use_reloader': False, 'debug': False}
    threading.Thread(target=_app.run, daemon=True, kwargs=kwargs).start()
    sys.exit(app.exec_())
