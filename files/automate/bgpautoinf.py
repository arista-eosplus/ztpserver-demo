import os, sys, re, time 
from jsonrpclib import Server

SWITCH_IP = 'localhost'
USERNAME = 'admin'
PASSWORD = 'admin'
ETHERNET_RE = re.compile(r'Interface (Ethernet[\d+|/])\s+.*')

switch = Server( 'https://%s:%s@%s/command-api' % 
                 ( USERNAME, PASSWORD, SWITCH_IP ) )

response = switch.runCmds( 1, [ 'show lldp neighbors detail' ], 'text')

def lldpparser(data):
    neighbors = dict()
    for entry in data.split('\n'):
        match = ETHERNET_RE.match(entry)
        if match:
            token = match.group(1)
            ipaddr = None
        
        if entry.strip().startswith('- Port Description'):
            description = entry.split(': ')[1]
            if ":" in description:
              ipaddr = description.split(':')[1].replace('"', '')
      
        if token and ipaddr is not None:
            neighbors[token] = ipaddr
    return neighbors

neighborInfo = response[ 0 ][ 'output' ]
neighbors = lldpparser(neighborInfo)

def main():
   while True:
       response = switch.runCmds( 1, [ 'show lldp neighbors detail' ], 'text')
       neighborInfo = response[ 0 ][ 'output' ]
       neighbors = lldpparser(neighborInfo)
       for k, v in neighbors.items():
          rc = switch.runCmds( 1, [ 'enable',
                          'configure',
                          'interface %s' % ( k ),
                          'ip address %s/31' % ( v ) ] )
       time.sleep(30)

if __name__ == '__main__':
   main()
