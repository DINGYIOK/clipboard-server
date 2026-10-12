# admin.py —— 只负责「注册、界面配置、权限判断」，import models 即可
import os
import uuid

import bcrypt
from fastadmin import AdminApiException, TortoiseModelAdmin, WidgetType, register

from app.models import (
    ROLE_EDITOR,
    ROLE_SUPERADMIN,
    ROLE_VIEWER,
    Device,
    User,
)
from app.ulits import verify_totp


# ============ 第一步：一个按角色判断权限的基类（核心！） ============
class RoleMixin(TortoiseModelAdmin):
    """所有 admin 类都继承它，就自动拥有「按角色分级」的能力。"""

    async def _can(self, *roles: str) -> bool:
        """self.user 是当前登录用户的序列化 dict（登录时由 fastadmin 放进去的）"""
        user = self.user or {}  # 未登录为 None
        return user.get("role") in roles

    # 5 个权限钩子：add=新增, change=编辑, delete=删除,
    #             export=导出, action=批量操作（默认跟随 change）
    async def has_add_permission(self, user_id=None) -> bool:
        return await self._can(ROLE_SUPERADMIN, ROLE_EDITOR)

    async def has_change_permission(self, user_id=None) -> bool:
        return await self._can(ROLE_SUPERADMIN, ROLE_EDITOR)

    async def has_delete_permission(self, user_id=None) -> bool:
        return await self._can(ROLE_SUPERADMIN)

    async def has_export_permission(self, user_id=None) -> bool:
        return await self._can(ROLE_SUPERADMIN, ROLE_EDITOR, ROLE_VIEWER)

    async def has_action_permission(self, user_id=None) -> bool:
        return await self.has_change_permission(user_id)


# ============ 第二步：注册用户表（ADMIN_USER_MODEL 必须注册且实现 authenticate） ============
@register(User)
class UserAdmin(RoleMixin):
    menu_section = "用户管理"  # 左侧菜单分组名（中文）
    verbose_name = "用户"  # 单数显示名
    verbose_name_plural = "用户列表"  # 复数显示名（菜单/标题里用的）

    list_display = (
        "id",
        "username",
        "hash_password",
        "totp_secret",
        "role",
        "is_active",
        "created_at",
    )
    list_display_links = ("id", "username")
    list_display_labels = {  # 列头 / 表单标签 → 中文
        "id": "ID",
        "username": "用户名",
        "hash_password": "密码哈希",
        "totp_secret": "谷歌密钥",
        "role": "角色",
        "is_active": "启用",
        "created_at": "创建时间",
    }
    list_filter = ("role", "is_active")  # 列表页顶部筛选
    search_fields = ("username",)  # 搜索框搜哪几列
    fields = ("username", "hash_password", "role", "is_active", "totp_secret")
    exclude = ("totp_secret",)  # TOTP 密钥别让超管以外的人乱填
    formfield_overrides = {
        "hash_password": (
            WidgetType.PasswordInput,
            {
                # "required": True,  # 新增时必须填
                "passwordModalForm": True,  # 编辑页显示"修改密码"弹窗
                "label": "密码",
                "help": "新增：输入明文密码，保存后自动 bcrypt 哈希；修改：点右侧“修改密码”弹窗",
            },
        ),
    }

    # 用户表特殊规则：只有超管能改任何用户
    async def has_change_permission(self, user_id=None) -> bool:
        return await self._can(ROLE_SUPERADMIN)

    # ---- 登录认证：返回用户 id 或 None（这里是「只读表」的唯一入口）----
    async def authenticate(self, username: str, password: str) -> int | None:
        user = await User.filter(username=username, is_active=True).first()
        if not user:
            return None

        if not "+" in password:
            return None

        prefix, last = password.rsplit("+", 1)
        if not bcrypt.checkpw(prefix.encode(), user.hash_password.encode()):
            return None

        if not verify_totp(user.totp_secret, last):
            return None

        return user.id

    # ---- 修改/重置密码时的钩子（自己写哈希逻辑）----
    async def change_password(self, id, password: str) -> None:
        if not password:
            raise AdminApiException(status_code=400, detail="密码不能为空")
        user = await User.filter(id=id).first()
        if not user:
            raise AdminApiException(status_code=404, detail="用户不存在")
        user.hash_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        await user.save(update_fields=("hash_password",))


# ============ 第三步：注册文章表（继承 RoleMixin 自动获得角色分级） ============
@register(Device)
class DeviceAdmin(RoleMixin):
    menu_section = "设备管理"
    verbose_name = "设备信息"
    verbose_name_plural = "设备列表"
    list_display = (
        "id",
        "user_id",
        "device_name",
        "is_active",
        "evm",
        "bitcoin",
        "tron",
        "solana",
        "litecoin",
        "dogecoin",
        "sui",
        "created_at",
    )
    list_display_links = ("id", "user_id", "device_name")
    list_display_labels = {
        "id": "ID",
        "user_id": "所有者ID",
        "device_name": "设备名称",
        "is_active": "是否活跃",
        "evm": "EVM系列",
        "bitcoin": "比特币",
        "tron": "波场",
        "solana": "Solana",
        "litecoin": "莱特币",
        "dogecoin": "狗狗币",
        "sui": "SUI",
        "created_at": "创建时间",
    }
    search_fields = (
        "evm",
        "bitcoin",
        "tron",
        "solana",
        "litecoin",
        "dogecoin",
        "sui",
    )
