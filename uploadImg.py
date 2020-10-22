# -*- coding: utf-8 -*-
import oss2, random, os
from itertools import islice

class ossManager:
    def __init__(self, id, key, endPoint, bucket):
        self.accessId = id
        self.accessKey = key
        self.use(endPoint, bucket)

    def use(self, endPoint, bucket):
        self.endPoint = endPoint
        self.bucket = bucket
        self.url = 'https://' + self.bucket + self.endPoint.replace('http://','.') + '/'
        self.authObj = oss2.Auth(self.accessId, self.accessKey)
        self.bucketObj = oss2.Bucket(self.authObj, self.endPoint, self.bucket)



    def upload(self, localRoute, uploadRoute):
        # <yourObjectName>上传文件到OSS时需要指定包含文件后缀在内的完整路径，例如abc/efg/123.jpg。
        # <yourLocalFile>由本地文件路径加文件名包括后缀组成，例如/users/local/myfile.txt。
        if self.bucketObj.put_object_from_file(uploadRoute, localRoute).status == 200:
            return self.url + uploadRoute
        else:
            return None

    def ls(self, count):
        # oss2.ObjectIteratorr用于遍历文件。
        for b in islice(oss2.ObjectIterator(self.bucketObj), count):
            print(b.key)

    def delete(self, objName):
        # <yourObjectName>表示删除OSS文件时需要指定包含文件后缀在内的完整路径，例如abc/efg/123.jpg。
        self.bucketObj.delete_object(objName)

    def fileExists(self, filename):
        return self.bucketObj.object_exists(filename)

import pyperclip
def setClipText(text):
    pyperclip.copy(text)
    return text

from PIL import ImageGrab
def saveClipImg(filename):
    image = ImageGrab.grabclipboard() # 获取剪贴板文件
    if image != None:
        image.save(filename)
        return True
    else:
        return False


def randomStr(len=10,randomSrc='abcdefghijklmnopqrstuvwxyz'):
    return ''.join(random.sample(randomSrc, len))

if __name__ == '__main__':
    # 实例化 ossManager
    import json
    info = {}
    with open('./accessAccount.json') as f:
        info = json.loads(f.read())

    ossmanager = ossManager(id=info['accessId'], key=info['accessKey'], endPoint=info['endPoint'], bucket=info['bucket'])

    # 开启上传图片线程
    cacheFilename = 'cache.png'
    from hook import hook as hookConstructor
    def autoUpImg(key, status):
        if key == 121 and status == 128:
            # F10 弹起
            if saveClipImg(cacheFilename) == True:
                filename = randomStr()
                while (ossmanager.fileExists(filename) is True):
                    filename = randomStr()
                print('')
                url = ossmanager.upload(cacheFilename, filename)
                setClipText('![desc](' + url + ')')
                print(url, end='\n\nuploadImg>')
                print('uploadImg>', end='')
            else:
                print('')
                print('剪贴板中不存在有效文件', end='\n\nuploadImg>')
                

    hook = hookConstructor(keyb_callback=autoUpImg)
    hook.start_keyboard_hook()


    # 命令行
    print('\n图片上传\n\n')
    while True:
        print('uploadImg>', end='')
        try:
            commend = input().split(' ')
        except:
            continue
        commendLen = len(commend)
        if commend[0] == 'help':
            print('ls <showCount> —— 显示 <showCount> 条文件名称')
            print('up <localRoute> [-f 允许自动覆盖, [<uploadRoute> 缺省为随机字符串]] —— 上传本地文件 <localRoute> 到远程 <uploadRoute>')
            print('del <uploadRoute> —— 删除远程文件 <localRoute>')
            print('')
            continue
        if commend[0] == 'ls' and commendLen == 2:
            ossmanager.ls(int(commend[1]))
            print('')
            continue
        if commend[0] == 'del':
            commend.remove('del')
            for filename in commend:
                ossmanager.delete(filename)
            continue
        if commend[0] == 'up' and commendLen <= 4:
            try:
                if '-f' in commend:
                    # 允许覆盖
                    commend.remove('-f')
                    commendLen -= 1
                    if commendLen == 2:
                        print(ossmanager.upload(commend[1], randomStr()))
                    else:
                        print(ossmanager.upload(commend[1], commend[2]))
                else:
                    # 不允许覆盖
                    if commendLen == 2:
                        filename = randomStr()
                        while(ossmanager.fileExists(filename) is True):
                            filename = randomStr()
                        url = ossmanager.upload(commend[1], filename)
                        setClipText('![desc](' + url + ')')
                        print(url)
                    else:
                        if ossmanager.fileExists(commend[2]) is True:
                            print('远程 oss 对象名存在：' + commend[2])
                        else:
                            url = ossmanager.upload(commend[1], commend[2])
                            setClipText('![desc](' + url + ')')
                            print(url)
                print('')
            except Exception as err:
                print(err)
            continue
        if commend[0] == 'exit':
            # 删除 cache
            hook.stop_keyboard_hook()
            if os.path.exists(cacheFilename) == True:
                os.remove(cacheFilename)
            break
        print('语法错误：' + ' '.join(commend))
        print('')

