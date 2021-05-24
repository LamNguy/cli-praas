from modules.router import Router 
import json
from prettytable import PrettyTable
import requests
import os
import time
import getpass
clear = lambda:os.system('clear')

class Utils:

	def __init__ ( self, conn,config):
		self.conn = conn
		self.select = True
		self.config = config
		
		

	def select_ip (self, server):
		if len(server.addresses) == 1:
			server_ip =  server.addresses[list(server.addresses.keys())[0]][0]['addr']	
		else:
			server_ip = raw_input('Choose interface address server? ')
			if (server.name != self.get_server_name_by_ip(server_ip)):
                        	raise Exception('Incorrect ip')
		return server_ip
	
	def select_router (self,server_routers):
		router_name = raw_input('Enter the name of router: ')
                router = next((i for i in server_routers if i.router_name == router_name),None)
		if router is None:
                	raise Exception('Router is not existed')
		return router

	# Get servers's metadata. 
	def get_servers(self):
		return [dict( index=index , name = s.name ,
			ips = [ s.addresses[i][0]['addr'] for i  in s.addresses.keys()])  for (index,s) in enumerate(self.conn.compute.servers())]

	# Display list of servers and choose server.
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
			raise Exception('Server is not existed')
		return server 
	
	# Get networks'id which belong to a server. 
	def get_server_networks(self, ports):
		return [p['net_id'] for p in ports]

	# Get routers instance which belong to a server.
	def get_server_routers(self, project_id, server_networks):

        	routers = []
        	for i in self.conn.network.routers(project_id=project_id):
                	router_interfaces = []
                	router_gateway = None

                	ports = self.conn.network.ports(device_id = i.id)
                	for p in ports:
                        	if p.device_owner == 'network:router_gateway':
                                	router_gateway = p
                        	if p.device_owner == 'network:router_interface' and (p.network_id in server_networks):
                                  	router_interfaces.append(p)
			if router_interfaces:
                		routers.append(Router(i.id,i.name,router_gateway,router_interfaces))
		return routers

	# pat information of a server on routers
	def server_pat_routers(self, server_routers, server, ip):
		
		for router in server_routers:
			table = PrettyTable()
                	table.field_names = ["Server", "Ip Address", "Server Port",
                                    	     "Router Port", "Router", "Gateway"]
			
			gateway = router.router_gateway.fixed_ips[0]['ip_address']
			payload = {
				'router': 'qrouter-' + router.router_id,
				'server': ip
			}
			url = self.config['api']['router_server_pat']
                        x = requests.get(url = url, params = payload)          
                        for key,value in x.json().iteritems():
                                table.add_row([server.name, ip , key, value, router.router_name ,gateway])
			print('Router [{}]').format(router.router_name)
                        print(table)


	# Create Port Address Translation.
	def create_pat_request(self):

		try:
			server = self.choose_server()
			server_routers = self.vm_topo(server)

			# select server ip
			ip = self.select_ip(server) 

			# show pat information of the server on the server routers.
			self.server_pat_routers(server_routers, server, ip)
			
			# select router in server routers
			router = self.select_router(server_routers)
				
			server_port = raw_input('Server port you want to open? ') 
			payload = {
			    	'server_ip': ip,
				'router_id': 'qrouter-' + router.router_id,
    				'create_server_port': server_port,
    				'gateway': router.router_gateway.fixed_ips[0]['ip_address']
			}
			url = self.config['api']['create_pat']
			create_response = requests.post(url = url, params = payload)
			print(create_response.text)
		except Exception as e:
			print(e)
		finally:
			_exit = raw_input('Press any thing to continue')

 	# modify port vm which has opened
	# querry all vm port on all router
	def modify_pat_request(self):

		try:
			server = self.choose_server()
                        server_routers = self.vm_topo(server)

                        # select server ip
                        ip = self.select_ip(server) 

                        # show pat information of the server on the server routers.
                        self.server_pat_routers(server_routers, server, ip)

                        # select router in server routers
                        router = self.select_router(server_routers)
			server_port = raw_input('Server port you want to change? ')
                        new_router_port = raw_input('Modify router port? ')

			payload = {
                                'server_ip': ip,
                                'router_id': 'qrouter-' + router.router_id,
                                'modify_server_port': server_port,
				'modify_router_port': new_router_port,
                                'gateway': router.router_gateway.fixed_ips[0]['ip_address']
                        }
	
			url = self.config['api']['modify_pat']
			modify_response = requests.post(url = url, params = payload)
                        print(modify_response.text)

		except Exception as e:
			print(e)
		finally:
			_exit = raw_input('Press any thing to continue')


	# remove port vm which has opened
	# quet tat ca cac thong tin cua router de tim vm port
	def remove_pat_request(self):
		
		try:
			server = self.choose_server()
                        server_routers = self.vm_topo(server)

                        # select server ip
                        ip = self.select_ip(server)

                        # show pat information of the server on the server routers.
                        self.server_pat_routers(server_routers, server, ip)

                        # select router in server routers
                        router = self.select_router(server_routers)

                        server_port = raw_input('Server port you want to remove? ')
			payload = {
                                'server_ip': ip,
                                'router_id': 'qrouter-' + router.router_id,
                                'remove_server_port': server_port,
                                'gateway': router.router_gateway.fixed_ips[0]['ip_address']
                        }
		
			url = self.config['api']['remove_pat']
			remove_response = requests.post(url= url, params = payload)
			print(remove_response.text)
			
		except Exception as e:
			print(e)
		finally:
			_exit = raw_input('Press any thing to continue')
	# show instance's network topology
	def server_topology(self):
		try:
			clear()
			server = self.choose_server()
			vm_routers = self.vm_topo(server)	
		except Exception as e:
			print(e)
		finally:
			_exit = raw_input('Press any thing to continue')
	# quit 
	def quit(self):
		self.select = False	

	def change_project (self):
		clear()
		print('Current project: {}').format(self.conn.current_project.name)
		print('------Projects-------')

		try:
			for i,p in enumerate(self.conn.identity.user_projects(self.conn.current_user_id)):
                                print('{}:{}').format(i,p.name)

			# input = None --> ok?
                	project = raw_input('Project name? ')
			_conn = self.conn.connect_as_project(project)
			_conn.authorize()
			self.conn = _conn
			print('Login project {} successfully').format(project)
		except Exception as e:
			print('Login project failed')
		finally:
			_exit = raw_input('Press any thing to continue')


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
			print('Login successfully')
		except Exception as e :
			print(e)
			print('Re-loggin failed')
		finally:
			_exit = raw_input('Press any thing to continue')
				
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
			print('Welcome user: [{}]\nCurrent Project: [{}]').format(
				self.conn.identity.get_user(self.conn.current_user_id).name,self.conn.current_project.name)
			print('TABLE OF OPTIONS\n1. Add PAT\n2. Modify PAT\n3. Remove PAT\n4. Manage Router PAT\n5. Server Network Topology\n6. Change project\n7. Change user\n8. Quit')
			choice = raw_input('Option number? ')
			switcher = {
				'1': self.create_pat_request,
				'2': self.modify_pat_request,
				'4': self.manage_routers_pat,
				'3': self.remove_pat_request,
				'5': self.server_topology,
				'6': self.change_project,
				'7': self.change_user,
				'8': self.quit 
			}
			func = switcher.get(choice,self.invalid)()

	# get server name by ip
	def get_server_name_by_ip(self,server_ip_address):
		ports = self.conn.network.ports()
       		port = next((i for i in ports if i['fixed_ips'][0]['ip_address'] == server_ip_address),None)
		if port is None:
			return 'Undefined'
		server = self.conn.get_server_by_id(port.device_id)
		return server.name

	def manage_routers_pat(self):
		clear()
		# list project routers 
		routers = self.conn.network.routers(project_id = self.conn.current_project_id ) 	
		
		for router in routers: 
			payload = {
				'router_id': 'qrouter-' + router.id
			}
			url = self.config['api']['router_pat']
			x = requests.get(url = url, params = payload).json()

			table = PrettyTable()
			table.field_names = ["Server", "Server IP", "Server Port", "Router Port",
				     	     "Router name", "Gateway" ]
		        table.sortby = 'Server'
			for key,value in x.items():
				server_name = self.get_server_name_by_ip(key.split(":")[0])
				table.add_row([ server_name, # server
						key.split(":")[0], # server ip
						key.split(":")[1], # serverport
						value, # router port
				      		router.name, # router name
						router.external_gateway_info['external_fixed_ips'][0]['ip_address']]) # gateway
			print('Router [{}]').format(router.name)
			print(table)
		
		_exit = raw_input('Enter anything')


	def print_topology(self,_routers, _server ):


		print('Virtual machine [{}] network topology').format(_server.name)
		topo = '* VM[{}]--------{}:{}--------if:{}-R[{}]-gw:{}--------{}:{}\n'
		for s in _routers:
                	for i in s.router_interfaces:
				# subnet ids of gateway and interfaces
                        	subnet_interface = self.conn.network.get_subnet(i.fixed_ips[0]['subnet_id'])
				net2 =  self.conn.network.get_network(subnet_interface.network_id)  # network of an interface
				subnet_gateway = self.conn.network.get_subnet(s.router_gateway.fixed_ips[0]['subnet_id'])
				net1 =  self.conn.network.get_network(subnet_gateway.network_id)  # network of gateway
                        	if net2.name in _server.addresses:
                                	fixed_ip = next((i for i in _server.addresses[net2.name] if i['OS-EXT-IPS:type'] == 'fixed'),'None')
					ips = next((i for i in self.conn.network.ips() if i.fixed_ip_address == fixed_ip['addr'] and i.router_id == s.router_id),None)
	
					if ips :
						topo1 = topo + "Server floating ip available on network {}: {}".format(net1.name,ips.floating_ip_address) + '\n'
						print(topo1).format(fixed_ip['addr'],net2.name,subnet_interface.cidr,i.fixed_ips[0]['ip_address'],s.router_name,s.router_gateway.fixed_ips[0]['ip_address'],net1.name,subnet_gateway.cidr)
					else:
                        			print(topo).format(fixed_ip['addr'],net2.name,subnet_interface.cidr,i.fixed_ips[0]['ip_address'],s.router_name,s.router_gateway.fixed_ips[0]['ip_address'],net1.name,subnet_gateway.cidr)		

	def vm_topo (self , server ):

		# get port attach to vm
		interface_server_attachments = self.conn.compute.get("/servers/{}/os-interface".format(server.id)).json()['interfaceAttachments']
		# get netword_id which ports belongs
                server_networks = self.get_server_networks(interface_server_attachments)
		# get project id 
                project_id = self.conn.current_project.id 
		# get vm_router link
                vm_routers = self.get_server_routers(project_id, server_networks)
		
		clear()
                self.print_topology(vm_routers,server)
		return vm_routers
