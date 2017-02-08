




# This application is used to discovery the pyhsical disk by using the MegaCLI tool.
https://gist.github.com/AlexYangYu/14161ce866417f817508

https://gist.github.com/magictour/540919c76f452f2761a037c0d91366b2



http://www.cnblogs.com/alexyang8/





Include=/etc/zabbix/zabbix_agentd.conf.d/
UnsafeUserParameters=1



# /etc/zabbix/zabbix_agentd.conf.d/disk.conf

UserParameter=raid.phy.discovery,sudo /opt/DiskMonitoring/raid.py pd_discovery
UserParameter=raid.phy.mec[*],sudo /opt/DiskMonitoring/raid.py mec $1
UserParameter=raid.phy.oec[*],sudo /opt/DiskMonitoring/raid.py oec $1
UserParameter=raid.phy.pfc[*],sudo /opt/DiskMonitoring/raid.py pfc $1











