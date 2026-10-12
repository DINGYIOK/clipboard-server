import logging

import tortoise.backends.asyncpg
from tortoise import Tortoise

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": "127.0.0.1",
                "port": 5432,
                "user": "postgres",
                "password": "123456",
                "database": "clipboard",
                "server_settings": {
                    "timezone": "Asia/Shanghai",  # 或 "CST"
                },
                # 连接池
                "minsize": 10,
                "maxsize": 100,
                "ssl": False,  # 添加这一行，明确禁用 SSL
            },
        },
    },
    "apps": {
        "models": {
            "models": ["app.models"],
            "default_connection": "default",
            "migrations": "app.migrations",
        },
    },
}


async def init_db():
    try:
        logging.info("🔍 正在初始化 Tortoise...")
        await Tortoise.init(config=TORTOISE_ORM, _enable_global_fallback=True)
        logging.info("✅ Tortoise 初始化成功！")
    except Exception as e:
        logging.info(f"❌ 初始化数据库错误：{e}")
        raise Exception(f"初始化数据库错误：{e}") from e


async def close_db():
    await Tortoise.close_connections()
