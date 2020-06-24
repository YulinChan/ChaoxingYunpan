#!/bin/python3
import requests
from bs4 import BeautifulSoup


# cookie有效期为一个月
# 还可利用ocr图片识别解决验证码,直接登录账号
# 利用os模块做成可在命令行执行的脚本
class cxpan:
    def __init__(self, uid, uf):
        self.uid = uid
        self.uf = uf
        self.homeId = '340970115999633408'
        self.cookies = {'UID': uid, 'uf': uf}
        self.ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162'
        self.header = {'User-Agent': self.ua,
                       'Host': 'pan-yz.chaoxing.com',
                       'Origin': 'http://pan-yz.chaoxing.com',
                       'Referer': 'http://pan-yz.chaoxing.com/'}
        self.session = requests.session()

    def post(self, url, params):
        return self.session.post(url, params=params, cookies=self.cookies, headers=self.header)

    def ls(self, parentId='340970115999633408'):
        params = {'puid': self.uid, 'parentId': parentId, 'enc': '42cdd418cc0fc9abca54fc44c82d4471'}
        mp = self.post('https://pan-yz.chaoxing.com/opt/listres', params)
        l = mp.json()['list']
        print("{:^25}\t{:^11}\t{:^18}\t{:^16}".format("File Name", "File Size", "File ID", "Dowanload Link"))
        for i in l:
            if i['isfile']:
                objectId = i['objectId']
                size = str(round(i['filesize'] / 1024 ** 2, 2)) + 'MB'
                dlink = f'https://d0.ananas.chaoxing.com/download/{objectId}'
                print("{:<25}\t{:<11}\t{:<18}\t{:<}".format(i['name'], size, i['id'], dlink))
            else:
                print("{:<25}\t{:^11}\t{:<18}".format(i['name'], "Dir", i['id']))

    # 一次只能删除一个，要想批量删除，puids，resoursetype都要写多个
    def rm(self, resids):
        params = {'resids': resids, 'puids': self.uid, 'resourcetype': '0'}
        p = self.post('https://pan-yz.chaoxing.com/opt/delres', params)
        print(p.json())

    def rename(self, resid, name):
        params = {'resid': resid, 'name': name, 'puid': self.uid}
        p = self.post('https://pan-yz.chaoxing.com/opt/rename', params)
        print(p.json()['msg'])

    # 移动多个，用逗号分隔
    def mv(self, resids, folderid):
        params = {'resids': resids, 'folderid': folderid + '_' + self.uid, 'puid': self.uid}
        p = self.post('https://pan-yz.chaoxing.com/opt/moveres', params)
        print(p.json())

    # 可在根目录创建,但不可创建共享文件夹
    def mkdir(self, name, parentId):
        params = {'name': name, 'parentId': parentId, 'puid': self.uid}
        p = self.post('https://pan-yz.chaoxing.com/opt/newfolder', params)
        msg = p.json()['msg']
        folderid = p.json()['data']['id']
        print(msg, folderid)

    # 可创建共享文件夹(不限于根目录)，但返回数据中不带邀请码，需要ls获取
    # 参数selectDlid控制是否共享文件夹，有onlyme，allperson可选
    def mkroot(self, name, parentId, selectDlid):
        params = {'name': name, 'parentId': parentId, 'selectDlid': selectDlid}
        p = self.post('https://pan-yz.chaoxing.com/opt/newRootfolder', params)
        msg = p.json()['msg']
        folderid = p.json()['data']['id']
        print(msg, folderid)

    # 分享文件
    def share(self, resids, vt, type):
        # vt:分享时限VT_ONE_DAY、VT_ONE_WEEK、VT_ONE_MONTH、VT_FOREVER；type：加密/公开分享 SHARE_WITH_PASSWORD、SHARE_NORMAL
        params = {'resids': resids, 'vt': vt, 'type': type}
        p = self.post('https://pan-yz.chaoxing.com/share/create', params)
        print(p.json())

    # 获取文件的md加密串
    def md5(self, resids):
        params = {'resids': resids, 'puids': self.uid}
        p = self.post('https://pan-yz.chaoxing.com/opt/getMd5Enc', params)
        print(p.json())
        return p.json()['Md5Enc']

    def dl(self, resids):
        # 批量下载
        params = {'resids': resids, 'puids': self.uid}
        url = 'https://ypdownload.chaoxing.com/opt/batchdownload_' + self.md5(resids)
        p = self.post(url, params)
        print(p.url)
        return p.url

    # 单文件上传限制
    def getLimit(self):
        r = requests.get('https://pan-yz.chaoxing.com/opt/getLimitFlow', cookies=self.cookies, headers=self.header)
        status = "文件上传有限制" if r.json()['uploadFlag'] else "文件上传无限制"
        size = r.json()['filesize'] / 1024 ** 3
        print(f'{status},单文件限制{size}GB')

    # 文件预览格式支持，请增加格式化输出以求整齐
    def previewType(self):
        r = requests.get('https://pan-yz.chaoxing.com/preview/supported', cookies=self.cookies, headers=self.header)
        fileFormat = list(r.json())
        print(f"目前共支持{len(fileFormat)}种格式的文件预览，具体如下:")
        flag = 0
        for i in fileFormat:
            flag += 1
            if flag % 10 == 0:
                print(i)
            else:
                print(i, end=' ')

            # 暂时未解决

    # 文件预览，暂时只支持文档
    def preview(self, resid):
        r = requests.get(f'https://pan-yz.chaoxing.com/preview/showpreview_{resid}.html', cookies=self.cookies,
                         headers=self.header)
        try:
            soup = BeautifulSoup(r.text, 'lxml')
            text = soup.find('div', id="main").text
            print(text)
        except:
            pass

    # 文件上传，参数filepath，name，targetFileId
    # upload('超星网盘分析.txt','超星网盘分析.txt','452486350640472064')
    # 旧版网盘也可以考虑开发一个客户端
    def upload(self, filepath, name, folderId):
        files = [{'file', open(f'{filepath}', 'rb')}]
        data = {'folderId': folderId, 'puid': uid, 'id': 'WU_FILE_2', 'name': name}
        p = requests.post('https://pan-yz.chaoxing.com/opt/upload', files=files, data=data, cookies=self.cookies,
                          headers=self.header)
        print(p.status_code, p.json())

    # 文件及文件夹搜索，参数为keyword
    def search(self, kw):
        params = {'kw': kw}
        p = self.post('https://pan-yz.chaoxing.com/opt/search', params)
        for i in p.json()['data']:
            if i['isfile']:
                objectId = i['objectId']
                size = str(round(i['filesize'] / 1024 ** 2, 2)) + 'MB'
                dlink = f'https://d0.ananas.chaoxing.com/download/{objectId}'
                print(i['name'], size, i['id'], dlink)
            else:
                print(i['name'], i['id'])

    # 文件分类，参数type,可选audio，image，video，doc，other
    def getres(self, type):
        params = {'t': type}
        p = self.post('https://pan-yz.chaoxing.com/opt/getres', params)
        for i in p.json()['data']:
            name = i['name']
            size = str(round(i['filesize'] / 1024 ** 2, 2)) + 'MB'
            objectId = i['objectId']
            dlink = f'https://d0.ananas.chaoxing.com/download/{objectId}'
            print(name, size, dlink)

    # 我的分享，包括分享情况及取消分享，还没实现。get是获取分享情况，post是进行分享操作，post的参数没有看到哟
    # http://pan-yz.chaoxing.com/share/myshare
    def myshare(self):
        pass

    # 回收站，同样的，get获取情况，post进行操作，和我的分享一样
    # http://pan-yz.chaoxing.com/recycle
    def recycle(self):
        pass

    # 访客上传，无需登录，200m以下
    def tempUpload(self,filepath):
        files = [('attrFile', open(filepath, 'rb'))]
        r = requests.post('http://notice.chaoxing.com/pc/files/uploadNoticeFile', files=files)
        print(r.json())


if __name__ == '__main__':
    uid = '94649288'
    uf = 'b2d2c93beefa90dc170077f2e681735b4ee92ae0967ae5c75407199b7d24e63fe4face37fdaf4f799b2f97e979079bbbd807a544f7930b6abeaaa6286f1f1754b37ecd2f1b804b880d8a4c92b12beb4be4cd98aa8d0fb2aa9eda0b2d9c60a7c0d00a2326ac07a43e'
    pan = cxpan(uid, uf)
    pan.ls()
    cmd = ''
    while cmd != 'exit':
        cmd = input('请输入需要执行的操作:')
        params = cmd.split(' ')
        if params[0] == 'ls':
            pan.ls(params[1])
        elif params[0] == 'rm':
            pan.rm(params[1])
        elif params[0] == 'mkdir':
            pan.mkdir(params[1], params[2])
        elif params[0] == 'mkroot':
            pan.mkroot(params[1], params[2], params[3])
        elif params[0] == 'md5':
            pan.md5(params[1])
        elif params[0] == 'dl':
            pan.dl(params[1])
        elif params[0] == 'upload':
            pan.upload(params[1], params[2], params[3])
        elif params[0] == 'preview':
            pan.preview(params[1])
        elif params[0] == 'previewType':
            pan.previewType()
        elif params[0] == 'getLimit':
            pan.getLimit()
        elif params[0] == 'rename':
            pan.rename(params[1], params[2])
        elif params[0] == 'mv':
            pan.mv(params[1], params[2])
        elif params[0] == 'share':
            pan.share(params[1], params[2], params[3])
        elif params[0] == 'search':
            pan.search(params[1])
        elif params[0] == 'getres':
            pan.getres(params[1])
        elif cmd == 'h':
            print("""
            帮助信息：
            ls id               参数要列出的文件夹的id
            rm id               参数为要删除的文件或文件夹的id #批量删除功能尚未加入
            mv id target_id     参数为要移动的文件或文件夹id以及要移动到的目标文件夹的id
            rename id name      参数为要重命名的文件或文件夹的id以及新名称
            preview id          参数为要预览的文件的id
            previewType         无参数，查看支持预览的文件格式
            dl ids              参数为要打包下载的文件或文件夹的id，支持下载多个
            share id time type  参数为要分享的文件或文件夹的id、分享的有效期限、分享方式（加密分享或公开分享）
            md5 id              参数为目标文件或文件夹的id
            getLimit            无参数，用于查看单文件上传大小限制
            upload              该功能尚未实现
            """)
