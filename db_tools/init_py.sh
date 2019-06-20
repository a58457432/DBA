#!/bin/bash
#
#init py3.7

dir='/usr/local/webserver/software/'
wget_cmd=`which wget`
curl_cmd=`which curl`
ls_cmd=`which ls`
py_init='https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tgz'
py_pkg='Python-3.7.3.tgz'
py_dir='Python-3.7.3'
hcode=`$curl_cmd -I -m 10 -o /dev/null -s -w %{http_code} www.baidu.com`
pip_init='https://files.pythonhosted.org/packages/93/ab/f86b61bef7ab14909bd7ec3cd2178feb0a1c86d451bc9bccd5a1aedcde5f/pip-19.1.1.tar.gz'
pip_pkg='pip-19.1.1.tar.gz'
pip_dir='pip-19.1.1'

init_py(){
yum install libffi-devel -y 
mkdir -p $dir
cd $dir
if [[ $hcode == 200 ]];then
	$wget_cmd -c $py_init
	$wget_cmd -c $pip_init
	if [[ `$ls_cmd $dir$py_pkg |wc -l` == 1 ]];then
		echo 'py download sucesss'
		# tar py
		tar  -xzf $py_pkg
		tar  -xzf $pip_pkg
		cd $py_dir
		./configure
		make && make install
		rm /usr/bin/python -f
		ln -s /usr/local/bin/python3.7 /usr/bin/python
		sed -i 's/python/python2.7/g'  /usr/bin/yum
		sed -i 's/python/python2.7/g'  /usr/libexec/urlgrabber-ext-down	

		cd $dir$pip_dir
		python setup.py install
	fi
else
	echo 'out network is lose'
fi 

}

init_py
