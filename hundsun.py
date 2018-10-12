# -*- coding: utf-8 -*-
#合并需要的升级文件
import pathlib
import shutil
import logging
import os
import re
import time
import stat,xlrd
from send2trash import send2trash
from collections import Counter
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

class hundsun:
    def __init__(self,source_dir_str,dest_dir_str,outfile_flag,logging_file,xlsx_sheet_name):
        self.source_dir = pathlib.Path(source_dir_str)
        self.dest_dir = pathlib.Path(dest_dir_str)
        self.outfile_flag = outfile_flag
        self.logging_file = logging_file
        self.subdir_list=[]
        self.subfile_list=[]
        self.readme_list = []
        self.list_a=xlsx_sheet_name
        self.readme_dir = self.dest_dir.joinpath('readme_'+outfile_flag)
        self.combine_dir=self.dest_dir.joinpath('combine_'+outfile_flag)
        self.subdir_name_index = -(len(self.dest_dir.parents)+2)
        self.outlogfile = str(str(pathlib.PurePath(self.dest_dir,'hundsun_'+self.outfile_flag+'_'+time.strftime('%Y-%m-%d', time.localtime())+'.log')))
        if not self.source_dir.exists():
            logging.warn('请检测如下目录是否存在信息： '+os.linesep+str(self.source_dir))
            os._exit(1)

    def checkzipfile(self):
        return [str(x) for x  in self.source_dir.rglob('*.zip') ]+[str(x) for x  in self.source_dir.rglob('*.rar') ]           
    def copytodest(self):
        if self.dest_dir.exists():
            try:
                [ os.chmod(x,stat.S_IWRITE) for x in self.dest_dir.rglob('*')  if x.is_file() and not os.access(x,os.W_OK) ]
                shutil.rmtree(self.dest_dir)
                logging.info('删除目录成功！')
            except PermissionError as e:
                logging.warn('如下文件:'+str(self.dest_dir)+'夹中可能有存在只读属性的文件,可以清空目录'+str(self.dest_dir)+'再进行操作')
                logging.warn('具体错误信息如下： '+os.linesep+str(e))
                os._exit(1)
            except:
                logging.warn('未知的错误信息')
                os._exit(1)
        try:
            logging.info('开始拷贝文件到目标路径，目标路径为'+str(self.dest_dir)+os.linesep)
            shutil.copytree(self.source_dir,self.dest_dir)
            [ os.chmod(x,stat.S_IWRITE) for x in self.dest_dir.rglob('*')  if x.is_file() and not os.access(x,os.W_OK) ]
            logging.info('拷贝文件成功，目标路径为'+str(self.dest_dir)+os.linesep)
        except:
            logging.warn('拷贝文件失败，请检查，或者删除目标路径后重新拷贝，目标路径为'+str(self.dest_dir)+os.linesep)
        try:
            [ os.chmod(x,stat.S_IWRITE) for x in self.source_dir.rglob('*.*')  if x.is_file() and not os.access(x,os.W_OK) ]
            logging.warn('修改文件权限成功：'+os.linesep)
        except:
            logging.warn('失败,请检查是否存在，目录为：'+str(self.source_dir)+os.linesep)
            
    def del_unuseitems(self):
        parent_list = list(set([x.parent for x in self.dest_dir.rglob('*.sql')]))
        try:
            [os.remove(x) for x in self.dest_dir.rglob('*.sql')]
            logging.info('删除目标目录中的sql文件成功'+os.linesep)
        except:
            logging.warn('删除目标目录中的sql文件失败'+os.linesep)
            os._exit(1)
        try:
            temp_list=[]
            while parent_list:
                     temp_list.clear()
                     [x.rmdir() for x in parent_list if  x.exists() and not os.listdir(x)]
                     [temp_list.append(x.parent) for x in parent_list if x.parent.exists() and x.parent > self.dest_dir]
                     parent_list.clear()
                     parent_list = list(set(temp_list))
            logging.info('清空目标路径'+str(self.dest_dir)+'下的空目录成功'+os.linesep)
        except:
            logging.warn('清空目标路径'+str(self.dest_dir)+'下的空目录失败'+os.linesep)
        try:
            self.subdir_list=[x for x in self.dest_dir.iterdir() if x.is_dir()]
            #self.subfile_list=[x for x in self.dest_dir.iterdir() if x.is_file()]
            logging.info('删除所有内容为空的目录成功'+os.linesep)
            self.readme_dir.mkdir()
            logging.info('创建目录'+str(self.readme_dir)+'成功'+os.linesep)
            self.combine_dir.mkdir()
            logging.info('创建目录'+str(self.combine_dir)+'成功'+os.linesep)
            
        except:
            logging.warn('删除空目录和创建目录失败'+os.linesep)
            os._exit(1)
    def filte_move_readme(self):
        try:
            xls_list = list(self.dest_dir.rglob('*.xls*'))
            xls_filter_list = [x for x in xls_list if re.search('(readme)|(BL)|(说明)|(补丁)|(SP)|(PACK)|(V\d)',x.name,re.I)]
            txt_list = list(self.dest_dir.rglob('*.txt'))
            txt_filter_list = [x for x in txt_list if re.search('(readme)|(M\d{4}\d(2)\d{2})|(BL)|(说明)|(补丁)|(SP)|(PACK)|(V\d)',x.name,re.I)]
            try:
                [os.chmod(x,stat.S_IWRITE) for x in txt_filter_list]
                logging.info('修改txt说明文件权限成功'+os.linesep)
            except:
                logging.warn('修改txt说明文件权限失败'+os.linesep)
            try:
                for x in txt_filter_list:
                    with open(x, 'a') as f:
                        f.write(os.linesep+str(x)+os.linesep)
                    logging.info('写入文件'+str(x)+'成功'+os.linesep)
            except:
                logging.info('写入备注文件失败'+os.linesep)
            temp_readme_list = []
            [temp_readme_list.append({'source_file':x,'dest_file':self.readme_dir.joinpath(x.name)}) for x in xls_filter_list ]
            [temp_readme_list.append({'source_file':x,'dest_file':self.readme_dir.joinpath(x.name)}) for x in txt_filter_list ]
            dest_file_list = [x['dest_file'] for x in temp_readme_list]
            count_dict = dict(Counter(dest_file_list))
            repeat_files = [x for x in count_dict if count_dict[x] >1]
            for x in temp_readme_list:
                if x['dest_file'] in repeat_files:
                    number_value = re.search('(\d)+',list(x['source_file'].parents)[self.subdir_name_index].name)
                    parent_name = x['source_file'].parent.name
                    if number_value:
                        prefix_name = str(number_value.group())
                    else:
                        prefix_name = list(x['source_file'].parents)[self.subdir_name_index].name[-15:]
                    x['dest_file']= x['dest_file'].parent.joinpath('-'.join([prefix_name,parent_name,x['dest_file'].name]))
            logging.info('在目录'+str(self.source_dir)+'中过滤升级说明文件成功'+os.linesep)
        except:
            logging.warn('在目录'+str(self.source_dir)+'中过滤升级说明文件失败'+os.linesep)
        try:
            for x in temp_readme_list:
                shutil.move(x['source_file'],x['dest_file'])
            logging.info('移动升级说明文件成功'+os.linesep)
            try:
                with open(self.readme_dir.joinpath('readme_relationship.txt'),'w') as f:
                    for x in temp_readme_list:
                        f.write(str(x['source_file'])+'    |--->'+str(x['dest_file'])+os.linesep)
                logging.info('写入说明文件对应关系成功'+os.linesep)
            except:
                logging.warn('写入说明文件对应关系失败'+os.linesep)
        except:
            logging.warn('移动升级说明文件失败'+os.linesep)
    def get_readme(self):
        readme_relationship=self.readme_dir.joinpath('readme_relationship.txt')
        result_readme_all=self.readme_dir.joinpath('readme_all.txt')
        with open(result_readme_all,'w') as file_handle:
            with open(readme_relationship,'r') as k:
                txt=k.read()
            w=[pathlib.Path(x.split('|--->')[1]) for x in txt.split('\n')[::-1] if x.strip() ]
            for t in w:
                if t.suffix in ('.xls','.xlsx'):
                    logging.info('开始处理文件'+str(t))
                    xlsx=xlrd.open_workbook(t)
                    temp_list=[x for x in xlsx.sheet_names()  for y  in self.list_a if re.search(y,x) ]
                    if temp_list:
                        file_handle.write(os.linesep+'#'*40+os.linesep)
                        file_handle.write(str(t))
                        file_handle.write(os.linesep+'#'*40+os.linesep)
                        for y in temp_list:
                            logging.info('sheet :'+str(y))
                            file_handle.write('$$$'*10+os.linesep+y+os.linesep+'$$$'*10+os.linesep)
                            sheet=xlsx.sheet_by_name(y)
                            for rownum in range(sheet.nrows):
                                for x in sheet.row_values(rownum):
                                    if str(x).strip():
                                        try:
                                            file_handle.write(str(x)+os.linesep)
                                        except:
                                            file_handle.write('升级说明文件'+t.name+'中的sheet['+y+']页第'+str(rownum)+'行编码错误,解析失败'+os.linesep)
                                            pass
                    logging.info('#'*30) 
                if t.suffix in ('.txt'):
                    logging.info('开始处理文件'+str(t))
                    try:
                        with open(t,'r') as f:
                            file_handle.write(os.linesep+'#'*40+os.linesep)
                            file_handle.write(str(t))
                            file_handle.write(os.linesep+'#'*40+os.linesep)
                            file_handle.write(f.read())
                    except:
                        logging.warn('打开文件'+str(t)+'失败')
                        pass
                            

        with open(result_readme_all,'r') as f:
            txt=f.read()
        with open(self.readme_dir.joinpath('readme_all_re.txt'),'w') as f:
            f.write('#'*40+'\n')
            f.write('关于内存表的配置项目：\n')
            f.write('#'*40+'\n')
            [f.write(x+'\n') for x in re.findall('<table[\S\s]*?table>',txt)]
            f.write('#'*40+'\n')
            f.write('关于中间件LS的配置项目：\n')
            f.write('#'*40+'\n')
            [f.write(x+'\n') for x in re.findall('<component[\S\s]*?/>',txt) if re.search('_ls_',x)]
            f.write('#'*40+'\n')
            f.write('关于中间件AS的配置项目：\n')
            f.write('#'*40+'\n')
            [f.write(x+'\n') for x in re.findall('<component[\S\s]*?/>',txt) if re.search('_as_',x)]    
            f.write('#'*40+'\n')
            f.write('关于中间件workeritem的配置项目：\n')
            f.write('#'*40+'\n')
            [f.write(x+'\n') for x in re.findall('<workeritem[\S\s]*?/>',txt) ]    
            f.write('#'*40+'\n')
            f.write('关于中间件数据库连接与同步的配置项目：\n')
            f.write('#'*40+'\n')
            [f.write(x+'\n') for x in re.findall('<ds[\S\s]*?>',txt) ]
            [f.write(x+'\n') for x in re.findall('<target[\S\s]*?>',txt) ]
            f.write('#'*40+'\n')
            f.write('关于中间件路由表的配置项目：\n')
            f.write('#'*40+'\n')
            [f.write(x+'\n') for x in re.findall('<routetable[\S\s]*?/>',txt)]
            f.write('#'*40+'\n')
            f.write('关于topic的配置项目：\n')
            f.write('#'*40+'\n')
            [f.write(x+'\n') for x in re.findall('<topic[\S\s]*?topic>',txt)]
            f.write('#'*40+'\n')
            f.write('关于plugin的配置项目：\n')
            f.write('#'*40+'\n')
            [f.write(x+'\n') for x in re.findall('<plugin[\S\s]*?plugin>',txt)]
    
    
    def move_files(self):
        flag=False
        try:
            if not self.combine_dir.joinpath('appcom').exists():
                self.combine_dir.joinpath('appcom').mkdir()
            for a in self.subdir_list:
                for b in a.rglob('*.so'):
                    shutil.copy2(b,self.combine_dir.joinpath('appcom',b.name))
                    os.remove(b)
                    logging.info('移动文件'+str(b)+'到'+str(self.combine_dir.joinpath('appcom',b.name))+'成功'+os.linesep)
            logging.info('合并so文件成功'+os.linesep)
            flag=True
        except:
            logging.warn('合并so文件失败，程序将自动退出'+os.linesep) 
            os._exit(1)
            
        if flag:
            #print(self.dest_dir)
            #os._exit(1)
            #appcom_list = [ x for x in self.dest_dir.rglob('*') if x.is_dir() and x.name=='appcom']
            appcom_list = [ y for x in self.subdir_list for y in x.rglob('*') if y.is_dir() and y.name=='appcom']
            appcom_dict_list=[y for x in appcom_list for y in x.parents if y.parent == self.dest_dir]
            appcom_count_dict = dict(Counter(appcom_dict_list))
            repeat_appcom_files = [x for x in appcom_count_dict if appcom_count_dict[x] >1]
            if repeat_appcom_files:
                result_list=[]
                for x in repeat_appcom_files:
                    temp_path=''
                    temp_number=0
                    for y in appcom_list:
                        for z in y.parents:
                            if x==z:
                                if temp_number < len(y.parts):
                                    temp_path=y
                    if temp_path:
                        result_list.append(temp_path)
                [os.removedirs(x) for x in appcom_list if x in result_list ]
            brother_appcom_dirs = list(set([ z.name.lower() for x in self.subdir_list for y in x.rglob('*') if y.name == 'appcom' for z in y.parent.iterdir() if z.name != 'appcom' and z.is_dir()]))
            #print('brother_appcom_dirs:',brother_appcom_dirs)
            brother_other_dirs = [y for x in self.subdir_list for y in x.rglob('*') if y.is_dir() if y.name.lower() in brother_appcom_dirs]
            #print('brother_other_dirs:',brother_other_dirs)
            brother_sub_files = [ {'relative_dir':y.relative_to(x.parent),'file_name':y} for x in brother_other_dirs  for y in x.rglob('*') if y.is_file() ]
            #print('brother_sub_files:',brother_sub_files)
            if brother_appcom_dirs:
                [ self.combine_dir.joinpath(x).mkdir() for x in brother_appcom_dirs if not self.combine_dir.joinpath(x).exists()]
                exists_file_list=[]
                #try:
                for y in brother_sub_files:
                    dest_file = self.combine_dir.joinpath(y['relative_dir'])
                    #exists_file_list.clear()
                    #exists_file_list =[x.relative_to(self.combine_dir) for x in  self.combine_dir.rglob('*') if x.is_file()]
                    if not self.combine_dir.joinpath(y['relative_dir']).parent.exists():
                        os.makedirs(self.combine_dir.joinpath(y['relative_dir']).parent)
                    if dest_file.exists():
                        try:
                            os.chmod(dest_file, stat.S_IWRITE )
                            dest_file.unlink()
                        except:
                            logging.info('^'*30)
                            logging.info('user system cmd to delete file')
                            os.system('del /F '+str(dest_file))
                            logging.info('^'*30)
                    shutil.copyfile(y['file_name'],dest_file)
                    try:
                        shutil.copystat(y['file_name'],dest_file)
                    except:
                        logging.error('拷贝文件状态失败,请检查:'+str(y['file_name']))
                    os.remove(y['file_name'])
                    logging.info('-'*30)
                    logging.info('file_name: '+str(y['file_name']))
                    logging.info('dest_file: '+str(dest_file))
                    logging.info('-'*30)
                    logging.info('移动文件'+str(y['file_name'])+'到'+str(dest_file)+'成功'+os.linesep)
                #except:
                #    logging.warn('合并其他文件失败，文件夹包括'+os.linesep)
    def checkuncomfile(self):
        uncombinefiles = [ {'relative_dir':y.relative_to(x) ,'file_name':y } for x in self.subdir_list for y in x.rglob('*') if y.is_file() ]
        if uncombinefiles:
            uncombine_dir = self.dest_dir.joinpath('uncombine_'+self.outfile_flag)
            os.makedirs(uncombine_dir)
            #try:
            for y in uncombinefiles:
                logging.info('-'*30)
                logging.info('relative_dir: '+str(y['relative_dir']))
                logging.info('file_name: '+str(y['file_name']))
                logging.info('-'*30)
                if str(y['relative_dir']) == y['file_name'].name:
                    shutil.copy2(y['file_name'],uncombine_dir.joinpath(y['file_name'].name))
                elif not uncombine_dir.joinpath(y['relative_dir']).parent.exists():
                    os.makedirs(str(uncombine_dir.joinpath(y['relative_dir']).parent))
                shutil.copy2(y['file_name'],uncombine_dir.joinpath(y['relative_dir']))
                os.remove(y['file_name'])
                logging.info('存在尚未合并的文件，已经将该文件移动到uncombine_dir目录下，信息如下：'+os.linesep+str(y['file_name'])+'    |--->'+str(uncombine_dir.joinpath(y['relative_dir']))+os.linesep)
            #except:
            #    logging.warn('存在尚未合并的文件，并且不能合并到目录：'+str(uncombine_dir)+os.linesep)
        else:
            logging.info('不存在尚未合并的文件'+os.linesep)
    def del_empty_dirs(self):
        empty_dir_list = [ x for w  in self.subdir_list for x in w.rglob('*')]
        empty_dir_list.extend([w  for w in self.subdir_list])
        sort_empty_dir_list = list(sorted(empty_dir_list,key=lambda x:-len(x.parts)))
        try:
            [x.rmdir() for x in sort_empty_dir_list]
            logging.info('删除原始目录成功'+os.linesep)
        except:
            logging.warn('删除原始目录失败'+os.linesep)
    def remove_ckfl(self):
        hsclient_dir = [x for x in self.combine_dir.rglob('*') if x.is_dir() if x.name=='HsClient']
        if hsclient_dir:
            try:
                [x.rename(x.parent.joinpath(''.join(x.name.split(re.search('范例|参考',x.name).group())))) for y in hsclient_dir for x in y.rglob('*.*') if x.is_file() if re.search('范例|参考',x.name) and not x.parent.joinpath(''.join(x.name.split(re.search('范例|参考',x.name).group()))).exists()]
                #[x.rename(x.parent.joinpath(''.join(x.name.split(re.search('范例|参考',x.name).group())))) for y in hsclient_dir for x in y.rglob('*.*') if x.is_file() if re.search('范例|参考',x.name)]
                logging.info('重命名范例参考文件成功')
            except:
                logging.warn('重命名范例参考文件失败')
        else:
            logging.warn('不存在HsClient目录')
    def move_loggingfile(self):
        logging.info('执行成功')
        logging.shutdown()
        if pathlib.Path(self.dest_dir,self.logging_file).exists():
            os.remove(pathlib.Path(self.dest_dir,self.logging_file))
        if pathlib.Path(self.logging_file).exists():
            shutil.move(self.logging_file,self.dest_dir)
            
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
    
    
    