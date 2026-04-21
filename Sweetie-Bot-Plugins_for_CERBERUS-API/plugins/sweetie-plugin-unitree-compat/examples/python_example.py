from sweetie_plugin_sdk.client import SweetiePluginClient
client = SweetiePluginClient('http://localhost:7101')
print(client.health())
print(client.execute('robot.command', {'action':'walk','direction':'forward','speed':0.3,'duration':1.5}))
