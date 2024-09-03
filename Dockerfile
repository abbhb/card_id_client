# 使用官方的 Ubuntu 20.04 镜像作为基础镜像
FROM python:3.8.10-slim-buster

# 设置环境变量，以便后续命令不会等待用户输入
ENV DEBIAN_FRONTEND=noninteractive

# 更新软件包列表并安装所需的基础软件
RUN apt update
RUN apt remove -y \
    gcc \
    g++
RUN apt install -y \
    g++ \
    cmake

RUN export CC=/usr/bin/gcc
RUN export CXX=/usr/bin/g++
## 设置 Python 3.8 作为默认版本
#RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1

# 安装 pip，并使用清华源替换默认源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install --upgrade pip
# 设置工作目录
WORKDIR /app

# 复制当前目录的所有内容到容器中的 /app 目录
COPY . /app


# 设置环境变量
#ENV PATH="/usr/bin/g++:/usr/bin/cmake:${PATH}"
ENV PYTHONUNBUFFERED=1

# 安装 Python 依赖
RUN pip install -r requirements.txt

# 暴露应用程序的端口
EXPOSE 12354

WORKDIR /app/examples
# 进入 example 目录并启动应用程序
ENTRYPOINT ["uvicorn","face2recognition_api:app","--host","0.0.0.0","--port","12354","--reload"]
