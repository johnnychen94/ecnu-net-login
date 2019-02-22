# ECNU Internet Login/Logout
命令行登陆及注销华东师范大学网络验证系统<http://gateway.ecnu.edu.cn>

# 背景

* 一个ID(学号/工号)同时只能让五台设备连接外网，如果有第六台设备联网时，最先连接的那一台设备会被强制断网
* 并非所有设备都需要一直连外网
* 当某台设备一段时间没有网络流量的时候，校园网网关会断开该设备与外网的连接


# 安装

```
git clone git@gitlab.ecnu.edu.cn:Johnnychen/ecnu-net-login.git
cp ecnu-net-login/ecnu-net.py ~/.local/bin/ecnu-net
chmod +x ~/.local/bin/ecnu-net
```

# 使用

第一次使用会记录学号与密码，后面则可以自动连接

* 帮助: `ecnu-net`, `ecnu-net -h`
* 联网: `ecnu-net --login`
* 断网: `ecnu-net --logout`

# TODO:

- [ ] 以参数的形式传递密码
- [ ] 更安全的密码存储策略
- [ ] 功能：更新配置文件
- [ ] 模块化从而在python中直接调用

# F.A.Q:

* 密码明文存储在~/.config/ECNU-net/config下
* 能否一直联网？

    有一个临时但满足绝大部分需求的解决办法：`nohup ping www.baidu.com &`