import sys
import time
from web3 import Web3
from eth_abi import decode

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

if not w3.is_connected():
    print("Connection failed!")
    exit()

if len(sys.argv) < 3:
    print("Usage: python SmartContractAccess.py <contract_address> <private_key>")
    sys.exit(1)

account = w3.eth.accounts[0] #TODO this has to be the admin SPECIFICALLY (probably also commandline argument)
private_key = sys.argv[1]
contract_address = sys.argv[2] 
contract_abi =[
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "_addr",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256[]",
				"name": "heldData",
				"type": "uint256[]"
			}
		],
		"name": "IncomingRequest",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "makeCreditRequest",
		"outputs": [],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "_addr",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256[]",
				"name": "heldData",
				"type": "uint256[]"
			}
		],
		"name": "PassOutTree",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "requester",
				"type": "address"
			},
			{
				"internalType": "bool",
				"name": "passed",
				"type": "bool"
			}
		],
		"name": "preFilterResult",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "_addr",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "string",
				"name": "reason",
				"type": "string"
			}
		],
		"name": "RequestDenied",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "_addr",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "string",
				"name": "reason",
				"type": "string"
			}
		],
		"name": "RequestFail",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "writeSubTreeAnswer",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "allowedAddresses",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getValue",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]


contract = w3.eth.contract(address=contract_address, abi=contract_abi)


def post_subtree_results():
    transaction = contract.functions.writeSubTreeAnswer().build_transaction({
        'chainId': 1337, 
        'gas': 2000000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(account),
    })
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"Transaction sent successfully with hash: {txn_hash.hex()}")

# We need: Input Array, Id of Subtree


def listen_for_passout_events():
    pass_out_filter = w3.eth.filter({
        "address": contract_address,
        "topics": [w3.keccak(text="PassOutTree(address,uint256[])").hex()]
    })

    while True:
        logs = w3.eth.get_filter_changes(pass_out_filter.filter_id)
        for log in logs:
            sender = "0x" + log["topics"][1].hex()[-40:]
            data_bytes = log["data"]
            data = decode(["uint256[]"], data_bytes)[0]
            
            print(f"Sender: {sender}")
            print("Values:", data)
            print("========")

        time.sleep(5)

       
if __name__ == "__main__":
    print("Listening for Pass Out Tree Events...")
    listen_for_passout_events()
