import requests
from imgur_python import Imgur
from os import path
from io import BytesIO
from encoding import PngEncoder
import tempfile
from config import client_id, token, seed

from sqlitedict import SqliteDict
class ImgurIdStore:
    '''Base class for the storing of KEY:IMGURID pairs
    Children can implement any database system to store and retrieve
    Imgur Ids, and convert stored data into desired formats'''
    def __init__(self, client_id, token, seed):
        self.imgur_client = Imgur({'client_id': client_id, 'access_token': token})
        self.image_encoder = PngEncoder(seed)
    
    def upload_file(self, file_path):
        """Converts file data to PNG file, uploads to imgur and returns the Imgur ID"""
        print('Encoding', file_path, 'as image...')
        with open(file_path, 'r') as f:
            image = self.image_encoder.encode_as_image(f.read())

        # Upload the image
        print('Uploading image...')
        with tempfile.NamedTemporaryFile(mode="wb") as temp:
            image.save(temp.name, format='PNG')

            response = self.imgur_client.image_upload(temp.name, 'Untitled', 'wik')
            return response['response']['data']['id']

    def download_file(self, imgur_id, target_file_path):
        """Downloads Imgur image, converts it back into UTF-8 and writes to file"""
        print('Downloading', imgur_id)
        response = requests.get(f'https://i.imgur.com/{imgur_id}.png')
        print('Decoding response...')
        output = self.image_encoder.decode_png_response(response.content)
        print('Writing to', target_file_path)
        with open(target_file_path, 'w') as f:
            for c in output:
                f.write(c)

    # Inherited methods - depends on where Imgur IDs are being stored
    def store_file(self, key, source_path):
        pass
    def get_file(self, key, target_path):
        pass
    def store_text(self, key, text):
        pass
    def get_text(self, key):
        pass
    def store_json(self, key, json_dict):
        pass
    def get_json(self, key):
        pass
    def store_bytes(self, key, text):
        pass
    def get_bytes(self, key, text):
        pass

class SDIdStore(ImgurIdStore):
    def __init__(self, db, client_id, token, seed):
        self.db = SqliteDict(f'{db}.sqlite', autocommit=True)
        super().__init__(client_id, token, seed)
    def store_file(self, key, source_path):
        id = self.upload_file(source_path)
        self.db[key] = id
    def get_file(self, key, target_path):
        id = self.db[key]
        self.download_file(id, target_path)

db = SDIdStore('test', client_id, token, seed)
#db.store_file('Кириллица', './another_test.txt')
db.get_file('Кириллица', './rs.html')

# ??? Multi part upload?

# From user perspective:
# USER SUPPLIED KEY, FORMAT -> DATA IN SUPPLIED FORMAT
# USER SUPPLIED DATA, FORMAT, USER SUPPLIED KEY -> SET IMGUR ID to VALUE OF KEY

# Should be extensible to different datastore paradigms
# For development, just create a sqlitedict