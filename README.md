# Music-Assist

基于Python的自用音乐助手脚本代码

## 介绍

项目目前支持仅支持网易云音乐的管理

项目主要的贡献在于：
+ 截至2024年03月11日，更新了对网易云音乐本地SQLite数据中歌单数据存储方式的认知
+ 针对xxx文件转换的mp3和flac文件，同时也保存了封面图片元数据，在播放时会显示封面图片

## 功能特性

+ 支持通过网易云歌单中的数量指定具体某个歌单并获取歌单中歌曲的信息
+ 支持将网易云音乐的音乐文件形成自组织的音乐数据库
+ 支持通过歌单信息输出从音乐数据库导出歌单中的歌曲到指定位置

## 安装

```bash
pip install -r requirements.txt
```

## 使用示例

具体使用方法查看对应文件上方注释
```bash
python -m music_base.py
python -m cloudmusic_playlist.py
```
## 版权和许可

本项目主要作交流学习，如有任何疑问，请联系leeal111@163.com

## 作者

Leeal

## 链接

项目主页: https://github.com/leeal111/music-assist