import serial
from openpyxl import Workbook

mode = int(input("若打卡器返回的为10进制请输入1，16进制则输入2"))
if mode != 1 and mode != 2:
    print("mode不对，请输入1，或2")
    exit(10)
serial_port = serial.Serial(
    port='/dev/ttyS0',
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
)
cards = []
try:
    while True:
        try:
            if serial_port.inWaiting() > 0:
                # 不管如何到最后等待3s后发送更新视图取更新回默认视图
                data = serial_port.readline().strip()
                print(f"读取到数据：{data}")
                s = data.decode("utf-8")[2:]
                if s:
                    card_id = int(s)
                    if mode == 2:
                        card_id = int(card_id,16)
                    print(f"读取到卡号：{card_id}")
                    cards.append(card_id)
        except Exception as exception_error:
            print(f"程序发生错误，错误信息：{str(exception_error)}")
except KeyboardInterrupt:
    # 录完了
    # 关闭串口
    serial_port.close()
    # 将卡号列表写入Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "卡号列表10-18"

    for i, card_id in enumerate(cards, start=1):
        ws[f'A{i}'] = card_id

    wb.save("卡号列表.xlsx")

    print(f"读取到的卡号列表：{cards}")
