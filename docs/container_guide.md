# Build Container for compatible version of CASA and OS

## Know the Compatibility
The information for the ALMA data cycles and the versions can restore the data with `scriptForPI.py` is on the website of [ALMA science](https://almascience.nrao.edu/processing/science-pipeline).

## Build Containers of Docker
(Take the CASA 4.7.0 and 4.3.1 as an example)
1. Install Docker
2. Browse the tabel on the website to know the compatible version of RHEL.
We can directly check the filename of the casa-release tarball.  
E.g.,  
The filename casa-release-4.7.0 of the tarball in the table: "`casa-release-4.7.0-1-el7.tar.gz`". The "`el7`" string represent the tarball is for RHEL 7.  
Normally, the corresponding version of CentOS can run the CASA as well.
3. Pull the image
We can check if the [repository](https://hub.docker.com/_/centos/tags) on DockerHub has a useable image.
```docker
# Local
docker pull [repo_name]:[tag]

docker pull centos:7.9.2009	# For CASA 4.7.0
docker pull centos:6.10		# For CASA 4.3.1
```
4. Build the container
```docker
# Local
docker run -ti --name casa470 centos:7.9.2009	# For CASA 4.7.0
docker run -ti --name casa431 centos:6.10	# For CASA 4.3.1
```
5. Construct libraries, install CASA
To know the exact libraries that we need to install, we need to repeatly execute CASA.
- **For CentOS 6** (casa-release-4.3.1)
```bash
# In Container

# Modify the repo url of metadata
cd /etc/yum.repos.d/
sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*

# Necessary update for yum
yum -y update

# Download and install CASA
yum -y install wget
wget https://casa.nrao.edu/download/distro/casa/release/el6/casa-release-4.3.1-pipe-1-el6.tar.gz
tar zxvf casa-release-4.3.1-pipe-1-el6.tar.gz

# Install library
yum -y install libpng
yum -y install freetype
yum -y install libSM
yum -y install libXi
yum -y install libXrender
yum -y install libXrandr
yum -y install libXfixes
yum -y install libXcursor
yum -y install libXinerama
yum -y install fontconfig
yum -y install libxslt

# Fix the typo of the library code in CASA
sed -i 's/pwd_module/pwd/g' /casa-release-4.3.1-pipe-el6/lib/python2.7/get_user.py
```
- **For CentOS 7**(casa-release-4.7.0)
```bash
# Container

# Necessary update for yum
yum -y update

# Download and install CASA
yum -y install wget
wget https://casa.nrao.edu/download/distro/linux/release/el7/casa-release-4.7.0-1-el7.tar.gz
tar zxvf casa-release-4.7.0-1-el7.tar.gz

# Install the Libraries
yum -y install perl
yum -y install libSM
yum -y install libX11
yum -y install libXext
yum -y install freetype
yum -y install libXi
yum -y install libXrender
yum -y install libXrandr
yum -y install libXfixes
yum -y install libXcursor
yum -y install libXinerama
yum -y install fontconfig
yum -y install libGL
```
