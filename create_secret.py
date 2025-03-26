from pykis import KisAuth
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
# print(os.getenv("REAL_ACC_NO"))

auth = KisAuth(
    # HTS 로그인 ID
    id=os.getenv("HTS_ID"),
    # 앱 키
    appkey=os.getenv("REAL_APP_KEY"),
    # 앱 시크릿 키
    secretkey=os.getenv("REAL_APP_SECRET"),
    # 앱 키와 연결된 계좌번호
    account=os.getenv("REAL_ACC_NO"),
    # 모의투자 여부
    virtual=False,
)

# 안전한 경로에 시크릿 키를 파일로 저장합니다.
auth.save("secret.json")