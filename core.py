# -*- coding: utf-8 -*-
import pathlib,shutil,logging,os,re,time,stat,xlrd
from functools import reduce
from collections import Counter

class hundsun:
    """
     用户恒生客户端以及中间件文件的升级脚本的合并
     python hundsun.py 将会调用该类
    """
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
            brother_other_dirs = [y for x in self.subdir_list for y in x.rglob('*') if y.is_dir() if y.name.lower() in brother_appcom_dirs]
            brother_sub_files = [ {'relative_dir':y.relative_to(x.parent),'file_name':y} for x in brother_other_dirs  for y in x.rglob('*') if y.is_file() ]
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
                    logging.info('开始移动文件'+str(y['file_name'])+'到'+str(dest_file)+'成功'+os.linesep)
                    if dest_file.exists():
                        try:
                            os.chmod(dest_file, stat.S_IWRITE )
                            dest_file.unlink()
                        except:
                            logging.info('^'*30+'use system cmd to delete file')
                            os.system('del /F '+str(dest_file))
                    shutil.copyfile(y['file_name'],dest_file)
                    try:
                        shutil.copystat(y['file_name'],dest_file)
                    except:
                        logging.error('拷贝文件状态失败,请检查:'+str(y['file_name']))
                    try:
                        os.remove(y['file_name'])
                    except:
                        logging.info('^'*30+'use system cmd to delete file')
                        os.system('del /F '+str(y['file_name']))
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
    def get_so_version(self):
        version_dict={}
        logging.info('开始读取该升级包中的so文件')
        for file_name in self.combine_dir.joinpath('appcom').rglob('*.so'):
            with open(file_name,'rb') as f:
                search_str=re.search('V(\d+\.){1,}\d+',repr(f.read()))
            if search_str:
                version_dict[file_name.name]=search_str.group()
            else:
                version_dict[file_name.name]='unkown'
        logging.info('读取该升级包中的so文件完成')
        with open(self.readme_dir.joinpath('appcom_version.txt') ,'w') as g:
            g.write('#'*70+os.linesep+' appcom version'+os.linesep+'#'*70+os.linesep)
            for k,v in version_dict.items():
                g.write('{:<50}{:<20}'.format(k,v)+os.linesep)
        logging.info('so文件版本信息写入'+str(self.readme_dir.joinpath('appcom_version.txt'))+'文件中')

class merge_sql:
    """
     用户恒生数据库升级的合并脚本
     python merge_sql.py 将会调用该类
    """
    def __init__(self,source_path,dest_path,all_user_str,allow_user_str,logging_file,outfile_flag):
        self.source_path = source_path
        self.outfile_flag = str(outfile_flag)
        self.all_user_str = all_user_str
        self.allow_user_str = allow_user_str
        self.dest_path = dest_path
        self.logging_file = logging_file
        self.no_batchfile_list=[]
        self.dest_all_sqlfile_list = []
        self.ignore_user_list=[]
        self.ignore_sqlfile_list=[]
        self.notin_dirsql_list=[]
        self.notin_batch_list=[]
        self.nobatchfile_list=[]
        self.oracle10_list=[]
        self.all_user_reg='|'.join(['('+x.split(':')[0].split('_')[1]+'_)' for x in self.all_user_str.strip().split(';')  if len(x)])
        self.all_user_dict={x.split(':')[0]:x.split(':')[1] for x in self.all_user_str.strip().split(';') if len(x) }
        self.allow_user_reg='|'.join(['('+x.split(':')[0].split('_')[1]+')' for x in self.allow_user_str.strip().split(';') if len(x) ])
        self.allow_user_dict={x.split(':')[0]:x.split(':')[1] for x in self.allow_user_str.strip().split(';') if len(x) }
        self.batchfile_list = []
        self.sqldir_list=[]
        self.outsqlfile = str(str(pathlib.PurePath(self.dest_path,'result_'+self.outfile_flag+'_'+time.strftime('%Y-%m-%d', time.localtime())+'.sql')))
        self.outlogfile = str(str(pathlib.PurePath(self.dest_path,'result_'+self.outfile_flag+'_'+time.strftime('%Y-%m-%d', time.localtime())+'.log')))
        self.plb_file_list=[x for x  in pathlib.Path(self.source_path).rglob('*.plb') ]
        self.source_sqlfile_list = [x for x  in pathlib.Path(self.source_path).rglob('*.sql') ]+self.plb_file_list
        self.check_dblink_list = []
        self.check_dblink_failed_list = []
        self.dest_sqlfile_list = []
        #self.dict_use=dict_use
         

    def check_dblink(self):
        if self.nobatchfile_list:
            logging.warn('-'*50+os.linesep+'不存在batch*.sql的文件有：  '+os.linesep+os.linesep.join(self.nobatchfile_list))

        for x in self.dest_sqlfile_list:
            try:
                content =x.read_text()
                if re.search('(identified|dblink)',content):
                    self.check_dblink_list.append(str(x))
            except:
                self.check_dblink_failed_list.append(str(x))
            
        if self.check_dblink_list:
            logging.warn('-'*50+os.linesep+'可能存在dblink的文件如下：'+os.linesep+os.linesep.join(self.check_dblink_list)+os.linesep*2)
        else:
            logging.info('-'*50+os.linesep+'可以检查的文件中未检查到dblink')
        if self.check_dblink_failed_list:
            logging.warn('-'*50+os.linesep+'检查dblink失败的文件如下：'+os.linesep+os.linesep.join(self.check_dblink_failed_list)+os.linesep*2)
    def check_oracle10g(self):
        [self.oracle10_list.append(str(x)) for x in self.dest_sqlfile_list if re.search('(oracle10g)',str(x))]
        if self.oracle10_list:
            logging.warn('-'*50+os.linesep+'可能存在oracle10g的文件如下：'+os.linesep+os.linesep.join(self.oracle10_list)+os.linesep*2)
    def showinfo(self):
        if self.notin_dirsql_list:
            temp_list=[]
            [temp_list.append(str(x)) for x in self.notin_dirsql_list]
            logging.warn('-'*50+os.linesep+'batch*.sql中有，但是目录中没有的文件有：'+os.linesep+os.linesep.join(temp_list)+os.linesep*2)
            
        if self.notin_batch_list:
            temp_list=[]
            [temp_list.append(str(x)) for x in self.notin_batch_list]
            logging.warn('-'*50+os.linesep+'目录中有，但是batch*.sql中没有的文件有：'+os.linesep+os.linesep.join(temp_list)+os.linesep*2)
            
        if self.ignore_sqlfile_list:
            temp_list=[]
            [temp_list.append(str(x)) for x in self.ignore_sqlfile_list]
            logging.warn('-'*50+os.linesep+'根据过滤用户的要求，被过滤的文件有：'+os.linesep+os.linesep.join(temp_list)+os.linesep*2)
    def sort_list(self):
        try:
            temp_dir=[]
            temp_dir = [x for x in pathlib.Path(self.dest_path).iterdir() if x.is_dir()]
            [temp_dir.append(y) for x in temp_dir for y in x.iterdir() if y.is_dir() and y not in temp_dir ]
            [x.replace(pathlib.Path(x.parent,'00'+x.parts[-1])) for x in temp_dir if x.parts[-1].lower() == 'sql']


            temp_dir=[]
            temp_dir = [x for x in pathlib.Path(self.dest_path).iterdir() if x.is_dir()]
            [temp_dir.append(y) for x in temp_dir for y in x.iterdir() if y.is_dir() and y not in temp_dir ]
            [x.replace(pathlib.Path(x.parent,'01'+x.parts[-1])) for x in temp_dir if x.parts[-1].lower() == 'hundsun']

            temp_dir=[]
            temp_dir = [x for x in pathlib.Path(self.dest_path).iterdir() if x.is_dir()]
            [temp_dir.append(y) for x in temp_dir for y in x.iterdir() if y.is_dir() and y not in temp_dir ]
            [x.replace(pathlib.Path(x.parent,'03'+x.parts[-1])) for x in temp_dir if x.parts[-1].lower() == 'sqlpatch']
            
            temp_dir=[]
            temp_dir = [x for x in pathlib.Path(self.dest_path).iterdir() if x.is_dir()]
            [temp_dir.append(y) for x in temp_dir for y in x.iterdir() if y.is_dir() and y not in temp_dir ]
            [x.replace(pathlib.Path(x.parent,'03'+x.parts[-1])) for x in temp_dir if x.parts[-1].lower() == 'patch']
            
            temp_dir=[]
            temp_dir = [x for x in pathlib.Path(self.dest_path).iterdir() if x.is_dir()]
            [temp_dir.append(y) for x in temp_dir for y in x.iterdir() if y.is_dir() and y not in temp_dir ]
            [x.replace(pathlib.Path(x.parent,'05'+x.parts[-1])) for x in temp_dir if x.parts[-1].lower() == 'procedure']
        except PermissionError as e:
            logging.warn('目标路径'+self.source_path+'中的中的某个文件夹的窗口可能'+os.linesep*2)
    def checkzipfile(self):
        return [str(x) for x  in pathlib.Path(self.source_path).rglob('*.zip') ]+[str(x) for x  in pathlib.Path(self.source_path).rglob('*.rar') ]
        #return [str(x) for x  in pathlib.Path(self.source_path).rglob('*.rar') ]
        
    def write_result_begin(self):
        if pathlib.Path(self.outsqlfile).exists():
            os.remove(self.outsqlfile)
        with open(self.outsqlfile,'a+') as f :
            f.write('---1)、本次合并包中共有'+str(len(self.dest_all_sqlfile_list))+'个*.sql文件'+os.linesep)
            f.write('---2)、本次合并包中共有'+str(len(self.batchfile_list))+'个batch.*sql文件'+os.linesep)
            f.write('---3)、本次合并包中共有'+str(len(self.no_batchfile_list))+'个xxx.*sql文件'+os.linesep)
            f.write('---4)、如果合并文件中有 $$$ 的字段，可能情况：1：无法解析文件，2：可能不再过滤的用户下 ，请根据实际情况替换'+os.linesep)
            f.write('---5)、本次过滤的用户为：'+'|'.join([x.split(':')[0] for x in self.allow_user_str.strip().split(';') if len(x) ])+os.linesep)
            f.write('---6)、特殊文件：spel_modi_FieldType.sql：所有allow_user_str参数中设置的用户都要执行一次  '+os.linesep)
            f.write('---7)、特殊文件：ORDataType.sql：连接用户名为$$$ ，是否全用户执行，自行判断  '+os.linesep)
            f.write('---8)、prompt /***注意检查upgrade.log文件中的 warning,ORA-,error 错误信息***/'+os.linesep)
            if self.plb_file_list:
                plb_str='|'.join([x.name for x in self.plb_file_list])
                f.write('---9)、prompt 存在plb文件一共有'+str(len(self.plb_file_list))+'plb文件名为:'+plb_str+os.linesep)
            f.write('whenever oserror exit;'+os.linesep)
            f.write('whenever sqlerror exit;'+os.linesep)
            f.write('set feedback off;'+os.linesep)
            f.write('spool '+self.outlogfile+os.linesep)
            f.write(os.linesep)*2
    def write_result_end(self):
        with open(self.outsqlfile,'a+') as f :
            f.write('prompt /***注意检查upgrade.log文件中的 warning,ORA-,error 错误信息***/'+os.linesep)
            f.write('spool off '+os.linesep)
            f.write(os.linesep)*2

    def move_file(self):
        self.dest_all_sqlfile_list = [ {'source_file':i,'dest_dir':pathlib.Path(pathlib.PurePath(self.dest_path,i.relative_to(self.source_path)).parent)} for i in self.source_sqlfile_list ]
        #如果需要删除目标目录下的所有文件的话，打开注释
        
        if pathlib.Path(self.dest_path).exists():
            try:
                [os.chmod(str(x),stat.S_IWRITE) for x in pathlib.Path(self.dest_path).rglob('*.sql')]
                shutil.rmtree(str(pathlib.Path(self.dest_path)))
                logging.info('删除目录成功！')
            except PermissionError as e:
                logging.warn('如下文件:'+self.dest_path+'夹中可能有存在只读属性的文件,可以清空目录'+self.dest_path+'再进行操作')
                logging.warn('具体错误信息如下： '+os.linesep+str(e))
                os._exit(1)
            except:
                logging.warn('未知的错误信息')
                os._exit(1)
        try:
            os.makedirs(str(pathlib.Path(self.dest_path)))
            logging.info('创建目录成功！')
        except:
            logging.warn('创建目录失败！')

        
        try:
            for j in self.dest_all_sqlfile_list:
                if not pathlib.Path(j['dest_dir']).exists():
                    os.makedirs(str(pathlib.Path(j['dest_dir'])))
                shutil.copy(j['source_file'],j['dest_dir'])
            logging.info('移动数据成功')
        except :
            logging.debug('移动数据失败')
        self.sort_list()    
        self.dest_sqlfile_list = [x for x  in pathlib.Path(self.dest_path).rglob('*.sql') ]
        self.dest_all_sqlfile_list = [ {'dest_dir':i.parent, 'dest_file':i,'file_name':i.name,'use_count':0} for i in self.dest_sqlfile_list ]
        try:
            self.batchfile_list.clear()
            self.no_batchfile_list.clear()
            for i, val in enumerate(self.dest_all_sqlfile_list):
                with open(val['dest_file'],'rb') as f:
                    content=repr(f.read())
                if re.search('conn(\s)*?(\S)*?/(\S)*?@',content,re.I):
                   self.batchfile_list.append(val)
                else:
                    self.no_batchfile_list.append(val)
            logging.info('过滤batch文件成功')
        except:
            logging.debug('过滤batch文件失败')
    def write_result_content(self):
        for i, val in enumerate(self.no_batchfile_list):
            if val['use_count'] == 0:
                used_file = ''
                batch_file_name = [{'dest_dir':x.parent,'dest_file':x} for x in val['dest_dir'].iterdir() if re.search('(^(BATCH).*(sql)$)',x.name,re.I)]
                if batch_file_name  == []:
                    parentdir = val['dest_dir'].parent
                    if parentdir > pathlib.Path(self.dest_path):
                        batch_file_name = [{'dest_dir':x.parent,'dest_file':x} for x in val['dest_dir'].parent.iterdir() if re.search('(^(BATCH).*(sql)$)',x.name,re.I)]
                if batch_file_name == []:
                    self.nobatchfile_list.append(str(val['dest_file']))
                    conn_user_name = '$$$'
                    conn_line_str = ''
                    if str(val['file_name']) == 'spel_modi_FieldType.sql':
                        conn_line_str = 'spel_modi_FieldType'
                    elif str(val['file_name']) == 'ORDataType.sql': 
                        conn_line_str = 'ORDataType'
                    else: 
                        all_reg_result = re.search('^('+self.all_user_reg+')',str(val['file_name']),re.I)
                        if all_reg_result:
                            conn_user_name = 'hs_'+all_reg_result.group().lower()[0:-1]
                            if conn_user_name in self.allow_user_dict.keys():
                                conn_line_str = 'conn '+conn_user_name+'/hundsun@'+self.all_user_dict[conn_user_name]+os.linesep
                            else:
                                val['use_count'] = -1
                                self.ignore_sqlfile_list.append(val['dest_file'])
                        else:
                            conn_line_str = 'conn $$$/hundsun@'+self.all_user_dict['hs_asset']+os.linesep
                    if conn_line_str:
                        if  conn_line_str == 'spel_modi_FieldType':
                            with open(self.outsqlfile,'a+') as f :
                                f.write('prompt ')
                                f.write('-'*50 + os.linesep)
                                f.write('prompt 批量执行 '+str(val['dest_file'])+os.linesep)
                                [ f.write('conn '+x.split(':')[0]+'/hundsun@'+x.split(':')[1]+os.linesep+'@'+str(val['dest_file'])+os.linesep) for x in allow_user_str.split(';') if len(x)]   
                            val['use_count']+=len(allow_user_list)
                        elif conn_line_str == 'ORDataType':
                            with open(self.outsqlfile,'a+') as f :
                                f.write('prompt ')
                                f.write('-'*50 + os.linesep)
                                f.write('prompt 批量执行 '+str(val['dest_file'])+os.linesep)
                                f.write('conn $$$/hundsun@'+self.all_user_dict['hs_asset']+os.linesep)
                                f.write('@'+str(val['dest_file'])+os.linesep)    
                            val['use_count']+=1
                        else:
                            with open(self.outsqlfile,'a+') as f :
                                f.write('prompt ')
                                f.write('-'*50 + os.linesep)
                                f.write('prompt 批量执行 '+str(val['dest_file'])+os.linesep)
                                f.write(conn_line_str)
                                f.write('@'+str(val['dest_file'])+os.linesep)    
                            val['use_count']+=1
                    
                    #logging.warn('文件  '+str(val['dest_file'])+'   没有batch文件')
                
                else:
                    allow_user_list,ignore_user_list,notin_dirsql_list,notin_batch_list  = self.get_batch_content(batch_file_name[0]['dest_file'])
                    if allow_user_list:
                        with open(self.outsqlfile,'a+') as f :
                            f.write('prompt ')
                            f.write('-'*50 + os.linesep)
                            f.write('prompt 批量执行 '+str(batch_file_name[0]['dest_file'])+os.linesep)
                            for i, val_new in enumerate(allow_user_list):
                                if isinstance(val_new,tuple):
                                    f.write(val_new[1]+os.linesep)
                                else:
                                    f.write('@'+str(val_new)+os.linesep)
                        for j, jx in enumerate(self.no_batchfile_list):
                            for j1 in allow_user_list:
                                if j1 == jx['dest_file']:
                                    jx['use_count']= jx['use_count']+1
                    if ignore_user_list:
                        for j, jx in enumerate(self.no_batchfile_list):
                            for j2 in ignore_user_list:
                                if j2 == jx['dest_file']:
                                    jx['use_count']= -1
                    if notin_batch_list:
                        for j, jx in enumerate(self.no_batchfile_list):
                            for j2 in notin_batch_list:
                                if j2 == jx['dest_file']:
                                    jx['use_count']= -2
                    
                    if len(ignore_user_list):
                        [self.ignore_sqlfile_list.append(x) for x in ignore_user_list]
                    if len(notin_dirsql_list):
                        [self.notin_dirsql_list.append(x) for x in notin_dirsql_list]
                    if len(notin_batch_list):
                        [self.notin_batch_list.append(x) for x in notin_batch_list]
    
    def remove_oracle10g(self):
        source_sql_file=pathlib.Path(self.outsqlfile)
        with open(source_sql_file.parent.joinpath(source_sql_file.stem+'-new'+source_sql_file.suffix),'w') as new_sql_file:
            with open(source_sql_file,'r') as f:
                line=f.readline()
                flag=0
                while line:
                    if re.search('oracle10g',line) and re.search('^prompt 批量执行.*',line):
                        flag=1
                    elif re.search('^prompt 批量执行.*',line) or re.search('^prompt /\*\*\*注意检.*',line):
                        flag=0
                    if  flag==1:
                        new_sql_file.write('--'+line)
                    else:
                        new_sql_file.write(line)
                    line=f.readline()
        #self.new_outsqlfile=source_sql_file.parent.joinpath(source_sql_file.stem+'-new'+source_sql_file.suffix
        
    def change_passwd(self,dict_passwd):
        source_sql_file=pathlib.Path(self.outsqlfile)
        if source_sql_file.parent.joinpath(source_sql_file.stem+'-new'+source_sql_file.suffix).exists():
            read_file=source_sql_file.parent.joinpath(source_sql_file.stem+'-new'+source_sql_file.suffix)
        else:
            read_file=source_sql_file
        try:
            with open(source_sql_file.parent.joinpath(source_sql_file.stem+'-passwd'+source_sql_file.suffix),'w') as new_sql_file:
                with open(read_file,'r') as f:
                    line=f.readline()
                    while line:
                        if  re.search('^conn.*',line):
                            new_sql_file.write(line.replace('hundsun',dict_passwd[line.strip().split('@')[1]]))
                        else:
                            new_sql_file.write(line)
                        line=f.readline()
            logging.info('修改生成的sql文件中的数据库密码完成')
        except:
            logging.warn('修改生成的sql文件中的数据库密码失败')
        
    #patchlib_file 是传入的batch*.sql的路径 类型：WindowsPath  
    def move_loggingfile(self):
        logging.info('执行成功')
        logging.shutdown()
        if pathlib.Path(self.dest_path,self.logging_file).exists():
            os.remove(str(pathlib.Path(self.dest_path,self.logging_file)))
        if pathlib.Path(self.logging_file).exists():
            shutil.move(self.logging_file,self.dest_path)
    def get_batch_content(self,pathlib_file):
        
        try:
            allow_user_list = []
            ignore_user_list = []
            #batch文件中有，目录中没有
            notin_dirsql_list = []
            notin_batch_list = []
            batch_content_list = []
            batch_dir_sqllist = [x for x  in pathlib_file.parent.rglob('*.sql')  if not re.search('(^(BATCH).*(sql)$)',x.name,re.I)]
            with open(str(pathlib_file)) as f:
                flag = 0
                for line in f:
                    if re.search('(^(conn).*)',line.strip().lower(),re.I):
                        conn_user_name = line.strip().split('/')[0].split(' ')[1].strip()
                        if conn_user_name in self.allow_user_dict.keys():
                            flag = 0
                            allow_user_list.append((1,'conn '+conn_user_name+'/hundsun@'+self.all_user_dict[conn_user_name.lower()]))
                        else:
                            flag = 1
                    elif re.search('(^(@).*)',line.strip()):
                        sql_line = pathlib.Path(line.strip()[1:])
                        list_temp = [x for x  in batch_dir_sqllist  if re.search(sql_line.name,x.name)]
                        if not list_temp:
                            notin_dirsql_list.append(str(pathlib_file)+':'+line.strip()) 
                        if flag == 0:
                            if list_temp:
                               [allow_user_list.append(x) for x in list_temp] 
                        elif flag == 1:
                            if list_temp:
                               [ignore_user_list.append(x) for x in list_temp]
            union_list = list(set(allow_user_list).union(set(ignore_user_list)))
            notin_batch_list = [x  for x in batch_dir_sqllist if x not in union_list] 
            return allow_user_list,ignore_user_list,notin_dirsql_list,notin_batch_list                      
        except:
            logging.debug('文件：'+str(pathlib_file)+'解析内容失败')
            logging.warn(os.linesep+'程序异常退出,请检查日志信息！')
            os._exit(1)