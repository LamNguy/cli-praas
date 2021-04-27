from modules.utils import Utils 
from modules.connection import Connection
import openstack
from  configparser import ConfigParser
import getpass
import os

os.system('clear')
print('----------------- PAT CLI ------------------')
username = raw_input('Username: ')
password = getpass.getpass('Password: ')
cfg = os.getcwd()+ '/config'

try:
	openstack.enable_logging(debug=True,path='openstack.log',stream=None)
	config = ConfigParser()
        config.read(cfg)

	connection = Connection(config)
	conn = connection.create_connection(username,password)
	#conn = connection.create_connection_from_config('openstack')
	
	conn.authorize()	
	utils = Utils(conn,config)
	utils.select_option()	

except Exception as e:
	print(e)
finally:
	conn.close()
