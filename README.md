[[English](README_en.md)] [[简体中文](README.md)]

## 简介

一个直播源转推脚本，基于强大的[Streamlink](https://streamlink.github.io)，能够在 YouTube、Twitch 等平台之间实现无缝的直播流转推。

## 已支持平台

- [x] Youtube
- [x] Twitch

## 使用

### 源码运行

```sh
# 克隆源码
git clone https://github.com/LyferLu/LiveRelay.git
cd LiveRelay
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate
# 安装依赖
pip install -r requirements.txt
# 源码运行
python main.py
```

## 配置

配置文件存储于`config.json`，该文件位于可执行程序相同目录

修改示例配置文件[`config.sample.json`](config.sample.json)后务必重命名为`config.json`

文件内容要求严格按照json语法，请前往在线json格式化网站校验后再修改

### 转推地址

按照示例修改`RTMPServer`字段

### 直播流配置

按照示例修改`streams`列表，注意逗号、引号和缩进

| 字段     | 含义         | 可填内容                 | 是否必填 | 备注                                              |
| -------- | ------------ | ------------------------ | -------- | ------------------------------------------------- |
| platform | 直播平台     | 直播平台的英文名         | 必填     | 大小写不敏感                                      |
| id       | 直播用户id   | 直播平台的房间号或用户名 | 必填     | 参考config文件示例格式<br/>一般在直播网址即可找到 |
| name     | 自定义主播名 | 任意字符                 | 非必填   |            |
| index    | 索引优先级   | int整形数字              | 必填     | 索引越小优先级越高                                |

#### YouTube的频道ID

YouTube的频道ID一般是由`UC`开头的一段字符，由于YouTube可以自定义标识名，打开YouTube频道时网址会优先显示标识名而非频道ID

获取YouTube的频道ID可以使用以下网站：

https://seostudio.tools/zh/youtube-channel-id

https://ytgear.com/youtube-channel-id

## 鸣谢

[https://github.com/auqhjjqdo/LiveRecorder](https://github.com/auqhjjqdo/LiveRecorder)

[https://github.com/gav-X/RepushStream](https://github.com/gav-X/RepushStream)