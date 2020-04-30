# ECNU Internet Login/Logout
命令行登陆及注销华东师范大学网络验证系统<http://gateway.ecnu.edu.cn>

ECNU 内网及外网各提供一个版本，根据需要使用：

* `Gitlab@LFLab.ECNU`: https://gitlab.lflab.cn/lflab/ecnu-net-login
* `Github`: https://github.com/johnnychen94/ecnu-net-login

注: 当前版本因为网络测试的原因可能会出现 实际上连接上但报错的情况

# 背景

* 一个ID(学号/工号)同时只能让五台设备连接外网，如果有第六台设备联网时，最先连接的那一台设备会被强制断网
* 并非所有设备都需要一直连外网
* 当某台设备一段时间没有网络流量的时候，校园网网关会断开该设备与外网的连接


# 安装

```bash
# bash
git clone https://gitlab.lflab.cn/lflab/ecnu-net-login.git
cp ecnu-net-login/ecnu_net.py ~/.local/bin/ecnu_net
chmod +x ~/.local/bin/ecnu_net
```

# 使用

第一次使用会记录学号与密码（也可以不存储），后面则可以自动连接

* 帮助: `ecnu_net`, `ecnu_net -h`
* 联网: `ecnu_net --login`
* 断网重连: `ecnu_net --login --daemon` （需要保存账号密码）
* 断网: `ecnu_net --logout`
* 更新参数: `ecnu_net --update`

## 后台运行 daemon mode

`nohup ecnu_net --login --verbose --daemon >> ecnu_net.log 2>&1 &`

当然也可以用 tmux

或者利用systemctl部署:

```bash
# "安装" ecnu_net
git clone https://gitlab.lflab.cn/lflab/ecnu-net-login.git
cp ecnu-net-login/ecnu_net.py /usr/local/bin/ecnu_net
chmod a+x /usr/local/bin/ecnu_net

# 部署服务
cp ecnu-net-login/ecnu_net.service /lib/systemd/system/ecnu_net.service

# 开机自启动
systemctl enable ecnu_net

# 把账号密码写入配置
ecnu_net --update
# 开启服务
systemctl start ecnu_net
```

# TODO

- [ ] 更快的检查网络开断的工具 (多线程)
- [ ] register to pypi?

# F.A.Q

* 密码**明文**存储在`~/.config/ecnu_net/config`下，请确保其他人没有对此的权限
