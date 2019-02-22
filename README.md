# ECNU Internet Login/Logout
命令行登陆及注销华东师范大学网络验证系统<http://gateway.ecnu.edu.cn>

# 背景

* 一个ID(学号/工号)同时只能让五台设备连接外网，如果有第六台设备联网时，最先连接的那一台设备会被强制断网
* 并非所有设备都需要一直连外网
* 当某台设备一段时间没有网络流量的时候，校园网网关会断开该设备与外网的连接


# 安装

```
git clone git@gitlab.ecnu.edu.cn:Johnnychen/ecnu-net-login.git
cp ecnu-net-login/ecnu_net.py ~/.local/bin/ecnu_net
chmod +x ~/.local/bin/ecnu_net
```

# 使用

第一次使用会记录学号与密码，后面则可以自动连接

* 帮助: `ecnu_net`, `ecnu_net -h`
* 联网: `ecnu_net --login`
* 断网: `ecnu_net --logout`
* 更新参数: `ecnu_net --update`

# TODO:

- [ ] 更安全的密码存储策略
- [ ] 模块化从而在python中直接调用
- [ ] 更快的检查网络开断的工具
- [ ] `TEST_URLS`移出仓库

# F.A.Q:

* 密码明文存储在`~/.config/ecnu_net/config`下
* 能否一直联网？

    有一个临时但满足绝大部分需求的解决办法：`nohup ping www.baidu.com &`