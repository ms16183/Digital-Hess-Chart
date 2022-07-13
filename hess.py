import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import io

from screeninfo.common import Monitor

import info



class HessChart:
    def __init__(self, cm, inch, name, fixing_point_angle, angle=45, limit=1):
        """Hessチャート描画

        Args:
            cm (float): モニタ上の長さ(センチメートル)．
            name (str): Hessチャートのタグ名．
            inch (float): モニタの対角線のインチ数
            fixing_point_angle (tuple): 固定点の角度．
            angle (float, optional): Hessチャートの表示角度. Defaults to 45.
            limit (float, optional): matplotlibの出力範囲指定. Defaults to 1.
        """
        # モニタ上の長さ
        self.cm = cm
        # Hessチャート名
        self.name = name
        # 対角インチ
        self.inch = inch
        # 固定点
        self.fixing_point_angle = fixing_point_angle
        # 視線の点
        self.point = (None, None)
        # Hessチャートの角度範囲
        self.angle = angle
        # matplotlibの出力範囲(調整用)
        self.limit = limit

        dpi = info.get_dpi(self.inch)

        print(f'figsize={cm/2.54}, dpi={dpi}')

        # 余白なしでグラフ生成
        self.fig = plt.figure(figsize=(cm/2.54, cm/2.54), dpi=dpi)
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self.ax = self.fig.add_subplot(1, 1, 1)

        self.draw()

            
    def draw(self, angle=None, limit=None):
        """チャートを描画する．

        Args:
            angle (float, optional): Hessチャートの表示角度. Defaults to None.
            limit (float, optional): matplotlibの出力範囲指定. Defaults to None.
        """
        if angle is None:
            angle = self.angle
        if limit is None:
            limit = self.limit

        # すべて消去
        self.fig.gca().clear()

        # 横軸(色は赤)
        phi = np.linspace(-angle, angle, 100) * np.pi/180
        theta = np.arange(90-angle, 90+angle, 5) * np.pi/180
        for t in theta:
            x = np.tan(phi)
            y = np.cos(t) / (np.sin(t)*np.cos(phi))
            self.ax.plot(x, y, 'r:')

        # 縦軸(色は赤)
        beta = np.linspace(-angle, angle, 100) * np.pi/180
        alpha = np.arange(90-angle, 90+angle, 5) * np.pi/180
        for a in alpha:
            x = np.cos(a) / (np.sin(a)*np.cos(beta))
            y = np.tan(beta)
            self.ax.plot(x, y, 'r:')

        # 固定点のプロット
        self.draw_point(*self.fixing_point_angle)

        # 範囲指定，目盛の削除
        self.ax.set_xlim(-limit, limit)
        self.ax.set_ylim(-limit, limit)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def convert_hess_coordinate(self, vertical_angle, horizontal_angle):
        """角度からHessチャート上の座標の値に変換する．

        Args:
            vertical_angle (float): 垂直角度[deg]
            horizontal_angle (float): 水平角度[deg]

        Returns:
            float: 座標(x, y)
        """
        alpha = (90-vertical_angle) * np.pi/180
        theta = (90-horizontal_angle) * np.pi/180
        phi = np.arctan(np.cos(alpha)/np.sqrt(np.sin(theta)**2-np.cos(alpha)**2))
        x = np.tan(phi)
        y = np.cos(theta)/(np.sin(theta)*np.cos(phi))
        return x, y
        

    def draw_point(self, vertical_angle, horizontal_angle, color='r', use_xy=False):
        """チャートに点を打つ．

        Args:
            vertical_angle (float): 垂直角度[deg]
            horizontal_angle (float): 水平角度[deg]
            color (str, optional): 色
            use_xy (bool, optional): 引数を(x, y)として捉える．
        """
        if use_xy:
            x, y = vertical_angle, horizontal_angle
        else:
            x, y = self.convert_hess_coordinate(vertical_angle, horizontal_angle)

        self.point = (x, y)
        self.ax.plot(x, y, color+'.')

        
    def get_point(self):
        return self.point
    
    def get_fixing_point_angle(self):
        return self.fixing_point_angle


    def get_hess_chart(self):
        """Hessチャートをfigureオブジェクトとして取得する．

        Returns:
            matplotlib.Figure: Hessチャートのfigure
        """
        return self.fig

    
    def get_hess_chart_as_byte(self):
        """Hessチャートをバイト列のデータとして取得する．

        Returns:
            byte: Hessチャートのバイト列
        """
        # グラフを画像形式に変換
        item = io.BytesIO()
        self.fig.savefig(item, format='png')
        return item.getvalue()


    def get_chart_info(self):
        return info.get_dpi(self.inch), info.get_pixel(self.cm, self.inch)

        
    def get_chart_name(self):
        return self.name



if __name__ == '__main__':
    charts = [HessChart(12.6, f'id_{i}', (0, 0)) for i in range(5)]
    charts[2].draw_point(0, 0)
    charts[2].draw_point(5*np.pi/180, -5*np.pi/180)
    p = charts[2].get_point()
    print(p)
    plt.show()
