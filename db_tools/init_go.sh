#!/bin/bash
#
#init go
#wget https://raw.githubusercontent.com/pote/gpm/v1.4.0/bin/gpm --no-check-certificate && chmod +x gpm && sudo mv gpm /usr/local/bin

dir='/usr/local/webserver/software/'
wget_cmd=`which wget`
curl_cmd=`which curl`
ls_cmd=`which ls`
#go_init='https://dl.google.com/go/go1.12.6.linux-amd64.tar.gz'
go_init='https://dl.google.com/go/go1.15.7.linux-amd64.tar.gz'
go_pkg='go1.15.7.linux-amd64.tar.gz'
hcode=`$curl_cmd -I -m 10 -o /dev/null -s -w %{http_code} www.baidu.com`

init_go(){
mkdir -p $dir
cd $dir
if [[ $hcode == 200 ]];then
	$wget_cmd -c $go_init
	if [[ `$ls_cmd $dir$go_pkg |wc -l` == 1 ]];then
		echo 'go download sucesss'
		tar -C /usr/local/ -xzf $go_pkg
		mkdir -p /usr/local/go/workspace
		echo 'export GOROOT=/usr/local/go' >> /root/.bash_profile
		echo 'export GOPATH=/usr/local/go/workspace' >> /root/.bash_profile
		echo 'export PATH=$PATH:/usr/local/go/bin' >> /root/.bash_profile
	fi
else
	echo 'out network is lose'
fi 

}

init_go
source /root/.bash_profile
