import os
from dotenv import load_dotenv

load_dotenv()

# 활성 프로필 (REAL1 / REAL2 / MOCK1)
KIWOOM_ACTIVE_PROFILE = os.getenv("KIWOOM_ACTIVE_PROFILE", "MOCK1")

_profile = KIWOOM_ACTIVE_PROFILE
KIWOOM_APP_KEY = os.getenv(f"KIWOOM_{_profile}_APP_KEY", "")
KIWOOM_SECRET_KEY = os.getenv(f"KIWOOM_{_profile}_SECRET_KEY", "")
KIWOOM_ACCOUNT = os.getenv(f"KIWOOM_{_profile}_ACCOUNT", "")
KIWOOM_IS_MOCK = os.getenv(f"KIWOOM_{_profile}_IS_MOCK", "true").lower() == "true"

# 키움 API URL
KIWOOM_REAL_URL = "https://api.kiwoom.com"
KIWOOM_MOCK_URL = "https://mockapi.kiwoom.com"
KIWOOM_HOST_URL = KIWOOM_MOCK_URL if KIWOOM_IS_MOCK else KIWOOM_REAL_URL

# 웹소켓 URL
KIWOOM_REAL_WS_URL = "wss://api.kiwoom.com:10000"
KIWOOM_MOCK_WS_URL = "wss://mockapi.kiwoom.com:10000"
KIWOOM_WS_URL = KIWOOM_MOCK_WS_URL if KIWOOM_IS_MOCK else KIWOOM_REAL_WS_URL

# 텔레그램 설정
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
