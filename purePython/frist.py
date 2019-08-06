# -*- coding: utf-8 -*-
# @Time    : 2018/6/8
# @Author  : Torre
# @Email   : klyweiwei@163.com
# 免费下载酷狗音乐：通过歌手singerId即可以专辑下载歌手的所有歌曲。
# 具体过程：1.酷狗首页搜索歌手，进入歌手主页，获取url中的singId,例如朴树主页：http://www.kugou.com/singer/3520.html,其中3520即为singId;
# 2.根据歌手singerId可以获得歌手的所有专辑的albumId,例如 这是专辑的页面,http://www.kugou.com/yy/album/single/962593.html,其中962593为albumId
# 3.酷狗播放歌曲的实现方式，是通过ajax请求获取的服务器资源,点击播放某歌曲,播放页面打开F12,切至netWork,观察Request URL请求,如下
# 例如http://www.kugou.com/yy/index.php?r=play/getdata&hash=89AB193EC33E2AE6AF04BD408F8F1083&album_id=962593&_=1529057140131
# 经过测试发现(建议使用截包工具截获url请求),只需要(get请求)http://www.kugou.com/yy/index.php?r=play/getdata&hash=89AB193EC33E2AE6AF04BD408F8F1083
# 而每首歌有一个单独的hash,只要找到每首歌的hash,即可获取每首歌的ajax请求url,而这个hash存在于专辑页面中,bs4提取专辑内所有歌曲的hash.
# 4.可以发现其ajax请求的response信息中存在该歌曲的MP3资源url,那么通过urllib.request.urlretrieve()函数即可保存该歌曲.


import os
import urllib.request
import requests
import re
import json
import getSoup
# from urllib.request import urlretrieve

headers = {
    'origin': "http://www.kugou.com",
    'x-devtools-emulate-network-conditions-client-id': "97C9BAA42BE5A8449EC4283F764B4D9E",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
    'content-type': "application/x-www-form-urlencoded",
    'accept': "*/*",
    'referer': "http://www.kugou.com/singer/3520.html",
    'accept-encoding': "gzip, deflate",
    'accept-language': "zh-CN,zh;q=0.9",
    'cookie': "kg_mid=88665d81b7959ab3787c4976831a30f9; Hm_lvt_aedee6983d4cfc62f509129360d6bb3d=1528705681; Hm_lpvt_aedee6983d4cfc62f509129360d6bb3d=1528707581",
    'cache-control': "no-cache",
    'postman-token': "c717ef07-2b91-06f1-1d22-abcb47b0bce2"
}

# 获取歌手的所有album信息
def getAlbumid(singerID):
    # 获取歌单albumid
    url = "http://www.kugou.com/yy/"
    querystring = {"r": "singer/album", "sid": singerID}
    # headers = {
    #     'origin': "http://www.kugou.com",
    #     'x-devtools-emulate-network-conditions-client-id': "97C9BAA42BE5A8449EC4283F764B4D9E",
    #     'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
    #     'content-type': "application/x-www-form-urlencoded",
    #     'accept': "*/*",
    #     'referer': "http://www.kugou.com/singer/3520.html",
    #     'accept-encoding': "gzip, deflate",
    #     'accept-language': "zh-CN,zh;q=0.9",
    #     'cookie': "kg_mid=88665d81b7959ab3787c4976831a30f9; Hm_lvt_aedee6983d4cfc62f509129360d6bb3d=1528705681; Hm_lpvt_aedee6983d4cfc62f509129360d6bb3d=1528707581",
    #     'cache-control': "no-cache",
    #     'postman-token': "c717ef07-2b91-06f1-1d22-abcb47b0bce2"
    # }
    response = requests.request("POST", url, headers=headers, params=querystring)
    res = response.text
    # print(type(res))
    jsonRes = json.loads(res)
    loadAlbumids = []  # 保存albumids到list
    loadAlbumname = []
    albumids = jsonRes['data']
    for albumid in albumids:
        albumid = albumid['albumid']
        # print(albumid)
        loadAlbumids.append(albumid)
        # print(albumid)
    for albumname in albumids:
        albumname = albumname['albumname']
        albumname = albumname[0]
        loadAlbumname.append(albumname)
        # print(albumname)
    return loadAlbumname, loadAlbumids

# getAlbumid(2303)

# 获取该专辑内的所有歌曲的hash
def getMp3Info(albumid):
    url = 'http://www.kugou.com/yy/album/single/'+str(albumid)+'.html'
    soup = getSoup.getSoup(url)
    hashs = soup.select('.songList a')
    loadMp3Hash = []
    for hashss in hashs:
        hash = hashss.get('data')
        # 通过spilt('|')分割字符串,获取hash
        mp3Hash = hash.split('|')[0]
        # print(hash.split('|')[0])
        # hash = hash.spilt('|')
        loadMp3Hash.append(mp3Hash)
        # print(mp3Hash)
    return loadMp3Hash

# mp3 = getMp3Info(1645030)
# for i in range(len(mp3)):
#     print(mp3[i])


# 通过ajax请求获取歌曲的PlayerUrl
def getPlayUrl(hash, albumId):
    url = "http://www.kugou.com/yy/index.php"
    querystring = {"r": "play/getdata", "hash": hash, "album_id": albumId}
    response = requests.request("GET", url, headers=headers, params=querystring)
    response.raise_for_status()
    res = response.text
    #print(type(res))
    jsonRes = json.loads(res)
    playUrl = jsonRes['data']

    audioName = playUrl['audio_name']
    playUrl = playUrl['play_url']
    music = (audioName, playUrl)
    print('-'.join(music))
    return audioName, playUrl

# @test
# mp3 = getMp3Info(1645030)
# for i in range(len(mp3)):
#     print(mp3[i])
#     getPlayUrl(mp3[i], '1645030')


# 文件/文件夹的创建是不允许一些非法字符存在的,此函数过滤掉非法字符
def validateName(name):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_name = re.sub(rstr, "", name)
    return new_name

# 进度信息
def cbk(a,b,c):
    per=100.0*a*b/c
    if per>100:
        per=100
    print('%.2f%%' % per)


# # 保存为MP3, 保存到特定文件夹下面：文件夹以专辑名字命名; 注意,在代码的根目录下创建mp3文件夹
def saveAudio(url, album, filename):
    filepath = os.getcwd()+'\\mp3\\'+album
    if os.path.exists(filepath):
        mp3 = os.path.join(filepath + '\\', '' + filename + '.mp3')
        if url == '':
            print('the url is NUll, pass')
        else:
            urllib.request.urlretrieve(url, mp3, cbk)
    else:
        os.makedirs(filepath)
        mp3 = os.path.join(filepath + '\\', '' + filename + '.mp3')
        if url == '':
            print('the url is NUll, pass')
        else:
            urllib.request.urlretrieve(url, mp3, cbk)


# 运行主程序, 只需要填入 歌手ID即可(http://www.kugou.com/yy/html/singer.html,
# 点击任一歌手即可获得其ID), 可以自动下载其所有专辑 : 比如3043 代表 许巍; 61874代表Sophia zelmani;朴树2303;34450 Taylor Swift
def downloadMp3(singerId):
    albumname, albumids = getAlbumid(singerId)
    # length = len(albumids)
    # print(albumids)
    for i in range(len(albumids)):
        hashs = getMp3Info(albumids[i])
        for ii in range(len(hashs)):
            audioName, playUrl = getPlayUrl(hashs[ii], albumids[i])
            saveAudio(playUrl, validateName(albumname[i]), validateName(audioName))


# 调用函数 ,下载歌曲
downloadMp3(34450)
