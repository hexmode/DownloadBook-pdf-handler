import os
from dotenv import load_dotenv  

load_dotenv()

# Define your credentials and MediaWiki API endpoint  
api_url = os.getenv("WIKI_API_URL") 
username = os.getenv("WIKI_USER")  
password = os.getenv("WIKI_PASS")
title = os.getenv("COLLECTION_TITLE")
verify = os.getenv("WIKI_CA_CERT", True)
URL_PREFIX = os.getenv("URL_PREFIX")

pages = [
    'Beacon_User_Guide/System_Requirements',
    'Beacon_User_Guide/Graph_Database',
    'Beacon_User_Guide/Access_Beacon',
    'Beacon_User_Guide/Graphs',
    'Beacon_User_Guide/Data_View',
    'Beacon_User_Guide/Run_Recipe',
    'Beacon_User_Guide/Lens',
    'Beacon_User_Guide/Organizational_Chart',
    'Beacon_User_Guide/Calc_Guided_View',
    'Beacon_User_Guide/Reports',
    'Beacon_User_Guide/Get_Help',
]
