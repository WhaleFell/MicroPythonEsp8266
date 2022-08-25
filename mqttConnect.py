# mqttConnect
import gc
from umqtt.simple import MQTTClient
import urequests
from utils import connectWIFI, wifi
import config
import utime
# 兼容性导入
try:
    import uasyncio
except ImportError:
    import asyncio as uasyncio

# 启动垃圾回收器
gc.collect()


# mqtts://broker.diandeng.tech:1883 电灯科技

### Config ####
blinker_tk = "335562d5d103"
mserver = "broker-cn.emqx.io"
port = "1883"

client_id = "mqttx_b6b02f04"  # 可选
user = None
password = None
###############

client: MQTTClient = None


def online() -> bool:
    """点灯科技设备上线,获取 mqtt 协议配置"""
    global client_id, mserver, port, user, password

    url = "https://iot.diandeng.tech/api/v1/user/device/diy/auth?authKey=%s&protocol=mqtt" % blinker_tk
    resp = urequests.get(url).json()
    if resp.get("message") != 1000:
        return False
    mserver = resp['detail']['host'].replace("mqtt://", "")
    port = int(resp['detail']['port'])
    user = resp['detail']['iotId']
    password = resp['detail']['iotToken']
    client_id = resp['detail']['deviceName']

    print('''
#############
# MQTT: %s:%s 
# ClientID: %s
# User: %s
# Pwd: %s
# ###########    
    ''' % (mserver, port, client_id, user, password)
          )

    global client

    client = MQTTClient(
        server=mserver,
        port=int(port),

        client_id=client_id,
        user=user,
        password=password,
    )


class MQTT(object):
    """操作 MQTT 服务"""

    def __init__(
        self,
        server: str = mserver,
        port=int(port),

        client_id: str = client_id,
        user: str = user,
        password: str = password,
    ) -> None:
        global client

        client = MQTTClient(
            server=server,
            port=int(port),

            client_id=client_id,
            user=user,
            password=password,
        )

        self.client = client
        self.content = '{"timestamp":%s,"data":%s}'

    async def subScribe(self, cb: function, sub="hyy9420"):
        """订阅主题并保持连接,cb 为回调函数"""
        a = 0
        isNeedConnect = True  # 是否需要连接

        while True:
            try:
                if isNeedConnect:
                    print("connecting mqtt......")
                    self.client.connect()
                    isNeedConnect = False

                a += 1
                print(f"Keepconnect {a}")
                self.client.set_callback(cb)  # 设置回调
                self.client.subscribe(b'%s' % sub)  # 设置订阅
                self.client.check_msg()  # 非堵塞检查
            except Exception as e:
                # 如果连接发生错误就重连
                print(f"[ERROR] Reconnect Now!{e}")
                if not wifi.isconnected():
                    print("Network disconnect...")
                    connectWIFI(config.wifi_ssid, config.wifi_passwd)
                # 设置重连
                isNeedConnect = True

            await uasyncio.sleep(1)  # 异步休息

    async def pubScribe(self, topic: str, msg: str, retries=3, *args, **kw):
        """发布连接"""
        content = self.content % (
            utime.mktime(utime.localtime())+946656000, msg)

        for _ in range(retries):
            try:
                print(f"send {topic} {content}")
                self.client.publish(topic, content, *args, **kw)
                return
            except Exception as e:
                print(f"[Error]send err:{e}")
                await uasyncio.sleep(1)
                continue

    def syncPubScribe(self, topic: str, msg: str, retries=3, *args, **kw):
        """同步发布连接"""
        content = self.content % (
            utime.mktime(utime.localtime())+946656000, msg)

        for _ in range(retries):
            try:
                print(f"send {topic} {content}")
                self.client.publish(topic, content, *args, **kw)
                return
            except Exception as e:
                print(f"[Error]send err:{e}")
                continue

    async def ping(self):
        """保持ping链接"""
        while True:
            print("ping!")
            # self.client.ping()
            # self.client.publish("www9420", ="111")
            self.pubScribe("www9420", "111")
            await uasyncio.sleep(1)


def __sub_cb(topic, msg):  # 回调函数，收到服务器消息后会调用这个函数
    print(topic, msg)
    if "hello" in msg:
        client.publish("www9420", msg=b'hello esp8266')


async def main():
    mqtt = MQTT(mserver, port, client_id)
    # uasyncio.create_task(mqtt.keepConnect(sub_cb))
    # uasyncio.create_task(mqtt.pubConnect("hyy9999", "startstart!!!"))
    await uasyncio.gather(
        *(
            mqtt.keepConnect(__sub_cb),
            mqtt.pubConnect("hyy9999", "startstart!!!"),
            mqtt.ping()
        )
    )


if __name__ == "__main__":
    wifi.disconnect()
    print("wifi disconnect!")
    mqtt = MQTT()
    uasyncio.run(mqtt.subScribe(__sub_cb))
