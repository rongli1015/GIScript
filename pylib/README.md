

һ��Ŀ¼�ṹ

   ---- pyLib 			����SuperMap Python�ӿڵ�Python Objects
   |	-- smBase.py		�����࣬�ṩһЩ������ͻ�������
   |	-- smData.py		�ռ�����������࣬�ṩ������Դ�����ݼ�����ز���
   |	-- smEngine.py		�ռ������������ͷ�װ


����lib ��������
   1���� lib �ļ������ض�Ӧƽ̨��ѹ��������ѹ��
   2������ѹ��� smy.pyd ����·�����õ�Python��������
      ����������ӿ�ʹ�����·�����һ�֣�
	1����·�����뵽PYTHONPATH���������У�
	2����·�����뵽Python��װĿ¼�º�׺��Ϊ.pth���ļ��У�һ��һ��·�������û�к�׺��Ϊ.pth���ļ������½������ɣ�
	3��Python�ű���ָ�� sys.path.append()

����SuperMap Python �� Unicode ��֧��
    ���� Python �ű���ָ��Ĭ���ַ���Ϊutf-8���������£�
    ......
	reload(sys)
    sys.setdefaultencoding("utf-8")
	......

    �ɲμ� pyLib\test\AppendRasterFile.py

�ġ�ע������
    �� 7.1 �汾�����UDBդ�������ھɰ汾���޷�������


