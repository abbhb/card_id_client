#!/bin/bash
sudo -S chmod -R 777 /dev/ttyS0 << EOF
aizhineng1404
EOF
# 启动PyQt5项目
python3 ./find_card_qt_v2.py
