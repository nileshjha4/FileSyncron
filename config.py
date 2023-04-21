import os
from dotenv import load_dotenv

load_dotenv()

USER_NAME = os.getenv('USER_NAME')
PASSWORD = os.getenv('PASSWORD')
REMOTE_PATH = os.getenv('REMOTE_PATH')
LOCAL_PATH = os.getenv('LOCAL_PATH')
