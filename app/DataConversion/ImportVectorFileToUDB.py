# -*- coding: gbk -*-
#===================================
#ʸ���ļ�����תSuperMap Udb��ʽ
#ImportVectorFileToUDB.py
#���л���Python2.7.6��Python3.x�汾��������
#===================================

import sys
import os
import time
import getopt
from os.path import walk,join,normpath
import os.path as pth
import logging

class VectorFileToUDB():
    '''����5����
    filePath��ת���ļ�·����udbPath��UDB����Դ·����fileType��ת���ļ����ͣ�
    datasourceName������ת�����������Դ��encodeType��������ݼ�����
    '''
    def __init__(self,filePath,udbPath,fileType,datasourceName,encodeType):
        self.filePath = filePath
        self.udbPath = udbPath
        self.fileType = fileType
        self.datasourceName = datasourceName
        self.encodeType = encodeType
        self.fileList = []
        self.importDataCount = 0  #��¼�ɹ���������ݸ���

    def SearchPath(self):
        #����ļ��б�
        del self.fileList[:]
        #�г���ѡĿ¼�е�ȫ���ļ�
        walk(self.filePath, self.visitFiles, 0)

    def visitFiles(self,arg,dirname,names):
        #��ǰĿ¼�е������ļ��б�
        curFileList = ()
        childFile = []
        for sfile in names:
            files = normpath(join(dirname,sfile))
            fileName = pth.split(files)[1]
            fileEx = pth.splitext(fileName)[1].upper()  # ��ȡ��չ��
            if self.fileType == 'fileSHP' and fileEx == '.shp'.upper():
                childFile.append(files)
            elif self.fileType == 'fileMIF' and fileEx == '.mif'.upper():
                childFile.append(files)
            elif self.fileType == 'fileE00' and fileEx == '.e00'.upper():
                childFile.append(files)
            elif self.fileType == 'fileDWG' and fileEx == '.dwg'.upper():
                childFile.append(files)
            elif self.fileType == 'fileDXF' and fileEx == '.dxf'.upper():
                childFile.append(files)
            elif self.fileType == 'fileGDBVector' and fileEx == '.gdb'.upper():
                childFile.append(files)
            elif self.fileType == 'fileDGN' and fileEx == '.dgn'.upper():
                childFile.append(files)
            elif self.fileType == 'fileTAB' and fileEx == '.tab'.upper():
                childFile.append(files)
            elif self.fileType == 'fileAIBinCov' and fileEx == '.adf'.upper():
                childFile.append(files)
        if childFile:
            curFileList = (dirname,childFile)
            self.fileList.append(curFileList)

    def VectorFile2UDB(self):
        logging.info("��ʼ���������...")
        SuperMap.Init()
        self.SearchPath()
        datasourceAlias = ""
        datasources = {}
        datasetNames = {}
        engineType = 'sceUDB'

        logging.info("��ʼ��������...")
        if len(self.fileList) > 0:
            for parent,files in self.fileList:
                if "None" == self.datasourceName:
                    L = parent.split("\\")
                    datasourceAlias = L[len(L) - 1]
                else:
                    datasourceAlias = self.datasourceName
                #��������Դ
                if not datasources.has_key(datasourceAlias):
                    if SuperMap.OpenDataSource(self.udbPath + '\\' + datasourceAlias + '.udb',"","",engineType,datasourceAlias) == 0:
                        isCreate = SuperMap.CreateDataSource(self.udbPath + "\\" + datasourceAlias,"","",engineType,datasourceAlias)
                        if isCreate == 1:
                            logging.info("��������Դ��[" + self.udbPath + '\\' + datasourceAlias + '.udb ' + "]�ɹ���")
                        else:
                            logging.error("��������Դ��[" + self.udbPath + '\\' + datasourceAlias + '.udb ' + "]ʧ�ܡ�")
                            SuperMap.Exit()
                            return
                    datasources[datasourceAlias] = datasourceAlias
                else:
                    SuperMap.CloseDataSource(datasourceAlias)
                    if SuperMap.OpenDataSource(self.udbPath + '\\' + datasourceAlias + '.udb',"","",engineType,datasourceAlias) == 0:
                        logging.info("������Դ��[" + datasourceAlias + "]ʧ�ܡ�")
                        SuperMap.Exit()
                        return
                #��¼��ǰ�ļ��Ƿ���ɹ�
                result = 0
                #����shp����
                for file in files:
                    fileName = pth.split(file)[1]
                    fileName = pth.splitext(fileName)[0]  # ��ȡ������չ�����ļ���
                    logging.info("��ʼ�������ݣ�[" + file + "]...")
                    isImport = SuperMap.ImportVectorFile(datasourceAlias,fileName, self.encodeType,self.fileType, file, "GIS")
                    if isImport == 1:
                        logging.info("�������ݣ�[" + file + "]������Դ��[" + datasourceAlias + "]�ɹ���")
                        self.importDataCount += 1
                    else:
                        logging.info("�������ݣ�[" + file + "]������Դ��[" + datasourceAlias + "]ʧ�ܡ�")
                SuperMap.CloseDataSource(datasourceAlias)
        logging.info("���������ɡ�")
        logging.info("���� " + str(self.importDataCount) + "�����ݱ��ɹ�����ΪUdb��ʽ��")
        SuperMap.Exit()

#---------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        '''������7��������0���ű��ļ�·����1��SuperMap Python���·����2��ת���ļ�·��
        3��UDB�ļ�·����4��ת���ļ����ͣ�5������Դ����(None����Դ���ļ�����������)��6��ѹ����������'''
        if (len(sys.argv) == 7):
            sys.path.append(sys.argv[1])  #��.net�����·����ӵ���������
            import smu as SuperMap        #����SuperMapģ��
            logPath = sys.argv[3] + r'\ʸ������ת��.log'         #��־�ļ�·��Ϊ����Դ���·��
            #������־�ļ�·��������������ʽ
            logging.basicConfig(filename=logPath,level=logging.DEBUG,format='%(asctime)s %(levelname)-8s %(message)s')
            logging.basicConfig(filename=logPath,level=logging.DEBUG,format='%(asctime)s %(levelname)-8s %(message)s')
            #����һ��StreamHandler����INFO�������ߵ���־��Ϣ��ӡ����׼���󣬲�������ӵ���ǰ����־�������
            #����ͬʱ�����־��Ϣ���ı��ļ��Ϳ���̨����C#�����е��õ�ʱ����Ի�ȡ������̨�������
            console = logging.StreamHandler(sys.stdout)
            console.setLevel(logging.INFO)
            #��־��Ϣ���ż�info:��Ϊ�˺�SuperMap����������־��Ϣ����
            console.setFormatter(logging.Formatter('info:' '%(message)s'))
            logging.getLogger('').addHandler(console)
            objImport = VectorFileToUDB(sys.argv[2],sys.argv[3] ,sys.argv[4],sys.argv[5],sys.argv[6])
            objImport.VectorFile2UDB()
        else:
            print "ִ�нű�ʧ�ܣ��ű���������ȷ��"
    except Exception,ex:
        print "ִ�нű�ʧ��:" + ex.message
        sys.exit(2)
    #=========================================���Դ���===============================================
    #��������Դ���ļ�����
    #objImport = VectorFileToUDB(r"E:\Data\����ת����������\SHP",r"E:\Data\����ת����������\SHP" ,"fileSHP","None","encNONE")
    #logPath = r'E:\Data\����ת����������\SHP\log.log'
    #logging.basicConfig(filename=logPath,level=logging.DEBUG,format='%(asctime)s %(levelname)-8s %(message)s')
    ##����һ��Handler��ӡINFO�����ϼ������־��sys.stdout
    ##����ͬʱ�����־��Ϣ���ı��ļ��Ϳ���̨����C#�����е��õ�ʱ����Ի�ȡ������̨�������
    #console = logging.StreamHandler(sys.stdout)
    #console.setLevel(logging.INFO)
    ##��־��Ϣ���ż�info:��Ϊ�˺�SuperMap����������־��Ϣ����
    #console.setFormatter(logging.Formatter('info:' '%(message)s'))
    #logging.getLogger('').addHandler(console)
    #sys.path.append(r"E:\CodeSource\sgs_src\DataManager7.0\D-Process\Bin")  #��.net�����·����ӵ���������
    #import smu as SuperMap #����SuperMapģ��
    #objImport.VectorFileToUDB()
    #=========================================���Դ���===============================================
