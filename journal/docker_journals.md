# Docker Records
## Building containers
|CASA Version|Tried image|Status|Description|
|:----------:|----------:|:-----|:----------|
|4.2.2|centos:6.10|Succeed||
|4.3.1|centos:6.10|Succeed||
|4.5.1|centos:6.10|Succeed||
|4.5.2|centos:6.10|Succeed||
|4.5.3|centos:6.10|Succeed||
|4.7.0|centos:7.3.1611|Succeed||
|4.7.2|centos:7.3.1611|Succeed||
|5.1.1|centos:7.4.1708|Succeed||
|5.4.0|centos:7.5.1804|Libraries installed, exist module error|`failed to load casa: No module named _atmosphere`|
|5.6.1|centos:7.7.1908|Libraries installed, exist module error|`failed to load casa: No module named _atmosphere`|

- images cannot use directly and their issues:  

|image     |Issue description|
|:--------:|:----------------|
|centos:6.6|the yum cannot be update properly|
|centos:6.7|the yum cannot be update properly|


## Utilize the docker container, images and tar.gz file
1. Save an image to a tar.gz file using gzip
```bash
docker save [repository[:tag]] | gzip > [filename].tar.gz
```
3. Load an image from the STDIN
```bash
docker load < [filename].tar.gz
```


### Tips for solving issues: 
1. `Error: Failed to download metadata for repo ‘appstream’: Cannot prepare internal mirrorlist`:  
```bash
cd /etc/yum.repos.d/
sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*
```
2. `docker: Error response from daemon: no command specified.`
(solved for centos:6.6)  
https://blog.csdn.net/shenghuiping2001/article/details/93378185  
The reason is because the image configuration file does not includes the necessary command.  
Solution:  
When initializing the container:
```bash
docker run -it --name [container_name] [image:tag] [command]

docker run -it --name docker_casa422-1 "/bin/bash"
```
3. `NameError: global name 'pwd_module' is not defined` for CASA 4.2.2, 4.3.1
Dive into the `/[CASA_dir]/lib64/python2.7/get_user.py`.  
Modify the `pwd_module` in line 20 into `pwd`.
