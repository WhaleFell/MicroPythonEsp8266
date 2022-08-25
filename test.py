# 测试文件

from machine import Pin
import utime
from machine import Pin
from utils import SingSong


def test1():
    GPIO = 5  # 蜂鸣器管脚定义
    buzzer = Pin(GPIO, Pin.OUT)  # 设置蜂鸣器GPIO口为输入模式

    while True:
        buzzer.value(1)  # 设置为高电平
        utime.sleep(0.3)  # 延时
        buzzer.value(0)  # 设置为低电平
        utime.sleep(1)  # 延时


def test2():
    from machine import Pin, PWM
    import utime

    # 定义音调频率
    tones = {'1': 262, '2': 294, '3': 330, '4': 349,
             '5': 392, '6': 440, '7': 494, '-': 0}
    # 定义小星星旋律
    melody = "1155665-4433221-5544332-5544332-1155665-4433221"

    # 设置D7（GPIO 13）口为IO输出，然后通过PWM控制无缘蜂鸣器发声
    beeper = PWM(Pin(5, Pin.OUT), freq=0, duty=1000)

    for tone in melody:
        freq = tones[tone]
        if freq:
            beeper.init(duty=1000, freq=freq)  # 调整PWM的频率，使其发出指定的音调
        else:
            beeper.duty(0)  # 空拍时一样不上电
        # 停顿一下 （四四拍每秒两个音，每个音节中间稍微停顿一下）
        utime.sleep_ms(400)
        beeper.duty(0)  # 设备占空比为0，即不上电
        utime.sleep_ms(100)

    beeper.deinit()  # 释放PWM


def test__():
    p5 = Pin(5, Pin.IN)
    sound = SingSong(GPIO=15)  # 蜂鸣器引脚
    sound.stop()
    p5.value(0)
    while True:
        print(p5.value(), end="")
        # # 人进入感应访问就输出高电平
        if (p5.value() == 1):
            sound.start()
        else:
            sound.stop()
        utime.sleep_ms(500)


test__()

if __name__ == "__main__":
    # test1()
    # sound = SingSong(GPIO=15)  # 蜂鸣器引脚
    # sound.play("1-1-1", loop=True)
    pass
