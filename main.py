# encoding=utf8
# microPY main
import config
import time
from utils import SingSong, connectWIFI, get_dht11, sync_ntp, HcSr501, reversePin
from mqttConnect import MQTT
from machine import Pin
import dht

try:
    import uasyncio
except ImportError:
    import asyncio as uasyncio


sound = SingSong(GPIO=15)  # 蜂鸣器引脚

led = Pin(2, Pin.OUT)  # 板载 led 默认为高电平熄灭
dh = Pin(4)  # DH 温度传感器
hc = HcSr501(GPIO=5)  # Hc-sr 501 人体感应器


# 初始化 MQTT 服务器
mqtt = MQTT(
    server=config.mserver,
    port=config.port,
    client_id=config.client_id,
    user=config.user,
    password=config.password,
)


def init():
    """初始化操作,非异步"""

    # 循环连接 WIFI 设备
    while True:
        led.value(0)
        isWifi = connectWIFI(config.wifi_ssid, config.wifi_passwd)
        if isWifi:
            led.value(1)
            break
        else:
            led.value(1)
            time.sleep(1)

    if sync_ntp():
        print("Sync Ntp Success!")


def handle_msg(topic, msg):
    print(f"rec {topic}:{msg}")
    # 切换 板载 led 灯状态
    if "led" in msg:
        reversePin(led)

    # 控制蜂鸣器
    elif "sound" in msg:
        reversePin(sound.buzzer)

    # 获取人体感应器信息
    elif "hc" in msg:
        if hc.value == 1:
            msg = "somebody"
        else:
            msg = "nobody"

        mqtt.syncPubScribe(topic="/hyyhome/pub/hc/", msg=msg)

    # 测试信息
    elif "test" in msg:
        mqtt.syncPubScribe(topic="/hyyhome/pub/test/", msg="online!")


async def asyncDht11():
    """每5秒获取DHT11温度传感器数值,获取6次取平均数后上传mqtt"""
    wd_lst = []
    sd_lst = []
    while True:
        for _ in range(6):
            wd, sd = get_dht11(dh)
            wd_lst.append(wd)
            sd_lst.append(sd)
            print(f"{wd} {sd}")
            await uasyncio.sleep(5)
        # 计算平均值
        avg_wd = sum(wd_lst)/len(wd_lst)
        avg_sd = sum(sd_lst)/len(sd_lst)
        await mqtt.pubScribe("/hyyhome/pub/dht11/", msg='{"wd":%s,"sd":%s}' % (round(avg_wd, 1), round(avg_sd, 1)))
        wd_lst.clear()
        sd_lst.clear()


async def asyncHc():
    """监听人体感应器的信息"""
    save_v = 0
    while True:
        v = hc.value
        if v != save_v:
            if v == 1:
                msg = "somebody"
            else:
                msg = "nobody"
            save_v = v
            print(f"[HC] {msg}")
            await mqtt.pubScribe(topic="/hyyhome/pub/hc/", msg=msg)
            sound.start()
            await uasyncio.sleep(2)
            sound.stop()

        await uasyncio.sleep(1)


async def main():
    """main() 异步执行"""
    print("Asyncio start run!")
    # uasyncio.gather(
    #     *(
    #         # 监听 /hyyhome/fetch/ 下的所有信息
    #         mqtt.subScribe(sub="/hyyhome/fetch/#", cb=handle_msg)
    #     )
    # )
    # await mqtt.subScribe(sub="/hyyhome/fetch/#", cb=handle_msg)
    # await print("test...")

    # 打包成一个 task 才可以运行
    uasyncio.create_task(asyncDht11())
    uasyncio.create_task(asyncHc())
    # await 等待这个 task 运行完成,起到 while True 的作用
    await uasyncio.create_task(mqtt.subScribe(sub="/hyyhome/sub/#", cb=handle_msg))


if __name__ == "__main__":
    init()
    uasyncio.run(main())
