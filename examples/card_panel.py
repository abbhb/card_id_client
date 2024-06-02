from io import BytesIO

import requests
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel


class noDataPanel(QWidget):
    def __init__(self):
        super(noDataPanel, self).__init__()
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.qlabel = QLabel("请刷卡!")
        self.verticalLayout.addWidget(self.qlabel)
        self.setLayout(self.verticalLayout)

class loadingDataPanel(QWidget):
    def __init__(self):
        super(loadingDataPanel, self).__init__()
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.qlabel = QLabel("识别中!")
        self.verticalLayout.addWidget(self.qlabel)
        self.setLayout(self.verticalLayout)


class SuccessDataPanel(QWidget):
    def __init__(self):
        super(SuccessDataPanel, self).__init__()
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.qlabel = QLabel("签到成功")
        self.photo = QLabel()
        self.user_img = QPixmap("unknown.png")
        self.photo.setPixmap(self.user_img)
        self.verticalLayout.addWidget(self.qlabel)
        self.setLayout(self.verticalLayout)
    def updateData(self,student_id:str,name:str,photo:str) -> None:
        self.user_img.load("unknown.png")
        try:
            # 下载图像数据
            response = requests.get(photo)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                self.user_img.loadFromData(image_data.getvalue())
            else:
                print("无法加载图像，状态码:", response.status_code)
        except:
            print("异常")
        self.qlabel.setText(name+",签到成功!["+student_id+"]")
class ErrorDataPanel(QWidget):
    def __init__(self):
        super(ErrorDataPanel, self).__init__()
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.qlabel = QLabel("签到失败!")
        self.verticalLayout.addWidget(self.qlabel)
        self.setLayout(self.verticalLayout)
    def showMsg(self,msg:str='请刷卡!') -> None:
        self.qlabel.setText(msg)
