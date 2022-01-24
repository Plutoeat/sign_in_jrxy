# sign_in_jrxy
实现今日校园自动签到

## **==提交出了问题待修改==**

### *==此代码开源使用，旨在为学生提供便捷，禁止将此代码用于盈利，禁止学生将此代码用于不正当地方，如果有问题一定要如实填报==*

## 一、配置文件

在项目根目录下运行`generate.py文件`,如下图所示，对`大连大学`支持更佳，其他学校没试过



<img src="./Images/01.png" style="zoom:38%;" />

## 二、部署项目

### 1.本地运行（windows）其他环境请自行研究

#### 1.批处理文件

>1. 打开`autorun.txt`填写项目绝对路径
>2. 保存，将后缀名改为.bat，改完名字`autorun.bat`
>3. win+r,输入shell:startup
>4. 将`autorun.bat`文件移至打开的文件夹中



<img src="./Images/02.png" style="zoom:38%;" />

#### 2.配置运行环境

**关于如何配置python运行环境(项目使用3.7版本，不一定一样)请自行搜索，网上有很多教程不再赘述**

1. win+r, 输入cmd

   ```shell
   pip3 install -r requirements.txt
   ```

   有的下载比较慢可以加一个镜像源

   ```shell
   pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

   

到此你的环境已经部署在本地，每天打开电脑他就会运行

### 2.云函数(请自行研究，网上也有许多教程)
