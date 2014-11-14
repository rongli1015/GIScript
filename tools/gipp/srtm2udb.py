# -*- coding: gbk -*-
#===================================
#ʸ���ļ�����תsmu Udb��ʽ
#ImportRasterFileToUDB.py
#���л���Python2.7.6��Python3.x�汾��������
#===================================

import sys
import os
import time
import datetime
import getopt
from os.path import walk,join,normpath
import os.path as pth
import logging

class RasterFileToUDB():
    '''����10����filePath��ת���ļ�·����udbPath��UDB�ļ�·����fileType��ת���ļ����ͣ�datasoruceName������Դ����(None����Դ���ļ�����������)��
    datasetName�����ݼ����ƣ�isGrid�����ݼ�����(0ΪӰ��1Ϊդ��)��encodeType��ѹ���������ͣ�
    isBuildPyramid���Ƿ񴴽�Ӱ���������isSplicing���Ƿ�ƴ��Ӱ��pixelFormat�����ظ�ʽ'''
    def __init__(self,filePath,udbPath,fileType,datasoruceName,datasetName,isGrid,encodeType,isBuildPyramid,isSplicing,pixelFormat):
	#self.uds = smEngine.uds(udbpath, u'smlib_worldpy')
        self.filePath = filePath
        self.udbPath = udbPath
        self.fileType = fileType
        self.datasourceName = datasoruceName
        self.datasetName = datasetName
        self.isGrid = int(isGrid)
        self.encodeType = encodeType
        self.isBuildPyramid = int(isBuildPyramid)
        self.isSplicing = int(isSplicing)
        self.pixelFormat = pixelFormat
        self.fileList = []
        self.importDataCount = 0    #��¼�ɹ���������ݸ���

    def ToUDB(self):
        logging.info(u"��ʼ���������...")

        self.SearchPath()
        if self.isSplicing:
            self.RasterToUDBAndMerge()
        else:
            self.RasterToUDB()

    def SearchPath(self):
        #����ļ��б�
        del self.fileList[:]
        #�г���ѡĿ¼�е�ȫ���ļ�
        path = self.filePath
        walk(path, self.visitFiles, 0)

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
            
    def RasterToUDB(self):
        datasourceAlias = ""
        datasources = {}
        datasetNames = {}
        engineType = 'sceUDB'
        if len(self.fileList) > 0:
            for parent,files in self.fileList:
                if "None" == self.datasourceName:
                    L = parent.split("\\")
                    datasourceAlias = L[len(L) - 1]
                else:
                    datasourceAlias = self.datasourceName
                #��������Դ
                if not datasources.has_key(datasourceAlias):
                    if smu.OpenDataSource(self.udbPath + '\\' + datasourceAlias + '.udb',"","",engineType,datasourceAlias) == 0:
                        if smu.CreateDataSource(self.udbPath + "\\" + datasourceAlias,"","",engineType,datasourceAlias):
                            logging.info(u"��������Դ��[" + self.udbPath + '\\' + datasourceAlias + u'.udb ' + u"]�ɹ���")
                        else:
                            logging.error(u"��������Դ��[" + self.udbPath + '\\' + datasourceAlias + u'.udb ' + u"]ʧ�ܡ�")
                            smu.Exit()
                            return
                    datasources[datasourceAlias] = datasourceAlias
                else:
                    smu.CloseDataSource(datasourceAlias)
                    if smu.OpenDataSource(self.udbPath + '\\' + datasourceAlias + '.udb',"","",engineType,datasourceAlias) == 0:
                        logging.error(u"������Դ��[" + datasourceAlias + u"]ʧ�ܡ�")
                        smu.Exit()
                        return
    
                for rasterFile in files:
                    datasetName = pth.split(rasterFile)[1]
                    datasetName = pth.splitext(datasetName)[0]  # ��ȡ������չ�����ļ���
                    #smu���ݼ������в��ܳ���'.'��'-',ϵͳ��ִ�е������ʱ���Զ���'.'�滻Ϊ�»���'_'
                    datasetName = datasetName.replace('.', '_')
                    datasetName = datasetName.replace('-', '_')
                    logging.info(u"��ʼ�������ݣ�[" + rasterFile + "]...")
                    if smu.ImportRasterFile(datasourceAlias,datasetName,self.encodeType,self.fileType,rasterFile,self.isGrid):
                        logging.info(u"�������ݣ�[" + rasterFile + u"]������Դ��[" + datasourceAlias + u"]�ɹ���")
                        self.importDataCount += 1
                    else:
                        logging.error(u"�������ݣ�[" + rasterFile + u"]������Դ��[" + datasourceAlias + u"]ʧ�ܡ�")
                #����Ӱ�������
                if self.isBuildPyramid:
                    datasetCount = smu.GetDatasetCount(datasourceAlias)
                    for datasetIndex in range(datasetCount):
                        datasetName = smu.GetDatasetName(datasourceAlias,datasetIndex)
                        logging.info(u'���ݼ�' + datasetName + u'��ʼ����Ӱ�������...')
                        if smu.BuildPyramid(datasourceAlias,datasetName):
                            logging.info(u"����Դ��[" + datasourceAlias + u"] ���ݼ���[" + datasetName + u"]����Ӱ��������ɹ���")
                        else:
                            logging.error(u"����Դ��[" + datasourceAlias + u"] ���ݼ���[" + datasetName + u"]����Ӱ�������ʧ�ܡ�")
                #�ر�����Դ
                smu.CloseDataSource(datasourceAlias)
        logging.info(u"���������ɡ�")
        logging.info(u"���� " + str(self.importDataCount) + u" �����ݱ��ɹ�����ΪUDB��ʽ��")
        smu.Exit()
        
    def RasterToUDBAndMerge(self):
        engineType = 'sceUDB'
        L = []
        left = []
        top = []
        right = []
        bottom = []
        ratiox = []
        ratioy = []
        if len(self.fileList) > 0:
            for parent,files in self.fileList:
                for rasterFile in files:
                    L = smu.GetImageGeoRef(self.fileType,unicode(rasterFile, "ascii"))
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
            
            datasourceAlias = self.datasourceName
	    
	    uPath = self.udbPath +  datasourceAlias + u'.udb'
	    print u"UDB: "+ uPath
            if smu.OpenDataSource(uPath,u"",u"",unicode(engineType, "ascii"),datasourceAlias) == 0:
		print u"Create UDB: "
		#print r'Create Datasource: ' + datasourceAlias
                #if smu.CreateDataSource(unicode(self.udbPath + u"/" + datasourceAlias, "ascii"),"","",
		#		unicode(engineType, "ascii"),unicode(datasourceAlias, "ascii")):
                #    logging.info(u"Create Datasource [" + self.udbPath + '/' + datasourceAlias + u'.udb ' + u"] Success!")
                #else:
                #    logging.error(u"Create Datasource [" + self.udbPath + '/' + datasourceAlias + u'.udb ' + u"] Failed!")
                #    smu.Exit()
                #    return
	    else:
		print u"Datasource Exist."

            #ʹ������ɼ�������Ϣ����DEM��Grid���ݼ�,���һ��������־���ݼ�Ϊѹ��ģʽ
            datasetType = u"Grid" if self.isGrid == '0' else "Image"
	    print u"Create Dataset: "+self.datasetName
            if smu.CreateDatasetRaster(datasourceAlias,self.datasetName,unicode(datasetType,"ascii"),self.encodeType,
				self.pixelFormat,nWidth,nHeight,dLeft,dTop,dRight,dBottom,256):
                logging.info(u"�������ݼ���[" + self.datasetName + u"]�ɹ���")
            else:
                logging.error(u"�������ݼ���[" + self.datasetName + u"]ʧ�ܡ�")
                smu.Exit()
                return

            #ѭ��׷���ļ�
            for parent,files in self.fileList:
                for rasterFile in files:
                    logging.info(u"��ʼ�������ݣ�" + rasterFile + " ...")
                    if smu.AppendRasterFile(datasourceAlias,self.datasetName,self.fileType,unicode(rasterFile,"ascii")):
                        logging.info(u"�������ݣ�[" + rasterFile + u"] ������Դ��[" + datasourceAlias + u"]�ɹ���")
                        self.importDataCount += 1
                    else:
                        logging.error(u"�������ݣ�[" + rasterFile + u"] ������Դ��[" + datasourceAlias + u"]ʧ�ܡ�")
            ##���²�����������ClipRegion�� ���ֽӿ������⣬����ʹ��
            #rgnDtName = "Rgn"
            #logging.info("�������ݣ�[" + rasterFile + "] ������Դ��[" + datasourceAlias + "]�ɹ���")
            #smu.CreateDatasetVector(datasourceAlias,rgnDtName,"Region","encDWORD")
            #for parent,files in self.fileList:
            #    for tifile in files:
            #        smu.MakeBoundsRgn(tifile,fileType,datasourceAlias,rgnDtName)
            #nID = smu.UnionRgnDt(datasourceAlias,rgnDtName)

            ##����ClipRegion
            #if smu.SetClipRegion(datasourceAlias,self.datasetName,datasourceAlias,rgnDtName,nID):
            #    logging.info("ΪӰ�����ݼ�" + self.datasetName + "���òü�����ɹ���")
            #else:
            #    logging.info("ΪӰ�����ݼ�" + self.datasetName + "���òü�����ʧ�ܡ�")

            #����Ӱ�������
            if self.isBuildPyramid:
                logging.info(u'��ʼ����Ӱ�������...')
                if smu.BuildPyramid(datasourceAlias,self.datasetName):
                    logging.info(u"����Դ��[" + datasourceAlias + u"] ���ݼ���[" + self.datasetName + u"]����Ӱ��������ɹ���")
                else:
                    logging.error(u"����Դ��[" + datasourceAlias + u"] ���ݼ���[" + self.datasetName + u"]����Ӱ�������ʧ�ܡ�")
            #�ر�����Դ
            smu.CloseDataSource(datasourceAlias)
        logging.info(u"���������ɡ�")
        logging.info(u"���� " + str(self.importDataCount) + u" �����ݱ��ɹ�����ΪUDB��ʽ��")
        smu.Exit()

#---------------------------------------------------------------------------
# ��ʼ�� pylib ����
def initSMLib():
	""" Initialize GIScript Environment,Load Library.
	"""
	smlib_path=os.path.dirname(sys.path[0]+"/../../lib_python/smlib/")
	print "Set Library Path: ugc,smlib,smu.so"	
	print "smlib: ", smlib_path
	sys.path.append(smlib_path)

if __name__ == '__main__':
      	print "Import SRTM to UDB."
	reload(sys)
	sys.setdefaultencoding("utf-8")
	
	initSMLib()
	import smlib
	smlib.load_smlib()
	import smEngine
	
	import smu
        #objImport = RasterFileToUDB(r'E:\Data\����ת����������\tif',r'E:\Data\����ת����������\tif','fileTIF','դ�����','Image',
        #                            '0','encDCT','1','1','IPF_RGB')
        #sys.path.append("E:\CodeSource\sgs_src\DataManager7.0\D-Process\Bin")  #��.net�����·�����ӵ���������
        #import smu as SuperMap        #����SuperMapģ��
        #logPath = r'E:\Data\����ת����������\tif\դ������ת��.log'         #��־�ļ�·��Ϊ����Դ���·��
        ##������־�ļ�·��������������ʽ
        #logging.basicConfig(filename=logPath,level=logging.DEBUG,format='%(asctime)s %(levelname)-8s %(message)s')
        ##����һ��StreamHandler����INFO�������ߵ���־��Ϣ��ӡ����׼���󣬲��������ӵ���ǰ����־��������
        ##����ͬʱ�����־��Ϣ���ı��ļ��Ϳ���̨����C#�����е��õ�ʱ����Ի�ȡ������̨�������
        #console = logging.StreamHandler(sys.stdout)
        #console.setLevel(logging.INFO)
        ##��־��Ϣ��ͷ��info:��Ϊ�˺�SuperMap����������־��Ϣ����
        #console.setFormatter(logging.Formatter('info:' '%(message)s'))
        #logging.getLogger('').addHandler(console)
        #objImport.ToUDB()
        #=========================================���Դ���===============================================
	curtime = datetime.datetime.now()
	strcurtime = curtime.strftime("%Y-%m-%d %H:%M:%S") 
	print strcurtime+"-Begin."
	
	objImport = RasterFileToUDB(r'/media/supermap/GeoImage/test',
				r'/media/supermap/GeoImage/test/',u'fileTIF',u'SRTM',u'Image',
                                    u'0',u'encDCT',u'1',u'1',u'IPF_RGB')
	objImport.ToUDB()

	#L = smu.GetImageGeoRef(u'fileTIF',u'/media/supermap/GeoImage/test/N-02-15.tif')
	#print L
	curtime = datetime.datetime.now()
	strcurtime = curtime.strftime("%Y-%m-%d %H:%M:%S")         
	print strcurtime+"-Finished."
 
    
  

