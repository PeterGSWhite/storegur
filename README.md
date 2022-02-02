# storegur

<h3 align="center">STOREGUR</h3>

  <p align="center">
  
  In theory, any data of any file type can be transformed into an image and then uploaded to Imgur for free.  <br/><br/> This is a proof of concept for exploiting Imgur by using it as a personal file store for arbitrary file types.<br/> Encodes UTF-8 encoded data into PNG images which can then be stored on Imgur for later retrieval.

  </p>

### Built With

* Python

### Prerequisites

* Python3
```
https://www.python.org/download/releases/3.0/
```
* Your own Imgur API Key (due to the nature of the app, I don't want people using mine and getting my access blocked).<br/>
Getting a client_id and token only takes a few seconds:
https://api.imgur.com/oauth2/addclient

### Installation

1. Clone the repo and cd in
```
git clone https://github.com/PeterGSWhite/storegur.git
cd storegur
```

2. Create venv and install python modules<br/>
```
python3 -m venv venv
(POSIX)	source venv/bin/activate
(Windows) venv/Scripts/activate
pip install -r requirements.txt
```

### Examples
```
from storegur import SDIdStore
from config import client_id, token # <- You need your own Imgur API credentials
seed = "Any string you choose - is used to set the encryption"

db = SDIdStore('db_name', client_id, token, seed)
"""The below method
  1. Encrypts data into a PNG image
  2. Uploads the image to Imgur
  3. Saves the Imgur Id to a Key-Value store so you can retrieve it later"""
db.store_file('Abra Cadabra', './a_file_of_data.txt', title='optional metadata', description='optional metadata')

# Then retrieval is the same but in reverse
db.get_file('Abra Cadabra', './downloaded_file.txt')
```
