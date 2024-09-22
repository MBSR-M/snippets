import hashlib
import hmac
import time

# Secret key for HMAC (should be securely shared/stored)
SECRET_KEY = b'supersecretkey'


# Define the block structure
class Block:
    def __init__(self, index, previous_hash, timestamp, data, current_hash, nonce):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.current_hash = current_hash
        self.nonce = nonce


# Function to calculate the HMAC-based hash of a block
def calculate_hmac_hash(index, previous_hash, timestamp, data, nonce, key=SECRET_KEY):
    value = f"{index}{previous_hash}{timestamp}{data}{nonce}".encode()
    return hmac.new(key, value, hashlib.sha256).hexdigest()


# Function to create the genesis (first) block
def create_genesis_block():
    return Block(0, "0", time.time(), "Genesis Block", calculate_hmac_hash(0, "0", time.time(), "Genesis Block", 0), 0)


# Function to create new blocks with HMAC protection
def create_new_block(previous_block, data, difficulty):
    index = previous_block.index + 1
    timestamp = time.time()
    previous_hash = previous_block.current_hash
    nonce = 0
    current_hash = calculate_hmac_hash(index, previous_hash, timestamp, data, nonce)

    # Proof of Work: Find a hash that starts with a certain number of zeros
    while not current_hash.startswith('0' * difficulty):
        nonce += 1
        current_hash = calculate_hmac_hash(index, previous_hash, timestamp, data, nonce)

    return Block(index, previous_hash, timestamp, data, current_hash, nonce)


# Define the MBSR cryptocurrency class
class MBSRCoin:
    def __init__(self, difficulty=4):
        self.blockchain = [create_genesis_block()]  # Start with genesis block
        self.difficulty = difficulty  # Set the difficulty level for mining

    def get_latest_block(self):
        return self.blockchain[-1]

    def add_block(self, data):
        new_block = create_new_block(self.get_latest_block(), data, self.difficulty)
        if self.is_block_valid(new_block, self.get_latest_block()):
            self.blockchain.append(new_block)
        else:
            print("Invalid block, it was not added to the blockchain!")

    # Function to validate a block
    def is_block_valid(self, block, previous_block):
        if previous_block.index + 1 != block.index:
            return False
        if previous_block.current_hash != block.previous_hash:
            return False
        if not block.current_hash.startswith('0' * self.difficulty):
            return False
        if block.current_hash != calculate_hmac_hash(block.index, block.previous_hash, block.timestamp, block.data,
                                                     block.nonce):
            return False
        return True

    # Function to check the integrity of the entire blockchain
    def is_chain_valid(self):
        for i in range(1, len(self.blockchain)):
            current_block = self.blockchain[i]
            previous_block = self.blockchain[i - 1]
            if not self.is_block_valid(current_block, previous_block):
                return False
        return True

    # Print out the blockchain and monitor metrics
    def print_blockchain(self):
        for block in self.blockchain:
            print(f"Index: {block.index}")
            print(f"Previous Hash: {block.previous_hash}")
            print(f"Timestamp: {block.timestamp}")
            print(f"Data: {block.data}")
            print(f"Hash: {block.current_hash}")
            print(f"Nonce: {block.nonce}\n")

    def mine_block(self, data):
        print(f"Mining block with data: {data}")
        start_time = time.time()
        self.add_block(data)
        end_time = time.time()
        print(f"Block mined in {end_time - start_time:.4f} seconds")

    # Monitor the latest block
    def monitor_latest_block(self):
        latest_block = self.get_latest_block()
        print("Latest Block:")
        print(f"Index: {latest_block.index}")
        print(f"Previous Hash: {latest_block.previous_hash}")
        print(f"Timestamp: {latest_block.timestamp}")
        print(f"Data: {latest_block.data}")
        print(f"Hash: {latest_block.current_hash}")
        print(f"Nonce: {latest_block.nonce}")
        print(f"Chain Valid: {self.is_chain_valid()}\n")


# Create a new instance of MBSR Coin with difficulty level 4
mbsr_coin = MBSRCoin(difficulty=4)

# Mine and add a few blocks to the blockchain
mbsr_coin.mine_block("First transaction data")
mbsr_coin.mine_block("Second transaction data")

# Print the blockchain data
mbsr_coin.print_blockchain()

# Monitor the latest block
mbsr_coin.monitor_latest_block()
