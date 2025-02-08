import time
import json
import hashlib
import random
from typing import List, Dict
from datetime import datetime
from colorama import Fore, Style
import os
import rsa  # RSA şifreleme kütüphanesi

# Block Class
class Block:
    #Constructor
    def __init__(self, index: int, previous_hash: str, transactions: List[dict], nonce: int = 0, miner: str = None):
        self.index = index
        self.timestamp = time.time()
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.nonce = nonce
        self.miner = miner
        self.hash = self.calculate_hash()

    #Calculate Hash SHA-256
    def calculate_hash(self) -> str:
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "transactions": self.transactions,
            "nonce": self.nonce,
            "miner": self.miner
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    #Timestamp değerini okunabilir hale getirir.
    def get_readable_timestamp(self) -> str:
        return datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Blockchain Class (Yönetici sınıf)
class Blockchain:
    #Constructor
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[dict] = []
        self.difficulty = 4
        self.create_genesis_block()
        self.users = {}  # Kullanıcıların özel ve genel anahtarlarını saklamak için

    # İlk bloğu oluşturan function ilk değer:0 (Genesis Block)
    def create_genesis_block(self):
        genesis_block = Block(index=0, previous_hash="0", transactions=[], nonce=0, miner="Genesis")
        self.chain.append(genesis_block)

    # Kullanıcıya ait cüzdan oluştur
    def create_wallet(self, username: str):
        if username in self.users:
            print(Fore.RED + "Bu kullanıcı adı zaten kullanılıyor!" + Style.RESET_ALL)
            return None
        public_key, private_key = rsa.newkeys(512)
        self.users[username] = {"public_key": public_key, "private_key": private_key}
        return public_key, private_key

    # İşlemi imzala
    def sign_transaction(self, sender: str, recipient: str, amount: float):
        if sender not in self.users or recipient not in self.users:
            print(Fore.RED + "Geçersiz kullanıcı!" + Style.RESET_ALL)
            return None
        transaction_data = f"{sender}->{recipient}:{amount}".encode()
        signature = rsa.sign(transaction_data, self.users[sender]["private_key"], 'SHA-256')
        return {"sender": sender, "recipient": recipient, "amount": amount, "signature": signature.hex()}
    
    # İşlemi doğrula
    def verify_transaction(self, transaction: dict):
        sender = transaction["sender"]
        recipient = transaction["recipient"]
        amount = transaction["amount"]
        signature = bytes.fromhex(transaction["signature"])
        transaction_data = f"{sender}->{recipient}:{amount}".encode()
        try:
            rsa.verify(transaction_data, signature, self.users[sender]["public_key"])
            return True
        except rsa.VerificationError:
            return False

    # Yeni bir işlem ekleyen fonskiyon
    def add_transaction(self, sender: str, recipient: str, amount: float):
        transaction = self.sign_transaction(sender, recipient, amount)
        if not transaction or not self.verify_transaction(transaction):
            print(Fore.RED + "İşlem doğrulaması başarısız!" + Style.RESET_ALL)
            return
        self.pending_transactions.append(transaction)
        print(Fore.YELLOW + "İşlem başarıyla eklendi!" + Style.RESET_ALL)

    # Yeni bir blok madenciliğini yaparak blockchain'e eklesin
    def mine_block(self, miner_address: str):
        if not self.pending_transactions:
            print(Fore.RED + "İşlem kuyruğu boş, madencilik yapılamaz!" + Style.RESET_ALL)
            return None
        last_block = self.chain[-1]
        reward_transaction = {"sender": "Blockchain", "recipient": miner_address, "amount": random.randint(5, 15)}
        self.pending_transactions.append(reward_transaction)
        new_block = Block(index=len(self.chain), previous_hash=last_block.hash, transactions=self.pending_transactions,
                          miner=miner_address)
        while not new_block.hash.startswith("0" * self.difficulty):
            new_block.nonce += 1
            new_block.hash = new_block.calculate_hash()
        print(Fore.GREEN + f"Yeni blok madenciliği tamamlandı: {new_block.hash}" + Style.RESET_ALL)
        self.chain.append(new_block)
        self.pending_transactions = []

    # Blok zincirini kontrol et
    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True


blockchain = Blockchain()
# Kullanıcı arayüzü
while True:
    print("\n1. Cüzdan oluştur")
    print("2. Yeni işlem ekle")
    print("3. Madencilik yap")
    print("4. Blok zincirini görüntüle")
    print("5. Zinciri doğrula")
    print("6. Çıkış")

    choice = input("Seçiminiz: ")

    if choice == "1":
        username = input("Kullanıcı adı: ")
        public_key, private_key = blockchain.create_wallet(username)
        if public_key:
            print(Fore.GREEN + f"Cüzdan oluşturuldu! Genel anahtar: {public_key}" + Style.RESET_ALL)
    elif choice == "2":
        sender = input("Gönderen: ")
        recipient = input("Alıcı: ")
        amount = float(input("Miktar: "))
        blockchain.add_transaction(sender, recipient, amount)
    elif choice == "3":
        miner = input("Madencinin adı: ")
        blockchain.mine_block(miner)
    elif choice == "4":
        for block in blockchain.chain:
            print(
                Fore.CYAN + f"Blok {block.index} - Hash: {block.hash} - Önceki Hash: {block.previous_hash}" + Style.RESET_ALL)
    elif choice == "5":
        valid = blockchain.is_chain_valid()
        print(Fore.GREEN + "Blok zinciri geçerli!"+ Style.RESET_ALL if valid else Fore.RED + "Blok zinciri bozulmuş!" + Style.RESET_ALL)
    elif choice == "6":
        break