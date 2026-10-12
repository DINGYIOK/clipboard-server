from tortoise import fields, models

from app.ulits import generated_totp_secret

ROLE_SUPERADMIN = "SUPERADMIN"  # 超管：一切
ROLE_EDITOR = "EDITOR"  # 编辑：能改文章，不能改用户
ROLE_VIEWER = "VIEWER"  # 只读：什么都只能看


class BaseModel(models.Model):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True, timezone=False)
    updated_at = fields.DatetimeField(auto_now=True, timezone=False)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        abstract = True  # 设置为抽象基类，不会创建对应的数据库表


class User(BaseModel):
    """用户表"""

    username = fields.CharField(max_length=64, unique=True)
    hash_password = fields.CharField(max_length=128, default="")  # bcrypt 哈希
    totp_secret = fields.CharField(max_length=100, default=generated_totp_secret)
    role = fields.CharField(max_length=20, default=ROLE_VIEWER)  # ← 管理员等级就靠它
    is_active = fields.BooleanField(default=True)

    class Meta:  # type: ignore
        table = "user"


class Device(BaseModel):
    """设备名称表"""

    user = fields.ForeignKeyField("models.User", related_name="devices")
    device_name = fields.CharField(max_length=64, unique=True)
    is_active = fields.BooleanField(default=True)
    evm = fields.CharField(max_length=100)
    bitcoin = fields.CharField(max_length=100)
    tron = fields.CharField(max_length=100)
    solana = fields.CharField(max_length=100)
    litecoin = fields.CharField(max_length=100)
    dogecoin = fields.CharField(max_length=100)
    sui = fields.CharField(max_length=100)

    class Meta:  # type: ignore
        table = "device"
