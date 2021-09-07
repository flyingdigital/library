###  写在前头

- 介绍

  这个项目是自动预约长江大学东区图书馆座位的一个小爬虫。使用了`Appium`框架(使用时需要连接**安卓手机**且需要打开手机开发者模式)。可以自动预约有空余两小时的座位。对特定的楼层有判断，优先选择好的座位。

- 需要准备的其他环境

  - [JDK1.8]([https://www.oracle.com/java/technologies/javase-downloads.html](https://link.zhihu.com/?target=https%3A//www.oracle.com/java/technologies/javase-downloads.html))
  - [SDK]([https://www.oracle.com/java/technologies/javase-downloads.html](https://link.zhihu.com/?target=https%3A//www.oracle.com/java/technologies/javase-downloads.html))
  - [Appium_Desktop](https://link.zhihu.com/?target=https%3A//github.com/appium/appium-desktop/releases)

  具体如何安装请百度。

- 安装需要的Python第三方库

  ```
  pip install -r requirements.txt
  ```

  

### 注意

#### 运行前的准备

1. 手机必须要打开开发者模式 
2. appium配置
   1. 我本人手机微信的chromedriver版本为`77.0.3865`，与我不同的请下载修改程序`getCookie() desired_caps chromedriverExecutable `为自己手机微信对应版本的chromedriver路径。
   2. 同样是 `desired_caps` 请将其中的`platformVersion`修改为自己的安卓版本。
3. 请启动Appium_Desktop，启动Appium服务
4. 手机要预先关注**长江大学图书馆**公众号
5. 用户需要预先将微信号与借书证进行绑定



### 小总结

#### 缺点

1. 手机自动化的时候必须要先关注**长江大学图书馆**的公众号，这里没做判断。
2. 没有判断用户是否已经预约。
3. 用户无法选择。

#### 可以扩展的地方

1. 可以分时获取图书馆作为数据，并统计改数据，分析哪一个时间段人最少。
2. 同理座位也一样。可以分析哪个地方座位最抢手。
3. 完善界面，给用户选择学习时常(按这个找位子)，希望的楼层等等。

#### 为什么我使用了Appium

由于图书馆的网页端登录验证实在是坑，他的验证我尝试过现成的一些OCR库、现成的接口(百度、腾讯文字识别等等)，要么就是没有识别到图片文字，要么就是识别不全，要么识别错误(据说使用CNN和yolo可以解决，但我没有尝试)。实在没办法，一拍脑袋转成了手机登录，但后获取其cookie，只要获取了cookie我就可以办事了。遂有了Appium。



程序写的不太好，望多多包涵。

若有更好的办法希望邮件联系(zhao_qian123@outlook.com)，万分感谢。



#### 停止维护！！！！   项目可能无法正常运行！！！  仅提供思路！！！