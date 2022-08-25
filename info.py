import configparser
from screeninfo import get_monitors
from math import sqrt
import numpy as np

class ConfigInfo:
    def __init__(self, path='./config.ini'):
        """設定ファイルの情報のやりとり

        Args:
            path (str, optional): iniファイルのパス. Defaults to './config.ini'.
        """
        # パーサー
        config = configparser.ConfigParser()
        config.read(path)

        # モニター情報
        self.width = config['screen'].getfloat('Width')
        self.height = config['screen'].getfloat('Height')
        self.inch = config['screen'].getfloat('MonitorInch')

        dots = sqrt(self.width**2 + self.height**2)
        self.dpi = dots / self.inch

        # Hessチャート設定
        self.fixed_depth = config['hess'].getfloat('fixed_depth')
        self.max_angle = config['hess'].getfloat('max_angle')
        self.cm = 2 * np.tan(self.max_angle*np.pi/180) * self.fixed_depth
        self.pixel = self.cm / 2.54 * self.dpi
    
    
    def get_monitor_info(self):
        """モニター情報の取得

        Returns:
            (float, float, float, float): 幅, 高さ, 対角インチ数, DPI
        """
        return self.width, self.height, self.inch, self.dpi

        
    def get_hess_info(self):
        """Hessチャート情報の取得

        Returns:
            float, float: 一辺の長さ[cm], 画面上のピクセル数
        """
        return self.cm, self.pixel



def cm2inch(cm):
    return cm / 2.54


def inch2cm(inch):
    return 2.54 * inch


if __name__ == '__main__':
    ci = ConfigInfo('./config.ini')
    w, h, inch, dpi = ci.get_monitor_info()
    print(f'Monitor: {w} x {h}, dpi={dpi:.1f}')
    cm, pix = ci.get_hess_info()
    print(f'Hess: {cm}cm x {cm}cm = {pix:.1f}pixel x {pix:.1f}pixel')