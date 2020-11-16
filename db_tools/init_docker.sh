#!/bin/bash
#
#init docker

dir='/usr/local/webserver/software/'
docker_dir='/etc/docker'
docker_file='/etc/docker/deamon.json'


init_docker(){
yum remove docker  docker-client  docker-client-latest  docker-common  docker-latest  docker-latest-logrotate  docker-logrotate  docker-selinux  docker-engine-selinux  docker-engine docker-ce -y
rm -rf /var/lib/docker
yum install -y yum-utils device-mapper-persistent-data lvm2
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

mkdir -p $docker_dir

if [ -e $docker_file ]; then
echo "docker file exist!"
else
touch $docker_dir
fi

cat >> $docker_file << EOF
{
    "registry-mirrors": [
            "http://hub-mirror.c.163.com"
    ]
}
EOF

systemctl daemon-reload
yum install docker-ce docker-ce-cli containerd.io
systemctl start docker
systemctl enable docker
}

init_docker
