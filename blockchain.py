from typing import List  # List type
import time  # Blok zaman damgası için
import json  # JSON formatı için
import hashlib  # Hash fonksiyonları için
from colorama import Fore, Style  # Renkli çıktılar için
from datetime import datetime  # Zaman damgası için

# Block Class
class Block:
    """
    Blockchain içindeki bir blok temsili
    """
    """
    __init__ : 
    Yeni bir nesne (object) oluşturulduğunda çalışır.
    Nesneye ait başlangıç değerlerini (attributes) tanımlar.
    return ifadesi kullanılmaz çünkü doğrudan nesneyi başlatır.

    self:
    self, bir sınıf içinde kullanılan özel bir değişkendir ve sınıfa ait özelliklere ve metotlara erişmeyi sağlar.
    Özellikleri:
    self, her nesneye özgü değişkenleri temsil eder.
    Sınıfın içindeki metotlarda, nesnenin kendi verilerine erişmesini sağlar.
    Python'da bir sınıf metodu içinde self yazılması zorunludur (ancak adı değiştirilebilir, yine de Python topluluğu self kullanır).
    """
    #Constructor
    def __init__(self, index: int, previous_hash: str, transactions: List[dict], nonce: int = 0):
        self.index = index
        self.timestamp = time.time() #Zaman damgası
        self.previous_hash = previous_hash #Önceki bloğun hash değeri
        self.transactions = transactions #Blok içindeki işlemler
        self.nonce = nonce #Proof of Work madenciliği için nonce değeri
        self.hash = self.calculate_hash() #Blok hash değeri

    #Calculate Hash SHA-256
    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "transactions": self.transactions,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def get_readable_timestamp(self):
        """Timestamp değerini okunabilir hale getirir."""
        return datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Blockchain Class (Yönetici sınıf)
class Blockchain:
    def __init__(self):
        self.chain: List[Block] = [] # Blok zinciri
        self.pending_transactions: List[dict] = [] # Bekleyen işlemler
        self.difficulty = 4 # Proof of Work zorluk seviyesi
        self.create_genesis_block() # İlk bloğu oluştur

    # İlk bloğu oluşuran function ilk değer:0 (Genesis Block)
    def create_genesis_block(self):
        genesis_block = Block(0, "0", [], nonce=0)
        self.chain.append(genesis_block)

    # YEni bir işlem ekleyen fonskiyon
    def add_transaction(self, sender: str, recipient: str, amount: float):
        self.pending_transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount
        })

        # 3 işlem eklendikten sonra otomatik madencilik
        if len(self.pending_transactions) >= 3:
            self.mine_block()
    
    # Yeni bir blok madenciliğini yaparak blockchain'e eklesin
    def mine_block(self):
        if not self.pending_transactions:
            print(Fore.RED + "Blokta işlem yok, madencilik yapılamıyor" + Style.RESET_ALL)
            return None

        #Zincirin en son bloğunu al
        last_block = self.chain[-1]
        #Yeni blok
        new_block = Block(
            index=len(self.chain),
            previous_hash=last_block.hash,
            transactions=self.pending_transactions,
            nonce=0
        )


        #Proof of Work madenciliği
        #belirli sayıda sıfır ile başlayan hash değeri bulunana kadar nonce değerini arttır
        while not new_block.hash.startswith('0' * self.difficulty):
            new_block.nonce += 1
            new_block.hash = new_block.calculate_hash()

        print(Fore.GREEN + f"Blok madenciliği başarılı: {new_block.hash}" + Style.RESET_ALL)

        #yeni bloğu zincire ekle
        self.chain.append(new_block)

        #Bekleyen işlemleri temizle
        self.pending_transactions = []

    #Blok zincirini kontrol et
    def is_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            #Blok hash kontrolü
            if current_block.hash != current_block.calculate_hash():
                print("Blok hash değeri hatalı")
                return False
            
            #Önceki blok hash kontrolü
            if current_block.previous_hash != previous_block.hash:
                print("Önceki blok hash değeri hatalı")
                return False
        
        #Blok zinciri geçerli
        return True

    def print_chain(self):
        for block in self.chain:
            print(Fore.CYAN + f"Timestamp: {block.timestamp} - Block: {block.index} - Hash: {block.hash} - "
                  f"Önceki Hash: {block.previous_hash} - Transactions: {block.transactions}" + Style.RESET_ALL)

    def get_balance(self, user: str):
        """Belirli bir kullanıcının bakiyesini hesaplar."""
        balance = 0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction["sender"] == user:
                    balance -= transaction["amount"]
                if transaction["recipient"] == user:
                    balance += transaction["amount"]
        return balance

    def export_to_json(self):
        """Blockchain verisini JSON formatında dışa aktarır."""
        return json.dumps([block.__dict__ for block in self.chain], indent=4)


# Blockchain Test
test_chain = Blockchain()
test_chain.add_transaction("Enes", "Serdar", 10)
test_chain.add_transaction("Serdar", "Enes", 5)
test_chain.mine_block()
test_chain.add_transaction("Beyza", "Enes", 15)
test_chain.mine_block()
test_chain.print_chain()

# Blok zinciri geçerli mi?
print(Fore.YELLOW + "Blok zinciri geçerli mi?", test_chain.is_valid(), Style.RESET_ALL)

print(Fore.BLUE + "Enes'in bakiyesi:", test_chain.get_balance("Enes"), Style.RESET_ALL)
print(Fore.BLUE + "Serdar'ın bakiyesi:", test_chain.get_balance("Serdar"), Style.RESET_ALL)
print(Fore.BLUE + "Beyza'nın bakiyesi:", test_chain.get_balance("Beyza"), Style.RESET_ALL)

# İşlem kuyruğu boş, madencilik yapılacak işlem yok.
test_chain.mine_block();

# Blockchain'i JSON olarak dışa aktarma
print(Fore.MAGENTA + "Blockchain JSON Formatı:")
print(test_chain.export_to_json())