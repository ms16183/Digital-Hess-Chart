import PySimpleGUI as sg
import csv
from datetime import datetime
from info import ConfigInfo
from hess import HessChart
import depthai as dai
from math import fabs, tan, pi
from statistics import mean
from imutils.video import FPS

# 設定ファイルロード
ci = ConfigInfo('./config.ini')
width = ci.width
height = ci.height
dpi = ci.dpi
angle = ci.max_angle
fixed_depth = ci.fixed_depth
pixel = ci.pixel

# チャート(両眼9方向)
charts = [
    # 左眼
    HessChart('LEFT, top left',     dpi, (-15,  15), angle, fixed_depth), HessChart('LEFT, top',     dpi, (0,  15), angle, fixed_depth), HessChart('LEFT, top right',     dpi, (15,  15), angle, fixed_depth),
    HessChart('LEFT, left',         dpi, (-15,   0), angle, fixed_depth), HessChart('LEFT, center',  dpi, (0,   0), angle, fixed_depth), HessChart('LEFT, right',         dpi, (15,   0), angle, fixed_depth),
    HessChart('LEFT, bottom left',  dpi, (-15, -15), angle, fixed_depth), HessChart('LEFT, bottom',  dpi, (0, -15), angle, fixed_depth), HessChart('LEFT, bottom right',  dpi, (15, -15), angle, fixed_depth),
    # 右眼
    HessChart('RIGHT, top left',    dpi, (-15,  15), angle, fixed_depth), HessChart('RIGHT, top',    dpi, (0,  15), angle, fixed_depth), HessChart('RIGHT, top right',    dpi, (15,  15), angle, fixed_depth),
    HessChart('RIGHT, left',        dpi, (-15,   0), angle, fixed_depth), HessChart('RIGHT, center', dpi, (0,   0), angle, fixed_depth), HessChart('RIGHT, right',        dpi, (15,   0), angle, fixed_depth),
    HessChart('RIGHT, bottom left', dpi, (-15, -15), angle, fixed_depth), HessChart('RIGHT, bottom', dpi, (0, -15), angle, fixed_depth), HessChart('RIGHT, bottom right', dpi, (15, -15), angle, fixed_depth),
]

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
window = sg.Window('Digital Hess Chart', layout,  disable_close=True, resizable=False, location=(width//2-pixel//2, 0))
window.finalize()

# 描画データ設定(Hessチャート，緑ポインタカーソル, 25サイズ)
graph_hess = window['-graph-'].draw_image(data=charts[chart_index].get_hess_chart_as_byte(), location=(0, 0))
cursor = window['-graph-'].draw_point((-100, -100), 25, color='green')

# カーソル設定(カーソル非表示)
window['-graph-'].set_cursor('none')

# バインド(カーソルの動き，左クリック)
window['-graph-'].bind('<Motion>', 'motion')
window['-graph-'].bind('<ButtonPress-1>', 'click')

# ---------- メインループ ----------
while True:

    event, values = window.read()

    # マウス移動時，緑ポインタの表示
    if event == '-graph-motion':
        # マーカーを左上から中心にシフト
        mouse_x = window['-graph-'].user_bind_event.x - 25/2
        mouse_y = window['-graph-'].user_bind_event.y - 25/2
        window['-graph-'].relocate_figure(cursor, mouse_x, mouse_y)


    # 切替えボタン押下時，Hessチャートの切り替え
    if event in ('-prev-', '-next-'):
        if event == '-prev-':
            chart_index = (chart_index - 1) % len(charts)
        if event == '-next-':
            chart_index = (chart_index + 1) % len(charts)

        # Hessチャートを切り替え
        graph_hess = window['-graph-'].draw_image(data=charts[chart_index].get_hess_chart_as_byte(), location=(0, 0))
        # カーソルを最前面に
        window['-graph-'].bring_figure_to_front(cursor)
        # チャート名切り替え
        window['-state-'].update(charts[chart_index].get_chart_name())


    # クリック時，グラフクリック位置の記録
    if event == '-graph-click':
        # マウス位置を座標に変換(中心を(0,0)，x=[-1, 1], y=[-1, 1])
        mousex = window['-graph-'].user_bind_event.x
        mousey = window['-graph-'].user_bind_event.y
        x =  2 * (mousex/pixel - 0.5)
        y = -2 * (mousey/pixel - 0.5)

        #print(f'[clicked]: x={x:.5f}, y={y:.5f}')

        # ポイント(前の点を消すためにグラフ自体を再描画)
        charts[chart_index].draw()
        charts[chart_index].draw_point(x, y, color='g', use_xy=True)

        # 再描画
        graph_hess = window['-graph-'].draw_image(data=charts[chart_index].get_hess_chart_as_byte(), location=(0, 0))
        window['-graph-'].bring_figure_to_front(cursor)

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

# ログ出力用のリストを生成
logdata = [['Name', 'Fixing Point Yaw', 'Fixing Point Pitch', 'Point Yaw', 'Point Pitch']]
for c in charts:
    logdata.append([c.get_chart_name(), *c.get_fixing_point_angle(), *c.convert_angle(*c.get_point())])
logdata = list(zip(*logdata)) # 転置
# ログをファイル出力
with open(datetime.now().strftime('%Y_%m_%d_%H_%M_%S')+'_dhc.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(logdata)
