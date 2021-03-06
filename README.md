# hundsun-merge

#### 项目介绍
    用于恒生升级包的合并与配置文件的提取

#### 软件架构
     ################################################
     pack_sort.py 用于原始升级包排序  **接口文件** 
     hundsun.py 用于中间件以及客户端文件的的更新整理  **接口文件** 
     merge_sql.py 用于数据库文件的合并，该文件不包含plb文件的合并，只是用于合并*.sql文件  ***接口文件*** 
     util.py 用于升级包排序，合并结果修改的相关操作 参考文件中的备注说明
     core.py 核心文件，不需要修改变动
     ################################################
     
#### 环境要求：
    python 3.6
    pip3 install xlrd
    pip3 install numpy 
    pip3 install pandas
    pip3 install rarfile
#### 程序特点 
    1、升级包自动排序，可以重复执行
    2、自动解压文件并删除压缩包
    3、自动提取提取配置内容
    4、配置灵活，按照需求自动过滤不需要合并的数据库用户 
    5、多套环境使用一个升级工具，比如生产，仿真，全真等环境可以通过配置环境以及该环境的过滤用户每次升级按照提示自动选择。 
    6、自动替换生产环境数据库用户密码。
    7、合并sql的同时自动检查是否有跨库的sql文件
    8、自动注释oracle10g的sql文件
    9、自动获取结果中所有.so文件的版本信息


#### 使用说明

步骤1：原始升级包排序：

        假设：原始路径为：E:\2018年工作内容\全真升级\01-uf20    标记为`$_PATH`;
        1.1、将原始升级压缩包复制到`$_PATH`
        1.2、使用 pack_sort.py 脚本进行升级包的排序，执行 python pack_sort.py 
        1.3、分别解压重命名的压缩包并删除原始升级包 【注意检查排序是否正确】
        范例格式为：
       $_PATH+-
             +---01证券UF20-BL2013SP2PACK1补丁51-20170706-V2
             +---02SP2PACK1补丁51增值程序
             +---03证券UF20-BL2013SP2PACK1补丁52-20170713-V2
             +---04SP2PACK1补丁52增值程序
             +---05证券UF20-BL2013SP2PACK1补丁53-20170719-V2
             \\---06SP2PACK1补丁53增值程序

步骤2：
    客户端中间件报盘机等文件的合并hundsun.py使用：

        #####################################################
        执行说明：
        #####################################################
            1、执行：python hundsun.py
            2、按照提示输入原始目录 即$_PATH
            3、合并的结果在hundsun.py中 dest_dir_name的目录中
        
        
        #####################################################
        合并结果说明：
        #####################################################
            +---combine_01-uf20   #合并的文件信息
            +---readme_01-uf20    #各个升级包中的升级说明文件
                +---readme_all.txt  #所有升级说明中的说明内容
                +---readme_all_re.txt  #根据readme_all.txt文件的内容提取的内存表、加载的so文件、路由等信息
                \\---readme_relationship.txt  #合并的结果于文件夹中的说明文件与原始升级包中的关系
            +---combine_hundsun_01-uf202018-10-10.log   #合并日志信息
            \\---uncombine_01-uf20  #尚未合并的文件
步骤3：
    数据库升级包的合并merge_sql.py使用

        #####################################################
        执行说明：
        #####################################################
            1、执行：python merge_sql.py
            2、按照提示输入原始目录 即$_PATH
            3、按照提示输入需要执行的环境
            4、合并的结果在该文件中的配置项DEST_DIR_NAME目录中

        #####################################################
        合并结果说明：
        #####################################################
            +---result_01-uf20_2018-10-10.sql  #合并的以后生成的结果文件
            +---result_01-uf20_2018-10-10-new.sql    #因本人使用的是oracle11g,所以将配置文件中的oracle10g的文件全部注释
            +---result_01-uf20_2018-10-10-new-passwd.sql    #替换为生产环境使用的密码，测试环境没有该文件
            \\---combine_2018-10-10.log   #合并日志信息



