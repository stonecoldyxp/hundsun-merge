#############################################################
#所有的执行都需要在python解析器中执行,推荐安装ipython       #
#pip install ipython                                        #
#每一个功能模块都可以单独执行                               #
#############################################################

######################################################################
#1、对于spel_modi_FieldType.sql  ORDataType.sql 特殊脚本每个用户需要执行，则批量生成
######################################################################
allow_user_str = 'hs_cash:dtcxrac1;hs_user:dtcgrac1;hs_ufx:dtcxrac1;hs_mch:dtcxrac1;hs_auth:dtcxrac1;hs_asset:dtcxrac1;hs_fund:dtcgrac1;hs_ofund:dtcgrac1;hs_secu:dtcgrac1;hs_crdt:dtcgrac1;hs_cbs:dtcxrac1;hs_data:dtjyrac1;hs_arch:dtcxrac1;hs_his:dtjyrac1;hs_sett:dtcxrac1;hs_settinit:dtcxrac1;hs_ref:dtcxrac1;hs_acpt:dtcxrac1;hs_prod:dtcxrac1;hs_opt:dtcxrac1'
dict_use={'dtcxrac1':'hundsun2016','dtcgrac1':'hundsun2016','dtjyrac1':'hundsun2016'}
[print("conn "+x.split(":")[0]+"/"+dict_use[x.split(":")[1]]+"@"+x.split(":")[1]+"\r\n@"+str(pathlib.Path(r"d:\database\01UF20\04证券UF20-BL2013SP3补丁11-20180814-V1\00Init\spel_modi_FieldType.sql"))) for x in allow_user_str.split(";")]

[print("conn "+x.split(":")[0]+"/hundsun@"+x.split(":")[1]+"\r\n@"+str(pathlib.Path(r"d:\database\01uf20\05证券UF20-BL2013SP3补丁2-20180328-V3\00Init\ORDataType.sql"))+"\r\n@"+str(pathlib.Path(r"d:\database\01uf20\05证券UF20-BL2013SP3补丁2-20180328-V3\00Init\spel_modi_FieldType.sql"))) for x in all_user_str.split(";")]
 
######################################################################
#2、检测是否有连接数据库错误的 
######################################################################
import re,pathlib
#文件为合并以后的脚本,可以通过如下程序检查是否有conn中用户与所在库连接不一致的情况
file_name=pathlib.Path(r'D:\database\01uf20\result_01uf20_2018-08-02-new.sql')
#数据库中所有的数据用户以及实例名称
#格式为：'用户1:用户1所在实例;用户2:用户2所在实例;...用户N:用户N所在实例'
all_user_str='hs_cash:dtcxrac1;hs_user:dtcgrac1;hs_ufx:dtcxrac1;hs_mch:dtcxrac1;hs_auth:dtcxrac1;hs_asset:dtcxrac1;hs_fund:dtcgrac1;hs_ofund:dtcgrac1;hs_secu:dtcgrac1;hs_crdt:dtcgrac1;hs_cbs:dtcxrac1;hs_data:dtjyrac1;hs_arch:dtcxrac1;hs_his:dtjyrac1;hs_fil:dtjyrac1;hs_sett:dtcxrac1;hs_settinit:dtcxrac1;hs_ref:dtcxrac1;hs_acpt:dtcxrac1;hs_prod:dtcxrac1;hs_opt:dtcxrac1'
dict_user={ x.split(':')[0]:x.split(':')[1] for x in all_user_str.split(';')}        
with open(file_name,'r') as f:
    line=f.readline()
    while line:
        if re.search('^conn.*',line):
            if dict_user[line.split(' ')[1].split('/')[0]] !=line.split(' ')[1].split('@')[1].strip():
                print(line)
        line=f.readline()
 
######################################################################
#3、以下信息为如何规避xml配置文件中重复的组件 ，适用于so文件，不适用于内存表
#D:\hundsun_sj\01UF20\xml\config_as.xml 为ls或者是as的配置文件
######################################################################
import re
with open(r"C:\Users\stonecold\Desktop\config_ls.xml","r") as f:
    dict_a={}
    a=f.readline()
    while a:
        if re.search("^(<component).*",a.strip()):
            print(a.split('"')[1],a.split('"')[3])
            dict_a[a.split('"')[1]]=a.split('"')[3]
        a=f.readline()
    for k,v in dict_a.items():
        print("<component dll=\""+k+"\"  arg=\""+v+"\" />")
    
######################################################################   
#4、以下信息为检查内存表中是否有重复的内存表信息：
#D:\hundsun_sj\01UF20\xml\hsmdb.xml 为内存表的配置文件
######################################################################
with open(r"D:\hundsun_sj\01UF20\xml\hsmdb.xml","r") as f:
    dict_b={}
    a=f.readline()
    while a:
        if re.search("^(<table).*",a.strip()):
            key =a.split("\"")[1]
            if key in dict_b.keys():
                dict_b[key]=dict_b[key]+1
            else:
                dict_b[key]=1
        a=f.readline()
    for k,v in dict_b.items():
        if v>1:
            print(k)
  
            
######################################################################
#5、检查xml文件加载的so是否存在真实的文件
######################################################################
# D:\test\appcom\appcom中为所有存服务器上下载的so文件
# D:\test\20180727\config_ls.xml 为生产中使用的xml文件
import pathlib
import xml.etree.ElementTree as ET
appcoms=[x.name for x in pathlib.Path(r'D:\test\appcom\appcom').glob('*.so')]
with open(r'D:\test\20180727\config_ls.xml','r') as f:
    txt=f.read()
tree=ET.fromstring(txt)
xml_appcom=['lib'+x.attrib['dll']+'.so' for x in tree.iter('component')]

[x for x in xml_appcom if x not in appcoms]


