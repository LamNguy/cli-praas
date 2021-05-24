import requests
server = '192.168.20.225'
router = 'qrouter-03b72092-e8bb-473e-b671-e1dce6c4b73d'
vmport = '23'
new_vmport = '998'
gateway = '192.168.0.5'
payload = {
	'router': gateway,
	'server': server	
}
#r = requests.get('http://192.168.0.105:3000/router_vm_ports', params = payload)
#print(r.text)
#x = requests.post('http://192.168.0.105:3000/remove?server={}&router={}&vmport={}&gateway={}'.format(server,router,vmport,gateway))

l = [u'192.168.30.43', u'192.168.30.44']
string = ','.join(l)
print(string)

