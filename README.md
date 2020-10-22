# uploadImg

## 介绍

这是一个应用，用于方便地上传 markdown 使用到的图片

**该应用基于 oss 对象储存服务**



## 使用

1. 将你的`access id`及`access key`填入`accessAccount - ex.json`中：

```json
{
	"accessId" : "**",
	"accessKey": "**",
	"endPoint" : "http://oss-cn-beijing.aliyuncs.com",
	"bucket"   : "gaolihaiimg"
}
```

2. 然后将`accessAccount - ex.json`重命名为`accessAccount.json`。

3. 运行`uploadImg.py`。
4. 输入`help`查看命令帮助。

此外，应用会启动一个线程，该线程将监听`F10`的弹起事件，当你的剪切板中有图片数据时，弹起`F10`将自动上传该图片，并自动将 Markdown 格式的图片引用文本置剪贴板。

