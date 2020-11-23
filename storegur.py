import requests
from imgur_python import Imgur
from os import path
from io import BytesIO
from encoding import PngEncoder
import tempfile
import json
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
    
    # Core upload and download functionality
    def upload_string(self, text, title='', description=''):
        """Converts string to PNG file, uploads to imgur and returns the Imgur ID"""
        image = self.image_encoder.encode_as_image(text)

        # Upload the image
        print('Uploading image...')
        with tempfile.NamedTemporaryFile(mode="wb") as temp:
            image.save(temp.name, format='PNG')

            response = self.imgur_client.image_upload(temp.name, title, description)
            return response['response']['data']['id']
    def download_char_list(self, imgur_id):
        """Downloads Imgur image, converts it back into UTF-8 and writes to file"""
        print('Downloading', imgur_id)
        response = requests.get(f'https://i.imgur.com/{imgur_id}.png')
        print('Decoding response...')
        output = self.image_encoder.decode_png_response(response.content)
        return output

    # Metadata
    def update_metadata(self, key, title, description):
        """Change the Title and Description of existing data"""
        imgur_id = self.db_get(key)
        self.imgur_client.image_update(imgur_id, title, description)
    def get_metadata(self, key):
        imgur_id = self.db_get(key)
        response = self.imgur_client.image_get(imgur_id)
        return {
            'title': response['response']['data']['title'],
            'description': response['response']['data']['description'],
            'datetime': response['response']['data']['datetime']
        }

    def delete_entry(self, key):
        imgur_id = self.db_get(key)
        self.imgur_client.image_delete(imgur_id)
        
    # Methods for different data types
    def store_file(self, key, source_path, title='', description=''):
        """Uploads file and returns the imgur Id of it's image"""
        print('Encoding', source_path, 'as image...')
        with open(source_path, 'r') as f:
            imgur_id = self.upload_string(f.read(), title, description)
            self.db_put(key, imgur_id)

    def get_file(self, key, target_path):
        """Gets image from Imgur Id and writes contents to file"""
        imgur_id = self.db_get(key)
        chars = self.download_char_list(imgur_id)
        print('Writing to', target_path)
        with open(target_path, 'w') as f:
            for c in chars:
                f.write(c)
    def store_text(self, key, text, title='', description=''):
        """Uploads string of text and assigns the Imgur Id of it's image to key"""
        imgur_id = self.upload_string(text, title, description)
        self.db_put(key, imgur_id)
    def get_text(self, key):
        """Gets the string of text from the assigned key"""
        imgur_id = self.db_get(key)
        chars = self.download_char_list(imgur_id)
        return ''.join(chars)
    def store_json(self, key, json_dict, title='', description=''):
        """Uploads json and assigns the Imgur Id of it's image to key
        Note: this project is not capable of accessing specific data within a json object
        The Entire json object must be uploaded and downloaded with each call.
        """
        json_string = json.dumps(json_dict)
        self.store_text(key, json_string, title, description)
    def get_json(self, key):
        """Gets the json from the assigned key 
        Note: this project is not capable of accessing specific data within a json object
        The Entire json object must be uploaded and downloaded with each call.
        """
        json_string = self.get_text(key) # Ends in a backtick and don't know why yet
        return json.loads(json_string)

class SDIdStore(ImgurIdStore):
    """Uses an sqlitedict as a key-imgurid store, but all data is stored on imgur"""
    def __init__(self, db, client_id, token, seed):
        self.db = SqliteDict(f'{db}.sqlite', autocommit=True)
        super().__init__(client_id, token, seed)
    def db_put(self, key, value):
        self.db[key] = value
    def db_get(self, key):
        return self.db[key]
