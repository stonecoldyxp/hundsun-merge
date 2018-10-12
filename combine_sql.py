# -*- coding: utf-8 -*-
import pathlib,logging,os,time
from functools import reduce
from core import deal_file
#################################################################################################
#配置信息-begin  如下三个配置参数用于可以按照实际情况来配置
#################################################################################################
#定义了合并文件的结果文件夹
DEST_DIR_NAME=r'd:\database'
#数据库中所有的数据用户以及实例名称
#格式为：'用户1:用户1所在实例;用户2:用户2所在实例;...用户N:用户N所在实例'
ALL_USER_STR = 'hs_cash:dtcxrac1;hs_user:dtcgrac1;hs_ufx:dtcxrac1;hs_mch:dtcxrac1;hs_auth:dtcxrac1;hs_asset:dtcxrac1;hs_fund:dtcgrac1;hs_ofund:dtcgrac1;hs_secu:dtcgrac1;hs_crdt:dtcgrac1;hs_cbs:dtcxrac1;hs_data:dtjyrac1;hs_arch:dtcxrac1;hs_his:dtjyrac1;hs_fil:dtjyrac1;hs_sett:dtcxrac1;hs_settinit:dtcxrac1;hs_ref:dtcxrac1;hs_acpt:dtcxrac1;hs_prod:dtcxrac1;hs_opt:dtcxrac1'
#设置生产环境中每个数据库中对应的用户密码，前提条件是每个库中的所有用户的密码都一样
#如果是测试环境或全真环境，密码默认都取值为hundsun
#格式为：{数据库实例名1:密码1,数据库实例名2:密码2}
DICT_USE={'dtcxrac1':'passwd2016','dtcgrac1':'passwd2016','dtjyrac1':'passwd2016'}
#配置测试环境需要过滤的用户
#格式为：
#[(环境名称1(自定义用于区分),数据库实例名1,过滤用户1,过滤用户2,...),(环境名称1(自定义用于区分),数据库实例名2,过滤用户1,过滤用户2,...)]
#其中 环境名称n,数据库实例名1 必须提供
#如 [('测试环境','uf20csdb','hs_fil'),('全真环境','ufqzcs','hs_fil','hs_cash'),('测试环境-2','ora_data')]
DICT_ENV=[('测试环境','uf20csdb','hs_fil'),('全真环境','ufqzcs','hs_fil','hs_cash')]
#是否需要检查待合并的升级包中是否存在尚未解压的文件 判断文件后缀为rar,zip
#如适当性平台可以将这个设置为0，因为有流程文件是压缩文件，不需要解压即可以合并
IF_CHECK_ZIP=1
#################################################################################################
#配置信息-end
#################################################################################################


            
if __name__=="__main__":
    while True:
        source_path=input('输入合并包的目录,[q 退出]:')
        if source_path == 'q':
            os._exit(0)
        elif pathlib.Path(source_path).exists():
            break
        else:
            print('文件路径不合法,请重新输入')
    
    while True:
        input_str='请输入需要的环境,['+','.join([' '+str(x[0])+'  '+x[1][0]+' ' for x in enumerate(DICT_ENV)])+'其它值 生产 q 退出]:'
        env_flag=input(input_str)
        if env_flag == 'q':
            os._exit(0)
        elif env_flag in [str(x[0]) for x in enumerate(DICT_ENV)]:
            all_user_str=reduce(lambda x,y :  x.replace(y,DICT_ENV[int(env_flag)][1]) ,[ALL_USER_STR]+list(set([z.split(':')[1] for z in ALL_USER_STR.split(';') if z ])))
            filter_user=[x+':'+ DICT_ENV[int(env_flag)][1] for x in DICT_ENV[int(env_flag)][2:] if x ]
            allow_user_str=';'.join([w for w in reduce(lambda x,y :  x.replace(y,'') ,[all_user_str]+filter_user).split(';') if w ])
            break
        elif env_flag == '':
            print('输入不能为空')
        else:
            all_user_str=ALL_USER_STR
            allow_user_str=ALL_USER_STR
            break
    #source_path = r'E:\2018年工作内容\日间测试\20180611\USER'
    outfile_flag=pathlib.Path(source_path).parts[-1]
    dest_path =  str(pathlib.Path(DEST_DIR_NAME).joinpath(pathlib.Path(source_path).parts[-1]))

    #allow_user_str = 'hs_user:dtcgrac1;hs_asset:dtcxrac1;hs_secu:dtcgrac1;hs_data:dtjyrac1;hs_sett:dtcxrac1'


    os.linesep='\n'
    logging_file = 'combine_'+time.strftime('%Y-%m-%d', time.localtime())+'.log'
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S',filename=logging_file,filemode="w")
    #################################################################################################
    #定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    #################################################################################################
    #初始化实例，获得相关的数据信息
    ins_name = deal_file(source_path,dest_path,all_user_str,allow_user_str,logging_file,outfile_flag)
    #检查否存在未解压的文件
    checkzip_result = ins_name.checkzipfile()
    if IF_CHECK_ZIP:
        if checkzip_result:
            #print(checkzip_result)
            logging.warn('存在压缩包的目录有：  '+os.linesep+os.linesep.join(checkzip_result))
            logging.warn('有压缩文件，请解压后再执行')
            os._exit(1)
    #移动sql文件到目标路径
    ins_name.move_file()
    #写开始内容
    ins_name.write_result_begin()
    #写batch内容
    ins_name.write_result_content()
    #写结束内容
    ins_name.write_result_end()
    #检查dblink
    ins_name.check_dblink()
    #检查oracle10的文件
    ins_name.check_oracle10g()
    #显示其他信息：
    ins_name.showinfo()
    #屏蔽oracle10g的sql语句
    ins_name.remove_oracle10g()
    #修改文件的密码
    if int(env_flag) not in range(len(DICT_ENV)):
        ins_name.change_passwd(DICT_USE)
    #移动日志文件
    ins_name.move_loggingfile()
    print('输出路径为:',dest_path)