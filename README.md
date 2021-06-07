# Proxy as a Service - Thesis graduation project
## _CLI tool for PRaaS_
The project separated into two part, including Proxy CLI and Proxy as a Service (PRaaS) and the part here is for Proxy CLI.
Proxy CLI is a tool which use a command-line to send operations request to PRaaS. CLI use keystone api of OpenStack for authorization and authentication. So the administrator login with username and password similar as OpenStack and use menu options it provide. CLI is designed that can be installed a remote pc withc can ping to both controller and PRaaS. In thesis, it will be installed on the controller node OpenStack to satisfy the requirement. 
## Features
- Operations for PAT (creating, removing, modifying)
- Manage PAT information on project routers in OpenStack
- Change user, project in OpenStack (just support for convenience)

#### 1. Prerequisite
- Python virtual environment such as __*virtualenv*__ or __*anaconda*__. (optional)
- Python >= 2.7
#### 2. Installation

CLI use python interpreter in the current environment. Use virtual environment is a safe and low-risk aprroach for not conflicting and the virtual python interpreter will be choosen. The guide using tool python __*virtualenv*__ for creating environment. __*A recommend that if CLI and PraaS services are installed on same location so it's effective to use only one environment*__.
__Install virtualenv__
```
$ pip install virtualenv
```
__Create virtual python env__
```
$ virtualenv myenv
```
__Activate env__
```
$ source myenv/bin/activate
```
__Deactivate env__
```
$ deactivate
```
__Clone the project__
```
$ git clone https://github.com/LamNguy/cli_pat cli-praas
```
__Install packages__
```
$ cd cli-praas
$ pip install -e .
```
__If the install fail due to missing package "pbr", install it and re-run install packages__
```
$ pip install pbr
```

#### 3. Configuration
CLI is a portable tool and needing edit config file on _config/proxy_config_. File _config/clouds.yaml_ is used for testing, so ignore it.
```
# config authentication
[config]
user_domain_name = Default
project_domain_name = Default
auth_url = http://controller:5000/v3  #ip or hostname of controller
region_name = RegionOne

# config api url to PAT agent
[api]
# default PRaaS is installed on controller node because neutron server are installed on it
# if neutron l3-agent are installed on difference node, so change the url.
remove_pat = http://controller:3000/pat/remove
router_server_pat = http://controller:3000/router_server_pat
create_pat = http://controller:3000/pat/create
modify_pat = http://controller:3000/pat/modify
router_pat = http://controller:3000/router_pat
```
#### 4. Run CLI
```
$ cli-proxy
```
#### 5. Note
CLI will generate log file in the directory cli-praas directory.
