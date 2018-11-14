# -*- coding: utf-8 -*-
##############################################################
#  需要安装 numpy ,pandas包                                  #
#  pip3 install numpy                                        #
#  pip3 install pandas                                       #
#  pip3 install rarfile                                      #
#  功能:原始升级包的排序,重命名,需要手工删除原始压缩包       #
#  需要将原始升级包放入同一个目录下                          #
##############################################################
import pathlib ,re,datetime,os,platform,rarfile,shutil
import pandas as pd
import numpy as np

def getcreatedate(x,y,z,t,g):
    if y=='01':
        return str(z)+t+datetime.date.today().strftime('%Y%m%d')
    else:
        if re.search('((\d){8})',x):
            return str(z)+t+str(g)+re.search('((\d){8})',x).group()
        else:
            return str(z)+t+str(g)+datetime.date.today().strftime('%Y%m%d')
            
if __name__=="__main__":
    while True:
        #需要输入目录，如 d:\hundsun_files\*  hundsun_files目录下包含了所有的用于升级的文件。
        uf20path=input('输入需要合并包的上级目录,[q 退出]:')
        if uf20path == 'q':
            os._exit(0)
        elif pathlib.Path(uf20path).exists():
            break
        else:
            print('文件路径不合法,请重新输入')

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



    df['order_by']=list(map(lambda x,y,z,t,g:getcreatedate(x,y,z,t,g),df['rar_name'],df['patch_iszz'],df['new_order'],df['patch_ists'],df['patch_ists_order']))
    df = df.sort_values('order_by')


    df['cum_order']=list(str(x).zfill(2) for x in range(len(df)) )

    df['new_file_name']=list(map(lambda x,y : x.parent.joinpath(y+x.name),df['source_name'],df['cum_order']))
    
    [print(pathlib.Path(y).name) for y in df.new_file_name]
    
    while True:
        remane_flag=input('是否按照如上输出进行排序,[y  是 ; n  否;q 退出]:')
        if remane_flag.lower() == 'q' or remane_flag.lower() == 'n':
            os._exit(0)
        elif remane_flag.lower() == 'y':
            list(map(lambda x,y:x.rename(y),df['source_name'],df['new_file_name']))
            print('重命名文件成功')
            break
        else:
            print('输入不合法,请重新输入,[y  是 ; n  否;q 退出]:')
    
    
    
    while True:
        remane_flag=input('是否删除原始文件并自动解压,[y  是 ; n  否;q 退出]:')
        if remane_flag.lower() == 'q' or remane_flag.lower() == 'n':
            os._exit(0)
        elif remane_flag.lower() == 'y':
            if re.search('\d+',platform.machine()).group()=='64':
                rarfile.UNRAR_TOOL=str(pathlib.Path(__file__).resolve().parent.joinpath('rar_x64','UnRAR.exe'))
            else:
                rarfile.UNRAR_TOOL=pathlib.Path(__file__).resolve().parent.joinpath('rar_x32','UnRAR.exe')
            rarfiles=[(x,x.stem,rarfile.RarFile(str(x)),x.parent.joinpath(x.stem)) for x in dirname.iterdir() if rarfile.is_rarfile(str(x))]
            for item in rarfiles:
                pathlib_name,str_name,rar_file,dir_name = item
                if dir_name.exists() and dir_name.is_dir():
                    try:
                        shutil.rmtree(dir_name)
                        print('删除目录'+str(dir_name)+'成功:')
                        
                    except:
                        print('删除目录'+str(dir_name)+'失败:')
                else:
                    try:
                        dir_name.mkdir()
                        print('创建目录'+str(dir_name)+'成功:')

                    except:
                        print('创建目录'+str(dir_name)+'失败:')
                    try:
                        print('#'*20+'开始解压'+'#'*20)
                        print('文件:'+str(dir_name))
                        result=rar_file.extractall(path=str(dir_name))
                        print('#'*20+'结束解压'+'#'*20)
                        if not result:
                            pathlib_name.unlink()
                            print('删除文件成功:'+str(pathlib_name))
                        else:
                            print('解压文件失败:'+str(pathlib_name))
                    except:
                        print('删除或解压文件'+str(pathlib_name)+'异常')
            print('解压删除压缩包文件成功')
            os._exit(0)
        else:
            print('是否删除原始文件并自动解压,[y  是 ; n  否;q 退出]:')

        