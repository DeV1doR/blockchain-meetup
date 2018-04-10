NODE=geth
ROOT_DIR=node_db
DATADIR1=./$(ROOT_DIR)/testnet
KEYSTORE1=$(DATADIR1)/keystore
LOG_FILE1=$(DATADIR1)/info.log
IPC_FILE1=$(DATADIR1)/geth.ipc
PID_FILE1=$(DATADIR1)/run.pid
PSWD_FILE=./$(ROOT_DIR)/pswd.txt
PSWD=$(shell cat $(PSWD_FILE))
JS_FILE=./$(ROOT_DIR)/utils.js
AMOUNT=1

NODE_PORT = 30305
RPC_PORT = 8545

BASE_ARGS=--dev \
	--nodiscover \
	--networkid=15 \
	--maxpeers=10 \
	--verbosity=3 \
	--preload $(JS_FILE) \
	--datadir=$(DATADIR1)

ARGS1=$(BASE_ARGS) \
	--port=$(NODE_PORT) \
	--rpc \
	--rpcaddr="127.0.0.1" \
	--rpcport=$(RPC_PORT) \
	--rpcapi="eth,web3,net,personal,db,shh,txpool,miner,admin" \
	--rpccorsdomain="*" \
	--mine \
	--minerthreads=1

GEN_ADDR := $(shell $(NODE) $(BASE_ARGS) --password=$(PSWD_FILE) account new | head -1 | cut -d "{" -f2 | cut -d "}" -f1)
GET_FILE_WITH_ADDR := $(shell find $(KEYSTORE1) -type f -name \*$(GEN_ADDR))

console:
	$(NODE) $(BASE_ARGS) attach $(IPC_FILE1)

sendfrom:
	$(NODE) $(BASE_ARGS) --exec 'personal.unlockAccount(eth.coinbase, "$(PSWD)", 2); quickSend(eth.coinbase, "$(ADDRESS)", $(AMOUNT));' attach $(IPC_FILE1)

account:
	python -c 'import binascii;\
import eth_keyfile;\
private_key = binascii.hexlify(eth_keyfile.extract_key_from_keyfile("$(GET_FILE_WITH_ADDR)", "${PSWD}")).decode("utf-8");\
print("Generated private key (hex): 0x%s" % private_key);\
from m1_pk_2_pb_2_addr import private_to_public_key, public_to_address;\
public_key = private_to_public_key(private_key);\
print("Derived public key (hex uncompressed): 0x04%s" % public_key);\
ethereum_address = public_to_address(public_key);\
print("Derived address (hex): 0x%s" % ethereum_address);\
'

start:
	mkdir -p $(DATADIR1) $(KEYSTORE1)
	@if [ "$(shell ls -A $(KEYSTORE1))" = "" ]; then\
		$(MAKE) account;\
	fi
	nohup $(NODE) $(ARGS1) ${} > $(LOG_FILE1) 2>&1 & echo $$! > $(PID_FILE1)

stop: $(PID_FILE1)
	-kill -9 `cat $<` && `rm $<`

clean:
	find $(DATADIR1)/* -not -name 'keystore' -delete

destroy:
	rm -rf $(DATADIR1)