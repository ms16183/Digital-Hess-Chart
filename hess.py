import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import io

class HessChart:
    def __init__(self, name, dpi, fixing_point_angle, angle, depth):
        """Hessチャート描画

        Args:
            name (str): Hessチャートのタグ名
            dpi (float): モニタのDPI[inch]
            fixing_point_angle (tuple): 固定点の角度[deg]
            angle (float): Hessチャートの角度範囲(-angle~angle)[deg]
            depth (float): スクリーンと被験者との固定距離[cm]
        """
        # Hessチャート名
        self.name = name
        # DPI
        self.dpi = dpi
        # 固定点
        self.fixing_point_angle = fixing_point_angle
        # 視線の点
        self.point = (None, None)
        # Hessチャートの角度範囲
        self.angle = angle
        # 固定距離
        self.depth = depth

        self.cm =  2 * np.tan(angle*np.pi/180) * self.depth
        self.limit = np.tan(angle*np.pi/180)

        # 余白なしでグラフ生成
        self.fig = plt.figure(figsize=(self.cm/2.54, self.cm/2.54), dpi=self.dpi)
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self.ax = self.fig.add_subplot(1, 1, 1)

        self.draw()

            
    def draw(self):
        """チャートを描画する．
        """
        angle = self.angle
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


    def convert_angle(self, x, y):
        """Hessチャート上の座標から角度に変換する．

        Args:
            x (float): x座標
            y (float): y座標

        Returns:
            float: 角度(v, h)[deg]
        """
        phi = np.arctan(x)
        theta = np.arctan(1/(y*np.cos(phi)))

        alpha = np.arccos(np.sqrt(np.sin(theta)**2*np.tan(phi)**2/(np.tan(phi)**2+1)))

        horizontal_angle = (np.pi/2 - theta)*180/np.pi
        vertical_angle = (np.pi/2 - alpha)*180/np.pi

        if x < 0:
            vertical_angle *= -1
        if y < 0:
            horizontal_angle -= 180

        return vertical_angle, horizontal_angle
        

    def draw_point(self, vertical_angle, horizontal_angle, color='r', use_xy=False):
        """チャートに点を打つ．

        Args:
            vertical_angle (float): 垂直角度[deg]
            horizontal_angle (float): 水平角度[deg]
            color (str, optional): 色
            use_xy (bool, optional): 引数を[-1, 1]の間の(x, y)として捉える．
        """
        if use_xy:
            x, y = vertical_angle*self.limit, horizontal_angle*self.limit
        else:
            x, y = self.convert_hess_coordinate(vertical_angle, horizontal_angle)

        # https://www.web-dev-qa-db-ja.com/ja/python/matplotlib%E7%89%B9%E5%AE%9A%E3%81%AE%E7%B7%9A%E3%81%BE%E3%81%9F%E3%81%AF%E6%9B%B2%E7%B7%9A%E3%82%92%E5%89%8A%E9%99%A4%E3%81%99%E3%82%8B%E6%96%B9%E6%B3%95/1043286160/
        self.point = (x, y)
        self.ax.plot(x, y, color+'.', markersize=50)

        
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


    def get_chart_name(self):
        return self.name



if __name__ == '__main__':
    charts = [HessChart(12.6, f'id_{i}', (0, 0)) for i in range(5)]
    charts[2].draw_point(0, 0)
    charts[2].draw_point(5*np.pi/180, -5*np.pi/180)
    p = charts[2].get_point()
    print(p)
    plt.show()
