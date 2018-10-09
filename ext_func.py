#升级文件进行排序【升级前执行，对原始包进行排序，重命名】
import pathlib ,re,datetime
import pandas as pd
import numpy as np
uf20path=r'E:\2018年工作内容\系统升级\20180914\提取包\01UF20'

dirname = pathlib.Path(uf20path)

subname = [x for x in dirname.iterdir() ]
#subname = [x for x in dirname.rglob('*.rar') ]

rar_name=[x.name for x in subname]

df=pd.DataFrame({'source_name':subname,'rar_name':rar_name})
#BL2012SP5Pack5
df['bl']=df['rar_name'].str.extract('(BL((\d){4}))',flags=re.IGNORECASE,expand=True)[1]
df.loc[df.bl.isna(),'bl']='00'
df.bl=df.bl.str.zfill(4)
df['SP']=df['rar_name'].str.extract('(SP((\d)+))',flags=re.IGNORECASE,expand=True)[1]
df.loc[df.SP.isna(),'SP']='00'
df.SP=df.SP.str.zfill(4)
df['Pack']=df['rar_name'].str.extract('(Pack((\d)+))',flags=re.IGNORECASE,expand=True)[1]
df.loc[df.Pack.isna(),'Pack']='00'
df.Pack=df.Pack.str.zfill(4)
df['patch_order']=df['rar_name'].str.extract('(补丁((\d){1,3})(增值)?)',flags=re.IGNORECASE,expand=True)[1]
df.loc[df.patch_order.isna(),'patch_order']='00'
df.patch_order=df.patch_order.str.zfill(4)

df['patch_iszz']=df['rar_name'].str.extract('(增值)',expand=True)[0]
df.loc[df.patch_iszz.isna(),'patch_iszz']='00'
df.loc[df.patch_iszz == '增值','patch_iszz']='01'
df['patch_ists']=df['rar_name'].str.extract('(特殊)',expand=True)[0]
df.loc[df.patch_ists.isna(),'patch_ists']='00'
df.loc[df.patch_ists == '特殊','patch_ists']='01'

df['patch_ists_order']=df['rar_name'].str.extract('特殊(\d){1,3}',expand=True)[0]
df.loc[df.patch_ists=='00','patch_ists_order']='00'
df.loc[df.patch_ists=='01' ,'patch_ists_order']=df['patch_ists_order'].str.zfill(2)
df['new_order']=df.bl+df.SP+df.Pack+df.patch_order

def getcreatedate(x,y,z,t,g):
    if y=='01':
        return str(z)+t+datetime.date.today().strftime('%Y%m%d')
    else:
        if re.search('((\d){8})',x):
            return str(z)+t+str(g)+re.search('((\d){8})',x).group()
        else:
            return str(z)+t+str(g)+datetime.date.today().strftime('%Y%m%d')

df['order_by']=list(map(lambda x,y,z,t,g:getcreatedate(x,y,z,t,g),df['rar_name'],df['patch_iszz'],df['new_order'],df['patch_ists'],df['patch_ists_order']))
df = df.sort_values('order_by')


df['cum_order']=list(str(x).zfill(2) for x in range(len(df)) )

df['new_file_name']=list(map(lambda x,y : x.parent.joinpath(y+x.name),df['source_name'],df['cum_order']))
df['new_file_name']=list(map(lambda x,y : x.parent.joinpath(y+x.name),df['source_name'],df['cum_order']))

list(df['new_file_name'])


list(map(lambda x,y:x.rename(y),df['source_name'],df['new_file_name']))




#对于spel_modi_FieldType.sql  ORDataType.sql 特殊脚本每个用户需要执行，则批量生成
allow_user_str = 'hs_cash:dtcxrac1;hs_user:dtcgrac1;hs_ufx:dtcxrac1;hs_mch:dtcxrac1;hs_auth:dtcxrac1;hs_asset:dtcxrac1;hs_fund:dtcgrac1;hs_ofund:dtcgrac1;hs_secu:dtcgrac1;hs_crdt:dtcgrac1;hs_cbs:dtcxrac1;hs_data:dtjyrac1;hs_arch:dtcxrac1;hs_his:dtjyrac1;hs_sett:dtcxrac1;hs_settinit:dtcxrac1;hs_ref:dtcxrac1;hs_acpt:dtcxrac1;hs_prod:dtcxrac1;hs_opt:dtcxrac1'
dict_use={'dtcxrac1':'idb#hspasswd2016','dtcgrac1':'cgjy#1226rac','dtjyrac1':'cgjy#1226rac'}
[print("conn "+x.split(":")[0]+"/"+dict_use[x.split(":")[1]]+"@"+x.split(":")[1]+"\r\n@"+str(pathlib.Path(r"d:\database\01UF20\04证券UF20-BL2013SP3补丁11-20180814-V1\00Init\spel_modi_FieldType.sql"))) for x in allow_user_str.split(";")]

[print("conn "+x.split(":")[0]+"/hundsun@"+x.split(":")[1]+"\r\n@"+str(pathlib.Path(r"d:\database\01uf20\05证券UF20-BL2013SP3补丁2-20180328-V3\00Init\ORDataType.sql"))+"\r\n@"+str(pathlib.Path(r"d:\database\01uf20\05证券UF20-BL2013SP3补丁2-20180328-V3\00Init\spel_modi_FieldType.sql"))) for x in all_user_str.split(";")]









#检测生成的sql脚本中是否需要添加dblink
import pathlib,re,os  
all_user_str = 'hs_cash:dtcxrac1;hs_user:dtcgrac1;hs_ufx:dtcxrac1;hs_mch:dtcxrac1;hs_auth:dtcxrac1;hs_asset:dtcxrac1;hs_fund:dtcgrac1;hs_ofund:dtcgrac1;hs_secu:dtcgrac1;hs_crdt:dtcgrac1;hs_cbs:dtcxrac1;hs_data:dtjyrac1;hs_arch:dtcxrac1;hs_his:dtjyrac1;hs_fil:dtjyrac1;hs_sett:dtcxrac1;hs_settinit:dtcxrac1;hs_ref:dtcxrac1;hs_acpt:dtcxrac1;hs_prod:dtcxrac1;hs_opt:dtcxrac1'
cg_users=set([x.split(':')[0] for x in all_user_str.split(';') if x.split(':')[1]=='dtcgrac1'])
cx_users=set([x.split(':')[0] for x in all_user_str.split(';') if x.split(':')[1]=='dtcxrac1'])
jy_users=set([x.split(':')[0] for x in all_user_str.split(';') if x.split(':')[1]=='dtjyrac1'])
path_all = [str(x) for x in pathlib.Path(r'd:\database').rglob('*') if re.search('passwd',x.name,re.IGNORECASE)]#根据条件过滤结果集的sql文件
all_users='|'.join(list(set([x.split(':')[0] for x in all_user_str.split(';') ])))
def getdblink(conn_user,file_name):
    try:
        content=''
        with open(file_name) as sql_f:
            line=sql_f.readline()
            while line:
                if not re.search('^(--)',line,re.IGNORECASE):
                    content=content+line
                line=sql_f.readline()
        file_user=set([x.lower() for x in list(set(re.findall('('+all_users+')',content,re.IGNORECASE)))])
        if ((file_user & cx_users) == file_user) or ((file_user & cg_users) == file_user):
            #print('###用户：',conn_user,'文件：',file_name)  #没有出现跨库的使用###来替换
        else:
            print('$$$用户：',conn_user,'文件：',file_name,'|'.join(list(file_user))) #可能出现跨库的使用$$$来替换
    except:
        print('&&&用户：',conn_user,'文件：',file_name)  #无法解析的名称用&&&替换
        pass
        
for y in path_all:
    with open(y) as f:
        line=f.readline()
        conn_user=''
        while line:
            if re.search('^(conn)',line,re.IGNORECASE):
                conn_user=line.split('/')[0].split(' ')[1].strip()
                #print(conn_user)
            if re.search('^(@)',line,re.IGNORECASE):
                if conn_user not in jy_users:
                    getdblink(conn_user,line[1:].strip())
            line=f.readline()
 
#检测是否有连接数据库错误的 
import re,pathlib
file_name=pathlib.Path(r'D:\database\01uf20\result_01uf20_2018-08-02-new.sql')
all_user_str='hs_cash:dtcxrac1;hs_user:dtcgrac1;hs_ufx:dtcxrac1;hs_mch:dtcxrac1;hs_auth:dtcxrac1;hs_asset:dtcxrac1;hs_fund:dtcgrac1;hs_ofund:dtcgrac1;hs_secu:dtcgrac1;hs_crdt:dtcgrac1;hs_cbs:dtcxrac1;hs_data:dtjyrac1;hs_arch:dtcxrac1;hs_his:dtjyrac1;hs_fil:dtjyrac1;hs_sett:dtcxrac1;hs_settinit:dtcxrac1;hs_ref:dtcxrac1;hs_acpt:dtcxrac1;hs_prod:dtcxrac1;hs_opt:dtcxrac1'
dict_user={ x.split(':')[0]:x.split(':')[1] for x in all_user_str.split(';')}        
with open(file_name,'r') as f:
    line=f.readline()
    while line:
        if re.search('^conn.*',line):
            #print(dict_user[line.split(' ')[1].split('/')[0]],line.split(' ')[1].split('@')[1])
            if dict_user[line.split(' ')[1].split('/')[0]] !=line.split(' ')[1].split('@')[1].strip():
                print(line)
        line=f.readline()

#去除合并脚本中有oracle10g的用户
import pathlib,re
file_name=pathlib.Path(r'D:\database\02user\result_02user_2018-08-02.sql')
new_sql_file=open(file_name.parent.joinpath(file_name.stem+'-new'+file_name.suffix),'w')
with open(file_name,'r') as f:
    line=f.readline()
    flag=0
    while line:
        if re.search('oracle10g',line) and re.search('^prompt 批量执行.*',line):
            flag=1
        elif re.search('^prompt 批量执行.*',line):
            flag=0
        if  flag==1:
            new_sql_file.write('--'+line)
        else:
            new_sql_file.write(line)
        line=f.readline()
new_sql_file.close()

#替换密码：
dict_use={'dtcxrac1':'idb#hspasswd2016','dtcgrac1':'cgjy#1226rac','dtjyrac1':'cgjy#1226rac'}
temp_list=[]
for x in pathlib.Path(r'D:\database\01UF20').rglob('*.log'):
   if re.search('^combine',x.name):
      temp_data={}
      for y in x.parent.glob('*.sql'):
         temp_data[os.path.getmtime(y)]=y
      temp_list.append(temp_data[sorted(temp_data.keys())[-1]])
for file_name in temp_list:
    new_sql_file=open(file_name.parent.joinpath(file_name.stem+'-passwd'+file_name.suffix),'w')
    with open(file_name,'r') as f:
        line=f.readline()
        while line:
            if  re.search('^conn.*',line):
                new_sql_file.write(line.replace('hundsun',dict_use[line.strip().split('@')[1]]))
            else:
                new_sql_file.write(line)
            line=f.readline()
    new_sql_file.close()
    
    







    
    
#以下信息为如何规避xml配置文件中重复的组件 ，适用于so文件，不适用于内存表
#D:\hundsun_sj\01UF20\xml\config_as.xml 为ls或者是as的配置文件
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
    
    
#以下信息为检查内存表中是否有重复的内存表信息：
#D:\hundsun_sj\01UF20\xml\hsmdb.xml 为内存表的配置文件
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

            
            
            
            
            
            
            
            
            
 
#检查xml文件加载的so是否存在真实的文件
appcoms=[x.name for x in pathlib.Path(r'D:\test\appcom\appcom').glob('*.so')]
with open(r'D:\test\20180727\config_ls.xml','r') as f:
    txt=f.read()
tree=tree=ET.fromstring(txt)
xml_appcom=['lib'+x.attrib['dll']+'.so' for x in tree.iter('component')]

[x for x in xml_appcom if x not in appcoms]


