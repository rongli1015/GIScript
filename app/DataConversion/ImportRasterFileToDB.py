# -*- coding: gbk -*-
#===================================
#դ���ļ��������
#ImportRasterFileToDB.py
#���л���Python2.7.6��Python3.x�汾��������
#===================================

import sys
import os
import time
import getopt
from os.path import walk,join,normpath
import os.path as pth
import logging
import re

class RasterFileToDB():
    '''����14����filePath��ת���ļ�·����isRasterFile����դ���ļ�·�����Ǵ��ı���ȡ�ļ�(1դ���ļ���0���ı���ȡ)��
    fileType��ת���ļ����ͣ�engineType����������(sceOraclePlus,sceSQLPlus,sceOracleSpatial,sceDB2,sceSybasePlus,sceKingBase)��
    dbServer��ʵ����(SQLServer���ݿ������)��dbName�����ݿ�����(Oracle�����ֵ)��dbUser���û�����dbPassword�����룻
    datasetName�����ݼ����ƣ�isGrid�����ݼ�����(0ΪӰ��1Ϊդ��)��encodeType��ѹ���������ͣ�
    isBuildPyramid���Ƿ񴴽�Ӱ���������isSplicing���Ƿ�ƴ��Ӱ��pixelFormat�����ظ�ʽ'''
    def __init__(self,filePath,isRasterFile,fileType,engineType,dbServer,dbName,dbUser,dbPassword,
                 datasetName,isGrid,encodeType,isBuildPyramid,isSplicing,pixelFormat):
        self.filePath = filePath
        self.isRasterFile = int(isRasterFile)
        self.fileType = fileType
        self.engineType = engineType
        self.dbServer = dbServer
        self.dbName = dbName
        self.dbUser = dbUser
        self.dbPassword = dbPassword
        self.datasetName = datasetName
        self.isGrid = int(isGrid)
        self.encodeType = encodeType
        self.isBuildPyramid = int(isBuildPyramid)
        self.isSplicing = int(isSplicing)
        self.pixelFormat = pixelFormat
        self.fileList = []
        self.importDataCount = 0    #��¼�ɹ���������ݸ���

    def ToDB(self):
        logging.info("��ʼ���������...")
        SuperMap.Init()
        self.SearchPath()
        if self.isSplicing:
            self.RasterToDBAndMerge()
        else:
            self.RasterToDB()

    def SearchPath(self):
        #����ļ��б�
        del self.fileList[:]
        #�г���ѡĿ¼�е�ȫ���ļ�
        path = self.filePath
        if self.isRasterFile:
            walk(path, self.visitFiles, 0)
        else:
            ReadPathFromText(path)

    def visitFiles(self,arg,dirname,names):
        #��ǰĿ¼�е������ļ��б�
        curFileList = ()
        childFile = []
        for sfile in names:
            files = normpath(join(dirname,sfile))
            fileName = pth.split(files)[1]
            fileEx = pth.splitext(fileName)[1].upper()  # ��ȡ��չ��
            if self.fileType == 'fileTIF' and (fileEx == '.tif'.upper() or fileEx == '.tiff'.upper()):
                childFile.append(files)
            elif self.fileType == 'fileIMG' and fileEx == '.img'.upper():
                childFile.append(files)
            elif self.fileType == 'fileArcInfoGrid' and fileEx == '.grd'.upper():
                childFile.append(files)
            elif self.fileType == 'fileSIT' and fileEx == '.sit'.upper():
                childFile.append(files)
            elif self.fileType == 'fileGDBRaster' and fileEx == '.gdb'.upper():
                childFile.append(files)
            elif self.fileType == 'fileBMP' and fileEx == '.bmp'.upper():
                childFile.append(files)
            elif self.fileType == 'fileJPG' and fileEx == '.jpg'.upper():
                childFile.append(files)
            elif self.fileType == 'fileRAW' and fileEx == '.raw'.upper():
                childFile.append(files)
        if childFile:
            curFileList = (dirname,childFile)
            self.fileList.append(curFileList)

    def ReadPathFromText(self,path):
            f = open(path,"r")
            demfiles = f.readlines()
            f.close()
            #��ǰĿ¼�е������ļ��б�
            curFileList = ()
            childFile = []
            if len(demfiles) > 0:
                for file in demfiles:
                    childFile.append(file[:-1])
                curFileList = ("",childFile)
                self.fileList.append(curFileList)
        
    def ProcessDtName(self,dtName):
        '''
        ����ֶ����Ƶ��ַ�����Ϊ��ĸ�����֡����ֺ��»��ߣ��ֶ����Ʋ����������ֺ��»��߿�ͷ�������
        ��ĸ��ͷ��Ҳ��������sm�����ݼ�������Ŀǰʵ������������30���ַ���
        '''
        if len(dtName) > 30:
            dtName = dtName[:30]
        if dtName[:2].upper() == "SM":
            dtName = "T" + dtName
        dtName = re.sub(ur"^[^a-zA-Z\u4E00-\u9FFFF]", ur"T" + dtName[0], dtName)
        return re.sub(ur"[^\w\u4E00-\u9FFFF]", ur"_", dtName)
            
    def RasterToDB(self):
        if len(self.fileList) > 0: 
            datasourceAlias = self.dbUser
            if SuperMap.OpenDataSource(self.dbServer,self.dbUser,self.dbPassword,self.engineType,datasourceAlias,self.dbName) == 0:
                if SuperMap.CreateDataSource(self.dbServer,self.dbUser,self.dbPassword,self.engineType,datasourceAlias):
                    logging.info("��������Դ��[" + datasourceAlias + "]�ɹ���")
                else:
                    logging.error("�򿪻򴴽�����Դ��[" + datasourceAlias + "]ʧ�ܡ�")
                    SuperMap.Exit()
                    return
            for parent,files in self.fileList:
                for rasterFile in files:
                    datasetName = pth.split(rasterFile)[1]
                    datasetName = pth.splitext(datasetName)[0]  # ��ȡ������չ�����ļ���
                    datasetName = self.ProcessDtName(datasetName)
                    logging.info("��ʼ�������ݣ�[" + rasterFile + "]...")
                    if SuperMap.ImportRasterFile(datasourceAlias,datasetName,self.encodeType,self.fileType,rasterFile,self.isGrid):
                        logging.info("�������ݣ�[" + rasterFile + "]������Դ��[" + datasourceAlias + "]�ɹ���")
                        self.importDataCount += 1
                    else:
                        logging.error("�������ݣ�[" + rasterFile + "]������Դ��[" + datasourceAlias + "]ʧ�ܡ�")
            #����Ӱ�������
            if self.isBuildPyramid:
                datasetCount = SuperMap.GetDatasetCount(datasourceAlias)
                for datasetIndex in range(datasetCount):
                    datasetName = SuperMap.GetDatasetName(datasourceAlias,datasetIndex)
                    logging.info('���ݼ�' + datasetName + '��ʼ����Ӱ�������...')
                    if SuperMap.BuildPyramid(datasourceAlias,datasetName):
                        logging.info("����Դ��[" + datasourceAlias + "] ���ݼ���[" + datasetName + "]����Ӱ��������ɹ���")
                    else:
                        logging.error("����Դ��[" + datasourceAlias + "] ���ݼ���[" + datasetName + "]����Ӱ�������ʧ�ܡ�")
            #�ر�����Դ
            SuperMap.CloseDataSource(datasourceAlias)
        logging.info("���������ɡ�")
        logging.info("���� " + str(self.importDataCount) + " �����ݱ��ɹ�����ΪUDB��ʽ��")
        SuperMap.Exit()
        
    def RasterToDBAndMerge(self):
        L = []
        left = []
        top = []
        right = []
        bottom = []
        ratiox = []
        ratioy = []
        if len(self.fileList) > 0:
            datasourceAlias = self.dbUser
            if SuperMap.OpenDataSource(self.dbServer,self.dbUser,self.dbPassword,self.engineType,datasourceAlias,self.dbName) == 0:
                if SuperMap.CreateDataSource(self.dbServer,self.dbUser,self.dbPassword,self.engineType,datasourceAlias):
                    logging.info("��������Դ��[" + datasourceAlias + "]�ɹ���")
                else:
                    logging.error("�򿪻򴴽�����Դ��[" + datasourceAlias + "]ʧ�ܡ�")
                    SuperMap.Exit()
                    return
            for parent,files in self.fileList:
                for rasterFile in files:
                    L = SuperMap.GetImageGeoRef(self.fileType,rasterFile)
                    l = float(L[0][0])
                    t = float(L[0][1])
                    r = float(L[0][2])
                    b = float(L[0][3])
                    w = int(L[1][0])
                    h = int(L[1][1])
                    x = (r - l) / w
                    y = (t - b) / h

                    left.append(l)
                    top.append(t)
                    right.append(r)
                    bottom.append(b)
                    ratiox.append(x)
                    ratioy.append(y)
                
            #���Bounds
            dLeft = min(left)
            dRight = max(right)
            dTop = max(top)
            dBottom = min(bottom)
            
            #����ֱ���
            dRatioX = min(ratiox)
            dRatioY = min(ratioy)
            
            #�������
            nWidth = int((dRight - dLeft) / dRatioX)
            nHeight = int((dTop - dBottom) / dRatioY)
            
            #����Right��Bottom���Ա�֤�ֱ��ʵ���ȷ��
            dRight = dLeft + dRatioX * nWidth
            dBottom = dTop - dRatioY * nHeight
            
            if SuperMap.OpenDataSource(self.dbServer,self.dbUser,self.dbPassword,self.engineType,datasourceAlias,self.dbName) == 0:
                if SuperMap.CreateDataSource(self.dbServer,self.dbUser,self.dbPassword,self.engineType,datasourceAlias):
                    logging.info("��������Դ��[" + datasourceAlias + "]�ɹ���")
                else:
                    logging.error("��������Դ��[" + datasourceAlias + "]ʧ�ܡ�")
                    SuperMap.Exit()
                    return
            #ʹ������ɼ�������Ϣ����DEM��Grid���ݼ�,���һ��������־���ݼ�Ϊѹ��ģʽ
            datasetType = "Grid" if self.isGrid == '0' else "Image"
            if SuperMap.CreateDatasetRaster(datasourceAlias,self.datasetName,datasetType,self.encodeType,self.pixelFormat,nWidth,nHeight,dLeft,dTop,dRight,dBottom,256):
                logging.info("�������ݼ���[" + self.datasetName + "]�ɹ���")
            else:
                logging.error("�������ݼ���[" + self.datasetName + "]ʧ�ܡ�")
                SuperMap.Exit()
                return
            #ѭ��׷���ļ�
            for parent,files in self.fileList:
                for rasterFile in files:
                    logging.info("��ʼ�������ݣ�" + rasterFile + " ...")
                    if SuperMap.AppendRasterFile(datasourceAlias,self.datasetName,self.fileType,rasterFile):
                        logging.info("�������ݣ�[" + rasterFile + "] ������Դ��[" + datasourceAlias + "]�ɹ���")
                        self.importDataCount += 1
                    else:
                        logging.error("�������ݣ�[" + rasterFile + "] ������Դ��[" + datasourceAlias + "]ʧ�ܡ�")
            ##���²�����������ClipRegion, �ײ㲿�ֽӿ�������
            #rgnDtName = "Rgn"
            #SuperMap. CreateDatasetVector(datasourceAlias,rgnDtName,"Region","encNONE")
            #for parent,files in self.fileList:
            #    for tifile in files:
            #        SuperMap.MakeBoundsRgn(tifile,fileType,datasourceAlias,rgnDtName)
            #nID = SuperMap.UnionRgnDt(datasourceAlias,rgnDtName)

            ##����ClipRegion
            #if SuperMap.SetClipRegion(datasourceAlias,self.datasetName,datasourceAlias,rgnDtName,nID):
            #    logging.info("ΪӰ�����ݼ�" + self.datasetName + "���òü�����ɹ���")
            #else:
            #    logging.info("ΪӰ�����ݼ�" + self.datasetName + "���òü�����ʧ�ܡ�")

            #����Ӱ�������
            if self.isBuildPyramid:
                logging.info('��ʼ����Ӱ�������...')
                if SuperMap.BuildPyramid(datasourceAlias,self.datasetName):
                    logging.info("����Դ��[" + datasourceAlias + "] ���ݼ���[" + self.datasetName + "]����Ӱ��������ɹ���")
                else:
                    logging.error("����Դ��[" + datasourceAlias + "] ���ݼ���[" + self.datasetName + "]����Ӱ�������ʧ�ܡ�")
            #�ر�����Դ
            SuperMap.CloseDataSource(datasourceAlias)
        logging.info("���������ɡ�")
        logging.info("���� " + str(self.importDataCount) + " �����ݱ��ɹ�����ΪUDB��ʽ��")
        SuperMap.Exit()

#---------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        '''������16��������0���ű��ļ�·����1��SuperMapPython���·����2��ת���ļ�·����3����դ���ļ�·�����Ǵ��ı���ȡ�ļ�(1դ���ļ���0���ı���ȡ)��
        4��ת���ļ����ͣ�5����������(sceOraclePlus,sceSQLPlus,sceOracleSpatial,sceDB2,sceSybasePlus,sceKingBase)��
        6��ʵ����(SQLServer���ݿ������)��7�����ݿ�����(Oracle�����ֵ)��8���û�����9�����룻
        10�����ݼ����ƣ�11�����ݼ�����(0ΪӰ��1Ϊդ��)��12��ѹ���������ͣ�
        13���Ƿ񴴽�Ӱ������� 14���Ƿ�ƴ��Ӱ�� 15�����ظ�ʽ'''
        if (len(sys.argv) == 16):
            sys.path.append(sys.argv[1])  #��.net�����·����ӵ���������
            import smu as SuperMap        #����SuperMapģ��
            logPath = sys.argv[2] + r'\դ������ת��.log'         #��־�ļ�·��Ϊ����Դ���·��
            #������־�ļ�·��������������ʽ
            logging.basicConfig(filename=logPath,level=logging.DEBUG,format='%(asctime)s %(levelname)-8s %(message)s')
            #����һ��StreamHandler����INFO�������ߵ���־��Ϣ��ӡ����׼���󣬲�������ӵ���ǰ����־�������
            #����ͬʱ�����־��Ϣ���ı��ļ��Ϳ���̨����C#�����е��õ�ʱ����Ի�ȡ������̨�������
            console = logging.StreamHandler(sys.stdout)
            console.setLevel(logging.INFO)
            #��־��Ϣ��ͷ��info:��Ϊ�˺�SuperMap����������־��Ϣ����
            console.setFormatter(logging.Formatter('info:' '%(message)s'))
            logging.getLogger('').addHandler(console)
            objImport = RasterFileToDB(sys.argv[2],sys.argv[3] ,sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7],sys.argv[8],
                                        sys.argv[9],sys.argv[10],sys.argv[11],sys.argv[12],sys.argv[13],sys.argv[14],sys.argv[15])
            objImport.ToDB()
        else:
            print "ִ�нű�ʧ�ܣ��ű���������ȷ��"

        ##=========================================���Դ���===============================================
        #objImport = RasterFileToDB(r'E:\Data\����ת����������\tif','1','fileTIF','sceOraclePlus','172.16.10.60','smTest',
        #                            'smTest','sagis','Image','0','encDCT','1','1','IPF_RGB')
        #sys.path.append("E:\CodeSource\sgs_src\DataManager7.0\D-Process\Bin")  #��.net�����·����ӵ���������
        #import smu as SuperMap        #����SuperMapģ��
        #logPath = r'E:\Data\����ת����������\tif\դ������ת��.log'         #��־�ļ�·��Ϊ����Դ���·��
        ##������־�ļ�·��������������ʽ
        #logging.basicConfig(filename=logPath,level=logging.DEBUG,format='%(asctime)s %(levelname)-8s %(message)s')
        ##����һ��StreamHandler����INFO�������ߵ���־��Ϣ��ӡ����׼���󣬲�������ӵ���ǰ����־�������
        ##����ͬʱ�����־��Ϣ���ı��ļ��Ϳ���̨����C#�����е��õ�ʱ����Ի�ȡ������̨�������
        #console = logging.StreamHandler(sys.stdout)
        #console.setLevel(logging.INFO)
        ##��־��Ϣ��ͷ��info:��Ϊ�˺�SuperMap����������־��Ϣ����
        #console.setFormatter(logging.Formatter('info:' '%(message)s'))
        #logging.getLogger('').addHandler(console)
        #objImport.ToDB()
        ##=========================================���Դ���===============================================
    except Exception,ex:
        print "ִ�нű�ʧ��:" + ex.message
        sys.exit(2)