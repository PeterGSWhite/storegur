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
    def db_put(self, key, value):
        """Inherit this method to control where (Key, Imgur ID) pair gets saved"""
        pass
    def db_get(self, key):
        """Inherit this method to control where (Key, Imgur ID) pair gets retrieved"""
        pass

    def upload_string(self, text):
        """Converts string to PNG file, uploads to imgur and returns the Imgur ID"""
        image = self.image_encoder.encode_as_image(text)

        # Upload the image
        print('Uploading image...')
        with tempfile.NamedTemporaryFile(mode="wb") as temp:
            image.save(temp.name, format='PNG')

            response = self.imgur_client.image_upload(temp.name, 'Untitled', 'wik')
            return response['response']['data']['id']
    def download_char_list(self, imgur_id):
        """Downloads Imgur image, converts it back into UTF-8 and writes to file"""
        print('Downloading', imgur_id)
        response = requests.get(f'https://i.imgur.com/{imgur_id}.png')
        print('Decoding response...')
        output = self.image_encoder.decode_png_response(response.content)
        return output

    # Inherited methods - implementation depends on where Imgur IDs are being stored
    def store_file(self, key, source_path):
        """Uploads file and returns the imgur Id of it's image"""
        print('Encoding', source_path, 'as image...')
        with open(source_path, 'r') as f:
            imgur_id = self.upload_string(f.read())
            self.db_put(key, imgur_id)

    def get_file(self, key, target_path):
        """Gets image from Imgur Id and writes contents to file"""
        imgur_id = self.db_get(key)
        chars = self.download_char_list(imgur_id)
        print('Writing to', target_path)
        with open(target_path, 'w') as f:
            for c in chars:
                f.write(c)
    def store_text(self, key, text):
        """Uploads string of text and returns the imgur Id of it's image"""
        imgur_id = self.upload_string(text)
        self.db_put(key, imgur_id)
    def get_text(self, key):
        """Gets the image from Imgur Id and returns the stored data as a string"""
        imgur_id = self.db_get(key)
        chars = self.download_char_list(imgur_id)
        return ''.join(chars)
    def store_json(self, key, json_dict):
        pass
    def get_json(self, key):
        pass
    def store_bytes(self, key, text):
        pass
    def get_bytes(self, key, text):
        pass

class SDIdStore(ImgurIdStore):
    """Uses an sqlitedict as a key-imgurid store, but all data is stored on imgur"""
    def __init__(self, db, client_id, token, seed):
        self.db = SqliteDict(f'{db}.sqlite', autocommit=True)
        super().__init__(client_id, token, seed)
    def db_put(self, key, value):
        self.db[key] = value
    def db_get(self, key):
        return self.db[key]

db = SDIdStore('test', client_id, token, seed)
#db.store_file('new', './a new one.txt')
#db.get_file('new', './hoii.html')
#db.store_text('sillykey','HEY buddy boy')
print(db.get_text('sillykey'))

# ??? Multi part upload?
# ??? Can I leverage other imgur features, like descriptions, titles and albums? Some kind of metadata attached to files, or file groupings/directories?

# From user perspective:
# USER SUPPLIED KEY, FORMAT -> DATA IN SUPPLIED FORMAT
# USER SUPPLIED DATA, FORMAT, USER SUPPLIED KEY -> SET IMGUR ID to VALUE OF KEY

# Should be extensible to different datastore paradigms
# For development, just create a sqlitedict