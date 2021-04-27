import openstack
class Connection:
	def __init__ (self,config):
		self.config = config	
	def create_connection_from_config(self,user):
		return openstack.connect(cloud = user)

	def create_connection(self,username,password):
		
		user_domain_name = self.config['config']['user_domain_name']
		project_domain_name = self.config['config']['project_domain_name']
		auth_url = self.config['config']['auth_url']
		region_name = self.config['config']['region_name']
		#identity_api_version = config['config']['identity_api_version']	
		
		return openstack.connect(
                	auth_url= auth_url,
                	username= username,
                	password= password,
                	region_name= region_name,
                	user_domain_name= user_domain_name,
                	project_domain_name= project_domain_name
         	)
