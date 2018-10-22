# -*- coding: utf-8 -*-
##############################################################
#  功能:合并中间件以及客户端的文件                           #
#  1：需要首先对文件进行排序,可以使用pack_sort.py进行排序    #
#  2：需要首先对文件进行排序,可以手工进行排序                #
##############################################################
import pathlib,logging,os,time
from core import hundsun


######################################################################################
#配置信息-begin  如下三个配置参数用于可以按照实际情况来配置
######################################################################################
#定义了合并后的文件夹，文件就不存在则会自动创建
DEST_DIR_NAME=r'd:\hundsun_sj'
#升级说明中需要处理的xls文件中的sheet页,可以根据需要自行添加
XLSX_SHEET_NAME=['安装说明','中间件配置','系统配置','特别注意','升级说明','对应配置修改']
#是否需要检查原始文件中存在未解压的文件,判断后缀是否为.rar .zip
IF_CHECK_ZIP=1
######################################################################################
#配置信息-end
######################################################################################

            
if __name__=="__main__":
    while True:
        #需要输入目录，如 d:\hundsun_files\*  hundsun_files目录下包含了所有的用于升级的文件。
        source_dir_str=input('输入需要合并包的上级目录,[q 退出]:')
        if source_dir_str == 'q':
            os._exit(0)
        elif pathlib.Path(source_dir_str).exists():
            break
        else:
            print('文件路径不合法,请重新输入')
    outfile_flag = pathlib.Path(source_dir_str).parts[-1]
    dest_dir_str = str(pathlib.Path(DEST_DIR_NAME).joinpath(pathlib.Path(source_dir_str).parts[-1]))
    os.linesep='\n'
    logging_file = 'combine_hundsun_'+outfile_flag+time.strftime('%Y-%m-%d', time.localtime())+'.log'
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S',filename=logging_file,filemode="w")
    #################################################################################################
    #定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    #################################################################################################
    ins_hundsun=hundsun(source_dir_str,dest_dir_str,outfile_flag,logging_file,XLSX_SHEET_NAME)
    checkzip_result = ins_hundsun.checkzipfile()
    #checkzip_result = 0
    if IF_CHECK_ZIP:
        if checkzip_result:
            logging.warn('存在压缩包的目录有：  '+os.linesep+os.linesep.join(checkzip_result))
            logging.warn('有压缩文件，请解压后再执行')
            os._exit(1)
    #拷贝原始文件到DEST_DIR_NAME目录
    ins_hundsun.copytodest()
    #删除所有后缀是.sql的文件
    ins_hundsun.del_unuseitems()
    #提取升级说明文件
    ins_hundsun.filte_move_readme()
    #获取升级说明中的信息,所有excel中的XLSX_SHEET_NAME的sheet页与txt文件并提取常用内容
    ins_hundsun.get_readme()
    #提取升级包中的各类文件
    ins_hundsun.move_files()
    #检查是否有未合并的文件放入DEST_DIR_NAME\uncombine_*目录中
    ins_hundsun.checkuncomfile()
    #删除空文件夹
    ins_hundsun.del_empty_dirs()
    #去除hsclient目录中带有[参考 范例]的文件
    ins_hundsun.remove_ckfl()
    #获取所有合并后so的版本信息
    ins_hundsun.get_so_version()
    #移动程序日志到合并文件中
    ins_hundsun.move_loggingfile()
    print('输出路径为:',dest_dir_str)
    
    
    