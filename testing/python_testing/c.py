import time
import hashlib
from kafka import KafkaProducer
import json


# Block structure
class Block:
    def __init__(self, index, previous_hash, timestamp, data, current_hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.current_hash = current_hash


# Hash function using SHA-3
def calculate_hash(index, previous_hash, timestamp, data):
    value = f"{index}{previous_hash}{timestamp}{data}".encode()
    return hashlib.sha3_256(value).hexdigest()


# Genesis block
def create_genesis_block():
    return Block(0, "0", time.time(), "Genesis Block", calculate_hash(0, "0", time.time(), "Genesis Block"))


# New block
def create_new_block(previous_block, data):
    index = previous_block.index + 1
    timestamp = time.time()
    previous_hash = previous_block.current_hash
    current_hash = calculate_hash(index, previous_hash, timestamp, data)
    return Block(index, previous_hash, timestamp, data, current_hash)


# MBSR Coin class
class MBSRCoin:
    def __init__(self):
        self.blockchain = [create_genesis_block()]
        self.producer = KafkaProducer(bootstrap_servers='localhost:9092',
                                      value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                                      api_version=(2, 8, 0))

    def get_latest_block(self):
        return self.blockchain[-1]

    def add_block(self, data):
        new_block = create_new_block(self.get_latest_block(), data)
        self.blockchain.append(new_block)
        self.broadcast_transaction(new_block)

    # Broadcast transaction via Kafka
    def broadcast_transaction(self, block):
        transaction = {
            'index': block.index,
            'previous_hash': block.previous_hash,
            'timestamp': block.timestamp,
            'data': block.data,
            'hash': block.current_hash
        }
        self.producer.send('mbsr_transactions', transaction)

    def print_blockchain(self):
        for block in self.blockchain:
            print(f"Index: {block.index}")
            print(f"Previous Hash: {block.previous_hash}")
            print(f"Timestamp: {block.timestamp}")
            print(f"Data: {block.data}")
            print(f"Hash: {block.current_hash}\n")


# CDN integration example: tracking bandwidth usage and payments
class CDNUsage:
    def __init__(self, mbsr_coin):
        self.mbsr_coin = mbsr_coin

    def track_usage(self, user_id, usage_data):
        transaction_data = {
            'user_id': user_id,
            'usage_data': usage_data,
            'cost': self.calculate_cost(usage_data)
        }
        self.mbsr_coin.add_block(transaction_data)

    @staticmethod
    def calculate_cost(usage_data):
        return usage_data['bandwidth'] * 0.01  # Cost per GB used (example)


# Example Usage:
__mbsr = MBSRCoin()
cdn_usage = CDNUsage(__mbsr)

# Simulate user usage
cdn_usage.track_usage('user123', {'bandwidth': 100})  # 100 GB used
cdn_usage.track_usage('user456', {'bandwidth': 250})  # 250 GB used

# Print the blockchain
__mbsr.print_blockchain()
