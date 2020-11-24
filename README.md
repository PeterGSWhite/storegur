# storegur

<h3 align="center">STOREGUR</h3>

  <p align="center">
    A proof of concept for exploiting Imgur and using it as a personal data/file store. Encodes UTF-8 encoded data into PNG images which can then be stored on Imgur for later retrieval.
    <br/>
  </p>

### Built With

* Python

### Prerequisites

* Python3
```
https://www.python.org/download/releases/3.0/
```

### Installation

1. Clone the repo
```
git clone https://github.com/PeterGSWhite/storegur.git
```

2. Create venv and install python modules<br/>
```
python3 -m venv api/venv
(POSIX)	source api/venv/bin/activate
(Windows) api/venv/Scripts/activate
pip install -r requirements.txt
```

### Examples
```
from storegur import SDIdStore
from config import client_id, token # <- You need your own Imgur API credentials
seed = "Any string you choose - is used to set the encryption"

db = SDIdStore('db_name', client_id, token, seed)
# The below method
  1. Encrypts data into a PNG image
  2. Uploads the image to Imgur
  3. Saves the Imgur Id to a Key-Value store so you can retrieve it later
db.store_file('Abra Cadabra', './a_file_of_data.txt', title='optional metadata', description='optional metadata')

# Then retrieval is the same but in reverse
db.get_file('Abra Cadabra', './downloaded_file.txt')
```
