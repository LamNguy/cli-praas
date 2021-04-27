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
		
	# Get servers's metadata. 
	def get_servers(self):
		return [dict( index=index , name = s.name , id=s.id )  for (index,s) in enumerate(self.conn.compute.servers())]

	# Display list of servers and choose server.
	def choose_server(self):
		print('Listing servers in project')
		table = PrettyTable()
                table.field_names = ["Number", "Server name", "Server id"]

		for s in self.get_servers():
			table.add_row([s['index'], s['name'], s['id']])	
		print(table)
		choose = raw_input('Choose server name?: ')
		server = next(( s for s in self.conn.compute.servers() if s.name == choose ),None)
		if server is None:
			raise Exception('Vm not existed')
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

	# Create Port Address Translation.
	def create_pat(self):

		try:
			server = self.choose_server()
			vm_routers = self.vm_topo(server)	

			# input	
			ip = raw_input('Enter the IP of vm: ')
					
			router_name = raw_input('Enter the name of router: ')
			# interface = raw_input('Enter the interface ip of router: ')  # if you want explicit the snat, using masquerade instead of snat
			# check router
			router = next((i for i in vm_routers if i.router_name == router_name),None)		
			if router is None:
				raise Exception('Router not existed')
			else:	
				gateway = router.router_gateway.fixed_ips[0]['ip_address']
				qrouter = 'qrouter-' +router.router_id
		
				x = requests.get('http://controller:3000/router_vm_ports?router={}&server={}'.format(qrouter, ip)).json()		
				table = PrettyTable()
                		table.field_names = ["Server", "Server Ip Address", "Server Port Opened",
						     "Router Port Opened", "Router name", "Gateway"]
                		table.sortby = 'Server Port Opened'
                		for key,value in x.items():
                        		table.add_row([server.name, ip , key, value, router.router_name,gateway])
                		print(table)
			
			vmport = raw_input('Server port you want to open? ')
			y = requests.post('http://controller:3000/add?server={}&router={}&vmport={}&gateway={}'.format(ip,qrouter,vmport,gateway))
			print(y.text)
		except Exception as e:
			print(e)
		finally:
			_exit = raw_input('Press any thing to continue')

 	# modify port vm which has opened
	# querry all vm port on all router
	def modify_pat(self):

		try:
			server = self.choose_server()
	  		vm_routers = self.vm_topo(server)

			# input
			ip = raw_input('Enter the IP of vm: ')
			router_name = raw_input('Enter the name of router: ')
		
			router = next((i for i in vm_routers if i.router_name == router_name),None)			
			#if router is None:
                        #        raise Exception('Router not existed')
			#qrouter = 'qrouter-' + router.router_id
			gateway = router.router_gateway.fixed_ips[0]['ip_address']
			arr = []
			for vm_router in vm_routers:
				_qrouter = 'qrouter-' + vm_router.router_id
				x = requests.get('http://controller:3000/router_vm_ports?router={}&server={}'.format(_qrouter, ip)).json()
				arr.append(x)
                        table = PrettyTable()
                        table.field_names = ["Server", "Server Ip Address", "Server Port Opened" , "Router Port Opened", "Router name", "Gateway"]
                        table.sortby = 'Server Port Opened'
			for i in arr:
                        	for key,value in i.items():
                                	table.add_row([server.name, ip , key, value, router.router_name, gateway])
                        print(table)
		
			#vmport = raw_input('Enter port vm: ')
			#new_router_port = raw_input('Enter new router port: ')
			#remove_response = requests.post('http://controller:3000/modify?server={}&router={}&new_router_port={}&vmport={}&gateway={}'.format(ip,qrouter,new_router_port,vmport,gateway))
                        #print(remove_response.text)

		except Exception as e:
			print(e)
		finally:
			_exit = raw_input('Press any thing to continue')


	# remove port vm which has opened
	# quet tat ca cac thong tin cua router de tim vm port
	def remove_pat(self):
		
		try:
			server = self.choose_server()
                	vm_routers = self.vm_topo(server)

	                ip = raw_input('Enter the IP of vm: ')
                	router_name = raw_input('Enter the name of router: ')
               		router = next((i for i in vm_routers if i.router_name == router_name),None)		
			if router is None:
                                raise Exception('Router not existed')


			gateway = router.router_gateway.fixed_ips[0]['ip_address']
              		qrouter = 'qrouter-' + router.router_id
			
			x = requests.get('http://controller:3000/router_vm_ports?router={}&server={}'.format(qrouter, ip)).json()
                        table = PrettyTable()
                        table.field_names = ["Server", "Server Ip Address", "Server Port Opened" , "Router Port Opened", "Router name", "Gateway"]
                        table.sortby = 'Server Port Opened'
                        for key,value in x.items():
                                table.add_row([server.name, ip , key, value, router.router_name, gateway])
                        print(table)

			
                	vmport = raw_input('Enter server port you want to remove?: ')

			remove_response = requests.post('http://controller:3000/remove?server={}&router={}&vmport={}&gateway={}'.format(ip,qrouter,vmport,gateway))
			print(remove_response.text)
			

		except Exception as e:
			print(e)
		finally:
			_exit = raw_input('Press any thing to continue')
	# show instance's network topology
	def network_topo(self):
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
			print('Welcome user: [{}]\nCurrent Project: [{}]\n').format(self.conn.identity.get_user(self.conn.current_user_id).name,self.conn.current_project.name)
			print('TABLE OF OPTIONS\n1. Add Port Address Translation\n2. Modify PAT\n3. Remove PAT\n4. Router checking\n5. Server network topology\n6. Change project\n7. Change user\n8. Quit')
			choice = raw_input('Option number? ')
			switcher = {
				'1': self.create_pat,
				'2': self.modify_pat,
				'4': self.show_router_ports,
				'3': self.remove_pat,
				'5': self.network_topo,
				'6': self.change_project,
				'7': self.change_user,
				'8': self.quit 
			}
			func = switcher.get(choice,self.invalid)()

	def get_vm_name_by_ip(self,server_ip_address):
		ports = self.conn.network.ports()
       		port = next((i for i in ports if i['fixed_ips'][0]['ip_address'] == server_ip_address),None)
		if port is None:
			return 'None'
		server = self.conn.get_server_by_id(port.device_id)
		return server.name

	def show_router_ports(self):
		routers = self.conn.network.routers(project_id = self.conn.current_project_id ) 	
		print('Router list')
		for i,router in enumerate(routers):
			print('{}:{}').format(i,router.name)
		router_name = raw_input('Enter router name')
		_router_ = next(( i for i in self.conn.network.routers(project_id = self.conn.current_project_id ) if i.name == router_name),None)
		qrouter = 'qrouter-' + _router_.id
		x = requests.get('http://controller:3000/router_ports?router={}'.format(qrouter)).json()
		table = PrettyTable()
		table.field_names = ["Server", "Server IP", "Server Port", "Router Port"]
		table.sortby = 'Server'
		for key,value in x.items():
			server_name = self.get_vm_name_by_ip(key[:-3])
			table.add_row([server_name,key[:-3],key[-2:],value])
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
