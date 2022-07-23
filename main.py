from datetime import datetime
import PySimpleGUI as sg
import csv
import datetime
import configparser
import info
from hess import HessChart
import depthai
import signal
import numpy as np
from math import atan, atan2
from cam import Main, create_pipeline

device = depthai.Device(create_pipeline())
app = Main(device)

# Ctrl+C検出
def signal_handler(sig, frame):
    app.running = False
signal.signal(signal.SIGINT, signal_handler)

# 設定ファイルロード
config = configparser.ConfigParser()
config.read('config.ini')
# チャート(両眼9方向)
# 作りたいサイズ，モニターのインチ数
cm = config['screen'].getfloat('HessSize')
inch = config['screen'].getfloat('MonitorInch')
charts = [
    # 左眼
    HessChart(cm, inch, 'LEFT, top left',    (-15,  15)), HessChart(cm, inch, 'LEFT, top',    (0,  15)), HessChart(cm, inch, 'LEFT, top right',    (15,  15)),
    HessChart(cm, inch, 'LEFT, left',        (-15,   0)), HessChart(cm, inch, 'LEFT, center', (0,   0)), HessChart(cm, inch, 'LEFT, right',        (15,   0)),
    HessChart(cm, inch, 'LEFT, bottom left', (-15, -15)), HessChart(cm, inch, 'LEFT, bottom', (0, -15)), HessChart(cm, inch, 'LEFT, bottom right', (15, -15)),
    # 右眼
    HessChart(cm, inch, 'RIGHT, top left',    (-15,  15)), HessChart(cm, inch, 'RIGHT, top',    (0,  15)), HessChart(cm, inch, 'RIGHT, top right',    (15,  15)),
    HessChart(cm, inch, 'RIGHT, left',        (-15,   0)), HessChart(cm, inch, 'RIGHT, center', (0,   0)), HessChart(cm, inch, 'RIGHT, right',        (15,   0)),
    HessChart(cm, inch, 'RIGHT, bottom left', (-15, -15)), HessChart(cm, inch, 'RIGHT, bottom', (0, -15)), HessChart(cm, inch, 'RIGHT, bottom right', (15, -15)),
]
dpi, pixel = charts[0].get_chart_info()

# 表示するチャートを指定
chart_index = 0

# デザインテーマ
sg.theme('Dark Blue')

# ---------- レイアウト ----------
layout = [
    [sg.Text(charts[chart_index].get_chart_name(), key='-state-')],
    [sg.Button('Prev', key='-prev-'), sg.Button('Next', key='-next-'), sg.Button('Quit', key='-quit-')], 
    [sg.Graph((pixel, pixel), (0, pixel), (pixel, 0), background_color='white', pad=(0, 0), key='-graph-')],
]
window = sg.Window('Digital Hess Chart', layout,  disable_close=True, resizable=False, location=(0, 0))
window.finalize()

# 描画データ設定(Hessチャート，緑ポインタカーソル)
graph_hess = window['-graph-'].draw_image(data=charts[chart_index].get_hess_chart_as_byte(), location=(0, 0))
cursor = window['-graph-'].draw_point((-100, -100), 5, color='green')

# カーソル設定(カーソル非表示)
window['-graph-'].set_cursor('none')

# バインド(カーソルの動き，左クリック)
window['-graph-'].bind('<Motion>', 'motion')
window['-graph-'].bind('<ButtonPress-1>', 'click')

# ---------- メインループ ----------
for horizontal_angle, vertical_angle in app.run():

    event, values = window.read(timeout=100, timeout_key='-timeout-')

    # 切替えボタン押下時，Hessチャートの切り替え
    if event in ('-prev-', '-next-'):
        if event == '-prev-':
            chart_index -= 1 
        if event == '-next-':
            chart_index += 1

        if chart_index < 0:
            chart_index = len(charts) - 1
        if chart_index > len(charts) - 1:
            chart_index = 0

        # Hessチャートを切り替え
        graph_hess = window['-graph-'].draw_image(data=charts[chart_index].get_hess_chart_as_byte(), location=(0, 0))
        # カーソルを最前面に
        window['-graph-'].bring_figure_to_front(cursor)
        # チャート名切り替え
        window['-state-'].update(charts[chart_index].get_chart_name())


    # timeout毎に取得した視線を表示
    if event == '-timeout-':
        h, v = horizontal_angle, vertical_angle
        '''
        # カメラ角度追加
        w, h = info.get_monitor_dot()
        v -= atan2(h/2, 30)
        '''
        # 左右反転
        h = -h

        # ポイント(前の点を消すためにグラフ自体を再描画)
        charts[chart_index].draw()
        charts[chart_index].draw_point(h, v, color='g')
        # 再描画
        graph_hess = window['-graph-'].draw_image(data=charts[chart_index].get_hess_chart_as_byte(), location=(0, 0))
        window['-graph-'].bring_figure_to_front(cursor)

        # ログ
        print(f'{charts[chart_index].get_chart_name()}')
        print(f'fixing point: {charts[chart_index].get_fixing_point_angle()}')
        print(f'  your point: {charts[chart_index].convert_angle(*charts[chart_index].get_point())}')
        print(f'')

    # 終了ボタン押下時，アプリケーションの終了
    if event in (None, '-quit-'):
        if sg.PopupYesNo('Are you quit?') == 'Yes':
            break


# ---------- 終了処理 ----------
# GUI終了
window.close() 

# カメラ終了
device.close()

# ログ出力用のリストを生成
logdata = [['Name', 'Fixing Point Yaw', 'Fixing Point Pitch', 'Point Yaw', 'Point Pitch']]
for c in charts:
    logdata.append([c.get_chart_name(), *c.get_fixing_point_angle(), *c.convert_angle(*c.get_point())])
logdata = list(zip(*logdata)) # 転置
# ログをファイル出力
with open(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')+'_dhc.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(logdata)
