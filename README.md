## SagiriGraiaPlatform 插件集合

这是一个存储适用于 [SagiriGraiaPlatform](https://github.com/SAGIRI-kawaii/SagiriGraiaPlatform) 的插件的仓库

## 如何使用

将插件文件夹放入 SagiriGraiaPlatform 下的 plugins 文件夹即可

注意插件文件夹名应与插件主文件命名相同

## 插件模板

请查看 [plugin_template.py](plugin_template.py)

其中提供了获取 SagiriGraiaPlatform 示例以及编写插件所需的 app、bcc、loop 的方法

若你不知道这些是什么，请前往 [GraiaProject/Application](https://github.com/GraiaProject/Application) 学习如何使用Graia

## 插件列表

- [MessagePrinter](plugins/MessagePrinter) 一个示例插件，输出所有收到的消息
- [GithubRepositoriesFinder](plugins/GithubRepositoriesFinder) 一个能搜索github仓库的插件
- [GroupWordCloudGenerator](plugins/GroupWordCloudGenerator) 记录聊天记录并生成个人/群组词云
- [SetuSaver](plugins/SetuSaver) 根据pid存储图片
- [WeiboHotSearch](plugins/WeiboHotSearch) 获取当前微博热搜50条