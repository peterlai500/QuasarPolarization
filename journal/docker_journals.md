# 2024 June 06
## Building containers
|CASA Version|Tried image|Status|Description|
|:----------:|----------:|:-----|:----------|
|4.2.2|centos:6.10|Libraries installed, exist import error|`NameError: global name 'pwd_module' is not defined`|
|     |centos:6.6 |failed|container cannot run properly|
|4.3.1|centos:6.10|Libraries installed, exist import error|`NameError: global name 'pwd_module' is not defined`|
|     |centos:6.7 |failed|cannot update yum|
|4.5.1|centos:6.10|Success||
|4.5.2|centos:6.10|Success||
|4.5.3|centos:6.10|Success||
|4.7.0|centos:7.3.1611|trying|updating yum|
|4.7.2|centos:7.3.1611|trying|updating yum|
|||||
## Utilize the docker container, images and tar.gz file
1. Commit a container to image
```bash
docker commit [contianer_id] [repository[:tag]]
```
2. Save an image to a tar.gz file using gzip
```bash
docker save [repository[:tag]] | gzip > [filename].tar.gz
```
3. Load an image from the STDIN
```bash
docker load < [filename].tar.gz
```


- tips for solve the issue: 
1. `Error: Failed to download metadata for repo ‘appstream’: Cannot prepare internal mirrorlist`:  
```bash
cd /etc/yum.repos.d/
sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*
```
2. `docker: Error response from daemon: no command specified.`
(not solved yet for centos:6.6 for 4.2.2)  
https://blog.csdn.net/shenghuiping2001/article/details/93378185

