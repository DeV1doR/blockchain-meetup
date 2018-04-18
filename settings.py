import json

NODE_URL = 'http://localhost:8545'

ACTIVATOR_ADDRESS = '0x0716416a52dbb014be680fd6f0748717d3668f73'
ACTIVATOR_ABI = json.loads('[{"constant":false,"inputs":[],"name":"unreg","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"note","type":"bytes32"}],"name":"reg","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"userExist","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getNote","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[{"name":"_limit","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"name":"","type":"bytes32"}],"name":"Error","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"","type":"bytes32"}],"name":"Success","type":"event"}]')

SENDER_ADDRESS = '0xad43a314ab316cfea09d1d464a9dba1b62acf963'
SENDER_PK = 'ab17ca9b5300e0a569f4f8e077eae1581c965daf0e19d5df1763b23a1c1605a2'
