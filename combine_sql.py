# -*- coding: utf-8 -*-
import pathlib
import shutil
import logging
import os
import re
import time
import stat
import argparse
from functools import reduce
#数据库中所有的数据用户以及服务器配置
all_user_str = 'hs_cash:dtcxrac1;hs_user:dtcgrac1;hs_ufx:dtcxrac1;hs_mch:dtcxrac1;hs_auth:dtcxrac1;hs_asset:dtcxrac1;hs_fund:dtcgrac1;hs_ofund:dtcgrac1;hs_secu:dtcgrac1;hs_crdt:dtcgrac1;hs_cbs:dtcxrac1;hs_data:dtjyrac1;hs_arch:dtcxrac1;hs_his:dtjyrac1;hs_fil:dtjyrac1;hs_sett:dtcxrac1;hs_settinit:dtcxrac1;hs_ref:dtcxrac1;hs_acpt:dtcxrac1;hs_prod:dtcxrac1;hs_opt:dtcxrac1'
dict_use={'dtcxrac1':'passwd2016','dtcgrac1':'passwd2016','dtjyrac1':'passwd2016'}
dict_env=[('uf20csdb','hs_fil'),('ufqzcs','hs_fil','hs_cash')]

class deal_file:
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
                if re.search('(^(BATCH).*(sql)$)',val['file_name'],re.I):
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
        try:
            with open(source_sql_file.parent.joinpath(source_sql_file.stem+'-passwd'+source_sql_file.suffix),'w') as new_sql_file:
                with open(source_sql_file.parent.joinpath(source_sql_file.stem+'-new'+source_sql_file.suffix),'r') as f:
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
        env_flag=input('请输入需要的环境,[0 测试 1 全真  其它值 生产 q 退出]:')
        if env_flag == 'q':
            os._exit(0)
        elif env_flag=='0':
            all_user_str=reduce(lambda x,y :  x.replace(y,dict_env[int(env_flag)][0]) ,[all_user_str]+list(dict_use.keys()))
            allow_user_str=reduce(lambda x,y :  x.replace(y,dict_env[int(env_flag)][0]) ,[all_user_str]+list(dict_use.keys()))
            #测试环境删除hs_fil用户
            allow_user_str=';'.join([x for x in allow_user_str.split(';') if x.split(':')[0] not in ['hs_fil']])
            
            break
        elif env_flag=='1':
            all_user_str=reduce(lambda x,y :  x.replace(y,dict_env[int(env_flag)][0]) ,[all_user_str]+list(dict_use.keys()))
            allow_user_str=reduce(lambda x,y :  x.replace(y,dict_env[int(env_flag)][0]) ,[all_user_str]+list(dict_use.keys()))
            allow_user_str=';'.join([x for x in allow_user_str.split(';') if x.split(':')[0] not in ['hs_fil','hs_cash']])
            break
        elif env_flag == '':
            print('输入不能为空')
        else:
            break
    #source_path = r'E:\2018年工作内容\日间测试\20180611\USER'
    outfile_flag=pathlib.Path(source_path).parts[-1]
    dest_path =  str(pathlib.Path(r'd:\database').joinpath(pathlib.Path(source_path).parts[-1]))

    #allow_user_str = 'hs_user:dtcgrac1;hs_asset:dtcxrac1;hs_secu:dtcgrac1;hs_data:dtjyrac1;hs_sett:dtcxrac1'


    os.linesep='\n'
    logging_file = 'combine_'+time.strftime('%Y-%m-%d', time.localtime())+'.log'
    
    
    '''
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='myapp.log',
                filemode='w')
    '''
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
    checkzip_result = 0
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
    if int(env_flag) not in range(len(dict_env)):
        ins_name.change_passwd(dict_use)
    #移动日志文件
    ins_name.move_loggingfile()
    print('输出路径为:',dest_path)