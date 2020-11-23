from storegur import SDIdStore
from config import client_id, token, seed
if __name__ == "__main__":
    db = SDIdStore('db_name', client_id, token, seed)

    # Call methods here