from modules.router import Router 
import json
from prettytable import PrettyTable
import requests
import os
import time
import getpass
from pick import pick
clear = lambda:os.system('clear')

class Utils:

	def __init__ ( self, conn, config, logger):
		self.conn = conn
		self.select = True
		self.config = config
		self.logger = logger

	def check_port ( self, port ):
		assert isinstance(int(port), int), 'Input wrong type!'
                assert int(port) in range (1,65535), 'Invalid value range, allowed is (1,65535)'

		
	# Select server ip address, if server has only one nic, auto assign this ip instead of selecting
	def select_ip (self, server):
		if len(server.addresses) == 1:
			server_ip =  server.addresses[list(server.addresses.keys())[0]][0]['addr']	
		else:
			server_ips = [ server.addresses[i][0]['addr'] for i  in server.addresses.keys()]
			x = raw_input('Since your server has more than one NIC, press Enter to continue')
			title = 'Choose server interface address'
                                    
                        server_ip , index = pick(server_ips, title)
			#if (server.name != self.get_server_name_by_ip(server_ip)):
                        #	raise Exception('Incorrect ip')
		return server_ip

	# Select router, if server is associated with only one router, auto assign this router instead of selecting
	def select_router (self,server_routers, server_name):
		if len(server_routers) == 0 :
			raise Exception ('Can not detect router for server {}'.format(server_name))
		elif len(server_routers) == 1:
			return server_routers[0]
		else:
			title = 'Choose server interface address'
			options = [ i.router_name for i in server_routers ]
			x = raw_input('Since there are more than one router, press Enter to continue')
                        router , index = pick(options , title)	
			#router_name = raw_input('Enter the name of router: ')
                	#router = next((i for i in server_routers if i.router_name == router_name),None)
			#if router is None:
                	#	raise Exception('Router is not existed')
			return server_routers[index] 

	# Get servers's metadata [ index, name, ips ] 
	def get_servers(self):
		return [dict( index=index , name = s.name ,
			ips = [ s.addresses[i][0]['addr'] for i  in s.addresses.keys()])  for (index,s) in enumerate(self.conn.compute.servers())]

	# List servers in project and choose specific server.
	def choose_server(self):
		print('Listing servers in project')
		table = PrettyTable()
                table.field_names = ["Number", "Server name", "Server ip"]

		for s in self.get_servers():
			table.add_row([s['index'], s['name'], ','.join(s['ips'])])	
		print(table)
		choose = raw_input('Choose server name?: ')
		server = next(( s for s in self.conn.compute.servers() if s.name == choose ),None)
		if server is None:
			raise Exception('Server {} is not existed'.format(choose))
		return server 
	
	# Get server networks id from its port attachment 
	def get_server_networks(self, server_id ):
		interface_server_attachments = self.conn.compute.get("/servers/{}/os-interface".format(server_id)).json()['interfaceAttachments']
		return [p['net_id'] for p in interface_server_attachments]

	# Get routers associated to a server.
	def get_server_routers(self, server ):
		
		# get server networks
		server_networks = self.get_server_networks(server.id)
        	routers = []
        	for i in self.conn.network.routers(project_id= self.conn.current_project.id ):
                	router_interfaces = []
                	router_gateway = None

                	ports = self.conn.network.ports(device_id = i.id)
                	for p in ports:
                        	if p.device_owner == 'network:router_gateway':
                                	router_gateway = p
                        	elif p.device_owner == 'network:router_interface' and (p.network_id in server_networks):
                                  	router_interfaces.append(p)
			if router_interfaces:
                		routers.append(Router(i.id,i.name,router_gateway,router_interfaces))
		return routers

	# pat information of a server on routers
	def server_pat_routers(self, server_routers, server, ip):
		
		for router in server_routers:
			table = PrettyTable()
                	table.field_names = ["Server", "Ip Address", "Server Port","Router Port", "Gateway"]
			
			gateway = router.router_gateway.fixed_ips[0]['ip_address']
			payload = {
				'router_id': 'qrouter-' + router.router_id,
				'server_ip': ip
			}
			url = self.config['api']['router_server_pat']
                        x = requests.get(url = url, params = payload)          
			self.logger.info('server_pat_routers with params {}'.format(payload))
                        for key,value in x.json().iteritems():
                                table.add_row([server.name, ip , key, value, gateway])
			print('Router [{}]').format(router.router_name)
                        print(table)


	# Create Port Address Translation.
	def create_pat_request(self):

		try:
			server = self.choose_server()
			self.server_topo(server)
			server_routers = self.get_server_routers( server )
			# select server ip
			ip = self.select_ip(server) 
			print('Your nic address is {}').format(ip)

			# show pat information of the server on the server routers.
			self.server_pat_routers(server_routers, server, ip)
			
			# select router in server routers
			router = self.select_router(server_routers, server.name)
				
			server_port = raw_input('Server port you want to open? ') 
			self.check_port(server_port)
			payload = {
			    	'server_ip': ip,
				'router_id': 'qrouter-' + router.router_id,
    				'create_server_port': server_port,
    				'gateway': router.router_gateway.fixed_ips[0]['ip_address']
			}
			url = self.config['api']['create_pat']
			
			create_response = requests.post(url = url, params = payload).json()	
			self.logger.debug('Create pat request with params {}'.format(payload))
			table = PrettyTable()
                        table.field_names = ["Status", "Server", "Server Port", "Router Port", "Gateway","Description"]
			if create_response['status'] == 'SUCCESS':
				 
                                table.add_row([ create_response['status'], 
                                                create_response['server_ip'], 
                                                create_response['create_server_port'], 
                                                create_response['create_router_port'],
						create_response['gateway'],
						create_response['message']])

			elif create_response['status'] == 'CREATED':
				table.add_row([ create_response['status'], 
                                                create_response['server_ip'], 
                                                create_response['created_server_port'], 
                                                create_response['created_router_port'],
                                                create_response['gateway'],
						create_response['message']])	
			elif create_response['status'] == 'ERROR':
				table.add_row([ create_response['status'] , "", "", "", "", create_response['message']])

			print(table)
			
		except Exception as e:
			self.logger.error(e)	
			print(e)
		finally:
			_exit = raw_input('Press Enter to exit')

 	# modify port vm which has opened
	# querry all vm port on all router
	def modify_pat_request(self):

		try:
			server = self.choose_server()
			self.server_topo(server)
                        server_routers = self.get_server_routers( server )

                        # select server ip
                        ip = self.select_ip(server) 

                        # show pat information of the server on the server routers.
                        self.server_pat_routers(server_routers, server, ip)

                        # select router in server routers
                        router = self.select_router(server_routers, server.name)
			
			server_port = input('Server port you want to change? ')
			self.check_port(server_port)
                        new_router_port = input('Modify router port? ')
			self.check_port(new_router_port)
			#assert isinstance(int(new_router_port), int), 'Argument of wrong type!'

			payload = {
                                'server_ip': ip,
                                'router_id': 'qrouter-' + router.router_id,
                                'modify_server_port': server_port,
				'modify_router_port': new_router_port,
                                'gateway': router.router_gateway.fixed_ips[0]['ip_address']
                        }
	
			url = self.config['api']['modify_pat']
			modify_response = requests.post(url = url, params = payload).json()
			self.logger.debug('modify request pat with params: {}'.format(payload))
			table = PrettyTable()
                        table.field_names = ["Status", "Server", "Server Port", "Old Router Port",'New Router Port', "Gateway", "Description"]
                        if modify_response['status'] == 'NO CREATED':

                               table.add_row([  modify_response['status'],
                                                modify_response['server_ip'],
                                                modify_response['modify_server_port'],
                                                "",
						"",
                                                modify_response['gateway'],
						modify_response['message']])
                        elif modify_response['status'] == 'USED':
                                table.add_row([ modify_response['status'],
                                                modify_response['server_ip'],
                                                modify_response['modify_server_port'],
						modify_response['modified_router_port'],
						"",
                                                modify_response['gateway'],
						modify_response['message']])
			elif modify_response['status'] == 'SUCCESS':
                                table.add_row([ modify_response['status'],
                                                modify_response['server_ip'],
                                                modify_response['modify_server_port'],
						modify_response['modified_router_port'],
						modify_response['modify_router_port'],
                                                modify_response['gateway'],
						modify_response['message']])
			elif remove_response['status'] == 'ERROR':
                                table.add_row([ modify_response['status'] , "", "", "", "", modify_response['message']])
			
                        print(table)

		except Exception as e:
			print(e)
			self.logger.error(e)
		finally:
			_exit = raw_input('Press Enter to exit')


	# remove port vm which has opened
	# quet tat ca cac thong tin cua router de tim vm port
	def remove_pat_request(self):
		
		try:
			server = self.choose_server()
			self.server_topo(server)
                        server_routers = self.get_server_routers( server )

                        # select server ip
                        ip = self.select_ip(server)

                        # show pat information of the server on the server routers.
                        self.server_pat_routers(server_routers, server, ip)

                        # select router in server routers
                        router = self.select_router(server_routers, server.name)
			

                        server_port = input('Server port you want to remove? ')
			self.check_port(server_port)
                        #assert isinstance(int(server_port), int), 'Argument of wrong type!'
			payload = {
                                'server_ip': ip,
                                'router_id': 'qrouter-' + router.router_id,
                                'remove_server_port': server_port,
                                'gateway': router.router_gateway.fixed_ips[0]['ip_address']
                        }
		
			url = self.config['api']['remove_pat']
			remove_response = requests.post(url= url, params = payload).json()
			self.logger.debug('remove pat request with params {}'.format(payload))
			table = PrettyTable()
                        table.field_names = ["Status", "Server", "Server Port", "Router Port", "Gateway","Description"]
                        if remove_response['status'] == 'REMOVED':

                               table.add_row([  remove_response['status'],
                                                remove_response['server_ip'],
                                                remove_response['remove_server_port'],
                                                remove_response['remove_router_port'],
                                                remove_response['gateway'],
						remove_response['message']])
                        elif remove_response['status'] == 'NO CREATED':
                                table.add_row([ remove_response['status'],
                                                remove_response['server_ip'],
                                                remove_response['remove_server_port'],
                                                "",
                                                remove_response['gateway'],
						remove_response['message']])
			elif remove_response['status'] == 'ERROR':
                                table.add_row([ remove_response['status'] , "", "", "", "", remove_response['message']])
                        print(table)
			
		except Exception as e:
			print(e)
			self.logger.error(e)
		finally:
			_exit = raw_input('Press Enter to exit')
	# show instance's network topology

	#def server_topology(self):
	#	try:
	#		clear()
	#		server = self.choose_server()
	#		x = self.server_topo(server)	
	#	except Exception as e:
	#		print(e)
	#	finally:
	#		_exit = raw_input('Press Enter to exit')

	def server_topo(self, server ):

		clear()
	        topo_without_ips  = '* VM[{}]--------{}:{}--------if:{}-R[{}]-gw:{}--------{}:{}\n'
		topo_with_ips = topo_without_ips +  "Server floating ip available on network {}: {}\n"
		server_routers = self.get_server_routers( server )
                print('Server [{}] network topology').format( server.name )
                for s in server_routers:
                        for i in s.router_interfaces:
                        	# get a couple (interface_net, gateway_net), if router does not have interfaces or gateway --> fail
		
                                subnet_interface = self.conn.network.get_subnet(i.fixed_ips[0]['subnet_id'])
                                interface_network =  self.conn.network.get_network(subnet_interface.network_id)  # network of an interface
                                subnet_gateway = self.conn.network.get_subnet(s.router_gateway.fixed_ips[0]['subnet_id'])
                                gateway_network =  self.conn.network.get_network(subnet_gateway.network_id)  # network of gateway
					
				# check if interface_net belong to server networks
                                if interface_network.name in server.addresses:
					# get server's ip on this interface_net	
                                        fixed_ip = next((i for i in server.addresses[interface_network.name] if i['OS-EXT-IPS:type'] == 'fixed'),'None')
					# check server's ip on this interface_net has a floating ip
                                        ips = next((i for i in self.conn.network.ips() if i.fixed_ip_address == fixed_ip['addr'] and i.router_id == s.router_id),None)

                                        if ips :
                                                print(topo_with_ips).format( fixed_ip['addr'],
									interface_network.name,
									subnet_interface.cidr,
									i.fixed_ips[0]['ip_address'],
									s.router_name,
									s.router_gateway.fixed_ips[0]['ip_address'],
									gateway_network.name,
									subnet_gateway.cidr)
                                        else:
                                                print(topo_without_ips).format( fixed_ip['addr'],
									interface_network.name,
									subnet_interface.cidr,
									i.fixed_ips[0]['ip_address'],
									s.router_name,
									s.router_gateway.fixed_ips[0]['ip_address'],
									gateway_network.name,
									subnet_gateway.cidr)
	# quit 
	def quit(self):
		self.select = False	

	def change_project (self):
		clear()
		title = 'Current project: {}\nChoose project below:'.format(self.conn.current_project.name)  

		try:
			options = [ p.name for p in self.conn.identity.user_projects(self.conn.current_user_id)]
			project, index = pick(options, title)
			self.logger.info('Change to project {}'.format(project))
			_conn = self.conn.connect_as_project(project)
			_conn.authorize()
			self.conn = _conn
		except Exception as e:
			self.logger.error(e)	


	# re-login with another user
	def change_user(self):
		clear()
		user = self.conn.identity.get_user(self.conn.current_user_id)
		
		print('You are logging with user: {}').format(user.name)
		
		username = raw_input('Username: ')
		password = getpass.getpass('Password: ')
		try:
			_conn = self.conn.connect_as(username=username, password=password)
			_conn.authorize()
			self.conn = _conn
			self.logger.info('Relogin with user {}'.format(username))
			print('Login successfully')
		except Exception as e :
			print('Login fail')
			self.logger.error(e)
		finally:
			_exit = raw_input('Press Enter to continue')
				
	# invalid option
	def invalid (self):
		clear()
		print('Invalid choice')
		time.sleep(2)

	def select_option (self):
		
		if self.conn.current_project.name is None:
			self.change_project()
		while self.select:
			clear()
			#print('Welcome user: [{}]\nCurrent Project: [{}]').format(
			#	self.conn.identity.get_user(self.conn.current_user_id).name,self.conn.current_project.name)
			#print('TABLE OF OPTIONS\n1. Add PAT\n2. Modify PAT\n3. Remove PAT\n4. Manage Router PAT\n5. Server Network Topology\n6. Change project\n7. Change user\n8. Quit')
			title = 'Welcome user: [{}]\nCurrent Project: [{}]'.format(self.conn.identity.get_user(self.conn.current_user_id).name,self.conn.current_project.name)
			options = [ '1. Add PAT' , '2. Modify PAT', '3. Remove PAT','4. Manage Router PAT',
				    '5. Change project', '6. Change user', '7. Quit' ]
			option, index = pick(options, title)
			switcher = {
				'1': self.create_pat_request,
				'2': self.modify_pat_request,
				'4': self.manage_routers_pat_request,
				'3': self.remove_pat_request,
				#'5': self.server_topology,
				'5': self.change_project,
				'6': self.change_user,
				'7': self.quit 
			}
			func = switcher.get(str(index+1),self.invalid)()

	# get server name by ip
	def get_server_name_by_ip(self,server_ip_address):
		ports = self.conn.network.ports()
       		port = next((i for i in ports if i['fixed_ips'][0]['ip_address'] == server_ip_address),None)
		if port is None:
			return 'Undefined'
		server = self.conn.get_server_by_id(port.device_id)
		return server.name


	def magic (self, options):
		return options.get('name')
	def manage_routers_pat_request(self):
		clear()
		# list project routers 
		try:
			routers = self.conn.network.routers(project_id = self.conn.current_project_id ) 	
			
			title = 'List router in project'

                        options = [ {'name':p.name, 'id':p.id , 
				'gateway': p.external_gateway_info['external_fixed_ips'][0]['ip_address']}  for p in routers ]
                        router , index = pick(options, title, options_map_func = self.magic)
			
			payload = {
				'router_id': 'qrouter-' + router['id']
			}

			url = self.config['api']['router_pat']
			x = requests.get(url = url, params = payload).json()
			self.logger.debug('manage routers pat request on router {}'.format(payload))
			table = PrettyTable()
			table.field_names = ["Server", "Server IP", "Server Port", "Router Port", "Gateway" ]
		        table.sortby = 'Server'
			for key,value in x.items():
				server_name = self.get_server_name_by_ip(key.split(":")[0])
				table.add_row([ server_name, # server
						key.split(":")[0], # server ip
						key.split(":")[1], # serverport
						value, # router port
						router['gateway']]) # gateway
			print('Router [{}]').format(router['name'])
			print(table)
		except Exception as e:
			self.logger.info(e)
		finally:
			_exit = raw_input('Press Enter to exit')

