# ESP8266 MicroPython 入门笔记

## 介绍

该项目基于 `MicroPython` 使用 `esp8266` 单片机制作，定时上传温湿度到 mqtt 服务器，检测到人体就启动蜂鸣器并推送mqtt，可以通过 mqtt 控制蜂鸣器和板载 ide 灯，查询是否存在人体。方便我出去时监控我的房间是否有父母进入。进入就推送到 mqtt 到我的手机。本项目采用 Asyncio 支持，可以多个任务运行在同一时间线上，不会堵塞，高效处理。

## 烧写镜像

```shell
python -m esptool read_mac  # 读取设备
python -m esptool -p COM6 erase_flash  # 擦除闪存
python -m esptool --port COM6 --baud 460800 write_flash --flash_size=detect 0 esp8266-20220618-v1.19.1.bin  # 烧录固件
```

## MicroPython 连接 WIFI
esp8266芯片的核心就是与wifi功能，对应使用micropython里面的network模块。  

wifi模块有两种模式:

- STA_IF 也就是station站点模式，将本芯片作为客户端连接到已知的无线网络上
- AP_IF 也就是AP/热点模式，将本芯片作为无线热点，等待其他客户端连接上来

### WIFI 热点创建
```python
import network
ap = network.WLAN(network.AP_IF)  # 指定用ap模式
ap.active(True)                   # 启用wifi前需要先激活接口
ap.config(essid="EUROPA-AP")      # 设置热点名称
ap.config(authmode=3, password='1234567890')  # 设置认证模式与密码
```
config 参数:  
mac, MAC地址
essid, 热点名称
channel, wifi通道
hidden, 是否隐藏
authmode, 认证模式
	0 – 无密码
	1 – WEP认证
	2 – WPA-PSK
	3 – WPA2-PSK
	4 – WPA/WPA2-PSK
password, 连接密码
dhcp_hostname, DHCP主机名

> 使用AP热点模式时，esp8266芯片可提供的连接数量是有限的，最多支持4个客户端连接。

### 连接 WIFI
```python
import network
import utime

sta_if = network.WLAN(network.STA_IF)  # 配置wifi模式为station
if not sta_if.isconnected():   # 判断有无连接
    print('connecting to network...')
    sta_if.active(True)        # 激活wifi接口
    sta_if.connect('<essid>', '<password>')  # 连接现有wifi网络，需要替换为已知的热点名称和密码
    while not sta_if.isconnected():
        utime.sleep(1)   # 未连接上就等待一下，直到连接成功
print('network config:', sta_if.ifconfig())  # 输出当前wifi网络给自己分配的网络参数
# ('192.168.1.100', '255.255.255.0', '192.168.1.1', '8.8.8.8')
```

### 连接网络
一旦wifi网络连接成功，那咱们就可以畅游网络，网络连接在micropython中主要是使用或封装socket模块来实现。

七层网络协议知道吧，socket模块应该是介于应用层和网络层+传输层中间的一个抽象封装，为上层应用层提供直接使用底层网络的能力。

## 上传文件
```shell
ampy --port COM6 put test.txt
```

```shell
用法: ampy [OPTIONS] COMMAND [ARGS]...

  ampy - Adafruit MicroPython工具

  Ampy是一个通过串行连接控制MicroPython板的工具。
  使用ampy，你可以操作板子内部文件系统上的文件，甚至运行脚本。
  甚至运行脚本。

选项。
  -p, --port PORT 连接板的串口名称。 可以选择
                     可以用AMPY_PORT环境变量指定。 [必需] -b, --baud

  -b, --baud BAUD 串行连接的波特率（默认为115200）。
                     可以选择用AMPY_BAUD环境变量来指定
                     变量指定。

  -d, --delay DELAY 进入RAW模式前的延迟时间，单位为秒（默认为0）。
                     可以选择用AMPY_DELAY环境变量来指定。
                     变量指定。

  --version 显示版本并退出。
  --help 显示此信息并退出。

命令。
  get 从板子上取回一个文件。
  ls 列出棋盘上一个目录的内容。
  mkdir 在板上创建一个目录。
  put 把一个文件或文件夹及其内容放在板上。
  reset 对板子进行软复位/重启。
  rm 从板上删除一个文件。
  rmdir 从板上强行删除一个文件夹及其所有子文件夹。
  run 运行一个脚本并打印其输出。

通过www.DeepL.com/Translator（免费版）翻译
```