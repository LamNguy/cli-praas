from modules.utils import Utils 
from modules.connection import Connection
import openstack
from  configparser import ConfigParser
import getpass
import os
import logging

formatter = logging.Formatter(
                '%(asctime)s - %(name)s - Level:%(levelname)s - %(message)s')
logger = logging.getLogger('cli-proxy')
logging.getLogger('cli-proxy').setLevel(logging.DEBUG)
filename = os.getcwd() + '/log/cli-proxy.log'
handler = logging.FileHandler(filename, 'a')
handler.setFormatter(formatter)
logger.addHandler(handler)


cfg = os.getcwd()+ '/config'
os.system('clear')

try:
	print('----------------- CLI PROXY  ------------------')
	username = raw_input('Username: ')
	password = getpass.getpass('Password: ')
	openstack.enable_logging(debug=True,path=os.getcwd() + '/log/openstack.log',stream=None)
	config = ConfigParser()
        config.read(cfg)

	connection = Connection(config)
	conn = connection.create_connection(username,password)
	#conn = connection.create_connection_from_config('openstack')
	
	conn.authorize()	
	utils = Utils(conn,config,logger)
	utils.select_option()	

except Exception as e:
	print('The authentication failed. please re-initiate the authentication process')
	logger.error(e)
finally:
	conn.close()
