from modules.utils import Utils 
from modules.connection import Connection
import openstack
from  configparser import ConfigParser
import getpass
import os
import logging


try:
	# ../cli-pat/
	current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
	if not os.path.exists(current_directory + '/logs') : 
		os.makedirs(current_directory+ '/logs')
	proxy_log_path = current_directory + '/logs/cli-proxy.log'

	formatter = logging.Formatter(
         	       '%(asctime)s - %(name)s - Level:%(levelname)s - %(message)s')
	logger = logging.getLogger('cli-proxy')
	logging.getLogger('cli-proxy').setLevel(logging.DEBUG)
	handler = logging.FileHandler(proxy_log_path, 'a')
	handler.setFormatter(formatter)
	logger.addHandler(handler)

	config_path = current_directory + '/config/proxy_config' 
	if not os.path.exists(config_path):
		raise Exception ('No configuration file')
	clouds_yaml_path = current_directory + '/config/clouds.yaml'
	if os.path.exists(clouds_yaml_path):
		os.environ['OS_CLIENT_CONFIG_FILE'] = clouds_yaml_path	
except Exception as e:
	print(e)
	os._exit(0)


def main():
	try:
		os.system('clear')
		print('----------------- CLI PROXY  ------------------')
		#username = raw_input('Username: ')
		#password = getpass.getpass('Password: ')
		username = raw_input('Username: ') 
		password = getpass.getpass('Password:') 
		openstack.enable_logging(debug=True,path= current_directory + '/logs/openstack.log',stream=None)
		config = ConfigParser()
        	config.read(config_path)
		connection = Connection(config)
		conn = connection.create_connection(username,password)
		#conn = connection.create_connection_from_config('openstack')
	
		utils = Utils(conn,config,logger)
		utils.select_option()	

	except Exception as e:
		print('The authentication failed. please re-initiate the authentication process')
		logger.error(e)
	finally:
		conn.close()

if __name__ == '__main__':
	main()
