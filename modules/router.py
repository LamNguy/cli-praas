class Router:
	def __init__ ( self, router_id, router_name , router_gateway , router_interfaces ):
		self.router_name = router_name
		self.router_id = router_id
		self.router_gateway = router_gateway
		self.router_interfaces = router_interfaces
		self.router_table = None
	
