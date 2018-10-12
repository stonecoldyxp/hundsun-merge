# -*- coding: utf-8 -*-
#合并需要的升级文件
import pathlib,logging,os,time
from core import hundsun
######################################################################################
#配置信息-begin  如下三个配置参数用于可以按照实际情况来配置
######################################################################################
#定义了合并文件的结果文件夹
DEST_DIR_NAME=r'd:\hundsun_sj'
#升级说明中需要处理的xls文件中的sheet页
XLSX_SHEET_NAME=['安装说明','中间件配置','系统配置','特别注意','升级说明','对应配置修改']
#是否需要检查原始文件中存在未解压的文件
IF_CHECK_ZIP=1
######################################################################################
#配置信息-end
######################################################################################

            
if __name__=="__main__":
    #source_dir_str = r'E:\2018年工作内容\日间测试\20180611\USER'
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
    #
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
    ins_hundsun.copytodest()
    ins_hundsun.del_unuseitems()
    ins_hundsun.filte_move_readme()
    ins_hundsun.get_readme()
    ins_hundsun.move_files()
    ins_hundsun.checkuncomfile()
    ins_hundsun.del_empty_dirs()
    ins_hundsun.remove_ckfl()
    ins_hundsun.move_loggingfile()
    print('输出路径为:',dest_dir_str)
    
    
    