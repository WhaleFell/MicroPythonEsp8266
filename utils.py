# encoding=utf8
# utils/ConnectWIFI.py
import network
import utime
from machine import Pin
from utime import sleep
try:
    import uasyncio
except ImportError:
    import asyncio as uasyncio


import dht
import ntptime

### config ####
wifi_ssid = "HomeAP"
wifi_passwd = "992829hws"
###############

wifi = network.WLAN(network.STA_IF)  # 配置wifi模式为station


# 重试函数,异常处理:(带参数的修饰器)
def handle_error(tries=3):
    def deco(func):
        def wrapper(*arg, **kw):
            # 写逻辑
            for _ in range(tries):
                try:
                    return func(*arg, **kw)
                except Exception as e:
                    continue
            return False
        return wrapper
    return deco


def reversePin(pin: Pin):
    """反转 Pin 高低电平状态"""
    v = pin.value()
    if v:
        pin.value(0)
    else:
        pin.value(1)


def connectWIFI(wifi_ssid: str, wifi_passwd: str, timeout: int = 15) -> bool:
    """连接 WIFI"""
    global wifi

    if not wifi.isconnected():
        print("Connecting to a WIFI network")
        wifi.active(True)
        wifi.connect(wifi_ssid, wifi_passwd)
        i = 0
        print("Connection ing", end="")
        while not wifi.isconnected():
            utime.sleep(1)
            i += 1
            if i >= timeout:
                print("\nConnection timeout! Please check you SSID or PWD")
                return False
            print(".", end="")

    print("Connection successful!")
    print("network config:", wifi.ifconfig())
    return True
    # ('192.168.1.100', '255.255.255.0', '192.168.1.1', '8.8.8.8')


class SingSong(object):
    """操作蜂鸣器类"""

    def __init__(self, GPIO: int = 5):
        self.buzzer = Pin(GPIO, Pin.OUT)  # 设置蜂鸣器GPIO口为输入模式
        self.buzzer.value(0)

    async def play(self, data: str, interval: int = 0.8,  loop: bool = False):
        """异步操作蜂鸣器,使其按照规定的节奏
        (该蜂鸣器是高电平触发!)
        data 格式: 2-3-1-2-4
        表示响2s停(interval)s 
        loop 表示是否循环播放
        """
        lst = data.split("-")

        while True:
            for l in lst:
                l = float(l)
                self.start()
                sleep(l)
                self.stop()
                # sleep(interval)  # 暂停
                await uasyncio.sleep(interval)

            if not loop:
                break

    def sync_play(self, data: str, interval: int = 0.8,  loop: bool = False):
        """控制蜂鸣器"""
        lst = data.split("-")

        while True:
            for l in lst:
                l = float(l)
                self.start()
                sleep(l)
                self.stop()
                sleep(interval)  # 暂停

            if not loop:
                break

    def start(self):
        """设置为高电平,触发"""
        self.buzzer.value(1)

    def stop(self):
        """设置为低电平,关闭"""
        self.buzzer.value(0)

    def __del__(self):
        # 对象销毁时重新设置为低电平
        print("Object deleted!")
        self.buzzer.value(0)


class HcSr501(object):
    """操作Hc-Sr501的类"""

    def __init__(self, GPIO: int = 5) -> None:
        self.hc = Pin(GPIO, Pin.IN)
        self.hc.value(0)  # 一开始设置低电平

    @property
    def value(self):
        """属性值,获取当前电平状态"""
        return self.hc.value()


def get_dht11(pin: Pin) -> tuple:
    """DHT11 温度传感器模块"""
    d = dht.DHT11(pin)
    d.measure()  # 启动测量
    wd = d.temperature()
    sd = d.humidity()
    return wd, sd


@handle_error(tries=3)
def sync_ntp():
    """通过网络校准时间"""
    ntptime.NTP_DELTA = 3155644800  # UTC+8
    ntptime.host = 'ntp1.aliyun.com'
    ntptime.settime()
    return True


if __name__ == "__main__":
    # wifi.disconnect()
    connectWIFI(wifi_ssid, wifi_passwd)
