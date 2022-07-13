from screeninfo import get_monitors
from math import sqrt

def cm2inch(cm):
    return cm / 2.54


def inch2cm(inch):
    return 2.54 * inch


def get_dpi(monitor_inch):

    for m in get_monitors():
        if m.is_primary:
            width, height = m.width, m.height
            print(f'size={width}x{height}')
            break

    dots = sqrt(width**2 + height**2)
    dpi = dots / monitor_inch

    return dpi


def get_pixel(cm, monitor_inch):
    return cm2inch(cm) * get_dpi(monitor_inch)


if __name__ == '__main__':
    monitor_inch = 43
    print(get_dpi(monitor_inch))
    print(get_pixel(5, monitor_inch))
