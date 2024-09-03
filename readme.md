# 安装指引


## 推荐python3.8（apt安装即可）
## 前置
如果你的是python3.8就对应改命令，结合自己环境


不知道你用的python在哪
```which python3.8```

如果默认python命令为空，但是apt安装了3.8可以结合自己路径设置，最后的1代表优先级为1
```sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1```



某python的pip升级命令
```python -m pip install --upgrade pip```

设置镜像源，报错说明版本还没升级
```python -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple```




# consul_service.py文件里注意修改本机ip


## 新的Ubuntu_desktop18.04
### 1.设置apt源为清华源并apt upgrade
### 2.sudo apt install python3.8
### 3.设置python3.8为默认python
```
which python3.8
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1
sudo update-alternatives --install /usr/bin/python python /usr/local/bin/python3 2
第二个为兼容默认的，优先级为2
```
### 额外步骤，这步不确定有没有用，照做就行
```sudo apt install python3-pip```

### 4.安装额外工具
```bash
sudo apt-get -y install cmake g++
sudo apt-get -y install mesa-common-dev
sudo apt-get -y install libglu1-mesa-dev
```
### 5.pip换源，没法换需要在有代理的网络环境下先更新pip
```
python -m pip install --upgrade pip
```
```python -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple```

### 6.拉取代码，傻子都会
### 7.安装requirement.txt

### 8. sudo apt-get install libxcb-xinerama0
这步解决qt运行不起来，xcb报错，此版本环境下应该是缺这个，其他问题结合文末链接自己debug

### 9.已经能运行find_[find_card_qt_v2.py](examples%2Ffind_card_qt_v2.py)
记得修改网络和config.py里的配置

### 10.运行前记得给dev/ttyS0的777权限，不然会报错的


# 全局解决问题

https://blog.csdn.net/LOVEmy134611/article/details/107212845 解决qt-xcb
