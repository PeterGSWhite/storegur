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
        """Uploads string of text and assigns the Imgur Id of it's image to key"""
        imgur_id = self.upload_string(text)
        self.db_put(key, imgur_id)
    def get_text(self, key):
        """Gets the string of text from the assigned key"""
        imgur_id = self.db_get(key)
        chars = self.download_char_list(imgur_id)
        return ''.join(chars)
    def store_json(self, key, json_dict):
        """Uploads json and assigns the Imgur Id of it's image to key"""
        json_string = json.dumps(json_dict)
        self.store_text(key, json_string)
    def get_json(self, key):
        """Gets the json from the assigned key """
        json_string = self.get_text(key) # Ends in a backtick and don't know why yet
        #print(json_string)
        return json.loads(json_string)

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
#db.store_file('examplejson', './hoii.json')
#db.get_file('jo', './hoii.json')
#db.store_text('sillykey','HEY buddy boy')
#print(db.get_text('sillykey'))

# j = {"web-app": {
#     "servlet": [   
#       {
#         "servlet-name": "cofaxCDS",
#         "servlet-class": "org.cofax.cds.CDSServlet",
#         "init-param": {
#           "configGlossary:installationAt": "Philadelphia, PA",
#           "configGlossary:adminEmail": "ksm@pobox.com",
#           "configGlossary:poweredBy": "Cofax",
#           "configGlossary:poweredByIcon": "/images/cofax.gif",
#           "configGlossary:staticPath": "/content/static",
#           "templateProcessorClass": "org.cofax.WysiwygTemplate",
#           "templateLoaderClass": "org.cofax.FilesTemplateLoader",
#           "templatePath": "templates",
#           "templateOverridePath": "",
#           "defaultListTemplate": "listTemplate.htm",
#           "defaultFileTemplate": "articleTemplate.htm",
#           "useJSP": False,
#           "jspListTemplate": "listTemplate.jsp",
#           "jspFileTemplate": "articleTemplate.jsp",
#           "cachePackageTagsTrack": 200,
#           "cachePackageTagsStore": 200,
#           "cachePackageTagsRefresh": 60,
#           "cacheTemplatesTrack": 100,
#           "cacheTemplatesStore": 50,
#           "cacheTemplatesRefresh": 15,
#           "cachePagesTrack": 200,
#           "cachePagesStore": 100,
#           "cachePagesRefresh": 10,
#           "cachePagesDirtyRead": 10,
#           "searchEngineListTemplate": "forSearchEnginesList.htm",
#           "searchEngineFileTemplate": "forSearchEngines.htm",
#           "searchEngineRobotsDb": "WEB-INF/robots.db",
#           "useDataStore": True,
#           "dataStoreClass": "org.cofax.SqlDataStore",
#           "redirectionClass": "org.cofax.SqlRedirection",
#           "dataStoreName": "cofax",
#           "dataStoreDriver": "com.microsoft.jdbc.sqlserver.SQLServerDriver",
#           "dataStoreUrl": "jdbc:microsoft:sqlserver://LOCALHOST:1433;DatabaseName=goon",
#           "dataStoreUser": "sa",
#           "dataStorePassword": "dataStoreTestQuery",
#           "dataStoreTestQuery": "SET NOCOUNT ON;select test='test';",
#           "dataStoreLogFile": "/usr/local/tomcat/logs/datastore.log",
#           "dataStoreInitConns": 10,
#           "dataStoreMaxConns": 100,
#           "dataStoreConnUsageLimit": 100,
#           "dataStoreLogLevel": "debug",
#           "maxUrlLength": 500}},
#       {
#         "servlet-name": "cofaxEmail",
#         "servlet-class": "org.cofax.cds.EmailServlet",
#         "init-param": {
#         "mailHost": "mail1",
#         "mailHostOverride": "mail2"}},
#       {
#         "servlet-name": "cofaxAdmin",
#         "servlet-class": "org.cofax.cds.AdminServlet"},
   
#       {
#         "servlet-name": "fileServlet",
#         "servlet-class": "org.cofax.cds.FileServlet"},
#       {
#         "servlet-name": "cofaxTools",
#         "servlet-class": "org.cofax.cms.CofaxToolsServlet",
#         "init-param": {
#           "templatePath": "toolstemplates/",
#           "log": 1,
#           "logLocation": "/usr/local/tomcat/logs/CofaxTools.log",
#           "logMaxSize": "",
#           "dataLog": 1,
#           "dataLogLocation": "/usr/local/tomcat/logs/dataLog.log",
#           "dataLogMaxSize": "",
#           "removePageCache": "/content/admin/remove?cache=pages&id=",
#           "removeTemplateCache": "/content/admin/remove?cache=templates&id=",
#           "fileTransferFolder": "/usr/local/tomcat/webapps/content/fileTransferFolder",
#           "lookInContext": 1,
#           "adminGroupID": 4,
#           "betaServer": True}}],
#     "servlet-mapping": {
#       "cofaxCDS": "/",
#       "cofaxEmail": "/cofaxutil/aemail/*",
#       "cofaxAdmin": "/admin/*",
#       "fileServlet": "/static/*",
#       "cofaxTools": "/tools/*"},
   
#     "taglib": {
#       "taglib-uri": "cofax.tld",
#       "taglib-location": "/WEB-INF/tlds/cofax.tld"}}}

#db.store_json('stringjson', j)
#print(db.get_file('json', './test.json'))
j = db.get_json('stringjson')
print(j['web-app']['servlet'][0]['servlet-name'])
print(j['web-app']['servlet'][1]["init-param"]['mailHost'])
#print(j['_ +'][1]['a'][0][1])

# ??? Multi part upload?
# ??? Can I leverage other imgur features, like descriptions, titles and albums? Some kind of metadata attached to files, or file groupings/directories?

# From user perspective:
# USER SUPPLIED KEY, FORMAT -> DATA IN SUPPLIED FORMAT
# USER SUPPLIED DATA, FORMAT, USER SUPPLIED KEY -> SET IMGUR ID to VALUE OF KEY

# Should be extensible to different datastore paradigms
# For development, just create a sqlitedict