from os import getenv

from dotenv import load_dotenv

load_dotenv()

API_ID = "6435225"
# -------------------------------------------------------------
API_HASH = "4e984ea35f854762dcde906dce426c2d"
# --------------------------------------------------------------
BOT_TOKEN = getenv("BOT_TOKEN", "6956731651:AAH3aSvIbZnV1e_jURbs1CFFZJmzQ3Q80_Y")
STRING1 = getenv("STRING_SESSION", None)
MONGO_URL = getenv("MONGO_URL", "mongodb+srv://Movieclone:movie12321@cluster0.bsbne.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
OWNER_ID = int(getenv("OWNER_ID", "5738579437"))
SUPPORT_GRP = "Ur_support07"
UPDATE_CHNL = "Ur_rishu_143"
OWNER_USERNAME = "TheRishuCoder"
