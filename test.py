import requests
server = '192.168.20.225'
router = 'qrouter-03b72092-e8bb-473e-b671-e1dce6c4b73d'
vmport = '23'
new_vmport = '998'
gateway = '192.168.0.5'
x = requests.post('http://192.168.0.105:3000/modify?server={}&router={}&vmport={}&new_vmport={}&gateway={}'.format(server,router,vmport,new_vmport,gateway))
#x = requests.post('http://192.168.0.105:3000/remove?server={}&router={}&vmport={}&gateway={}'.format(server,router,vmport,gateway))
print(x.text)

