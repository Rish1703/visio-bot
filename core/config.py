import os
from dotenv import load_dotenv
from supabase import create_client, Client
import openai

load_dotenv()

TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN")
DID_API_KEY = os.getenv("DID_API_KEY")
FREE_LIMIT = 5

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
openai.api_key = OPENAI_API_KEY
