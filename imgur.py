import requests
from imgur_python import Imgur
from os import path
from io import BytesIO
from encoding import PngEncoder
import tempfile
from config import client_id, token, seed

# Set up
imgur_client = Imgur({'client_id': client_id, 'access_token': token})

# Create the image
encoder = PngEncoder(seed)
def upload_file(file_path):
    with open(file_path, 'r') as f:
        image = encoder.encode_as_image(f.read())

    # Upload the image
    with tempfile.NamedTemporaryFile(mode="wb") as temp:
        image.save(temp.name, format='PNG')

        response = imgur_client.image_upload(temp.name, 'Untitled', 'wik')
        return response['response']['data']['id']

# Get the image
def download_file(imgur_id, target_file_path):
    print('Downloading', imgur_id)
    response = requests.get(f'https://i.imgur.com/{imgur_id}.png')
    print('Decoding response...')
    output = encoder.decode_png_response(response.content)
    print('Writing to', target_file_path)
    with open(target_file_path, 'w') as f:
        for c in output:
            f.write(c)

# id = upload_file('./wik.txt')
# print(id)
download_file('bSlVJnN', './output.html')
# To do:
# write functions for saving from, or decoding to:
# File, string, bytes, json
# ??? Multi part upload?
# ??? What will the nature of the key-value store be?
# ??? Integrate with other databases? Are there other projects which wrap well known databases?