# -*- coding: utf-8 -*-
"""登录模块：仅支持 Cookie/Token 登录（手动粘贴 Token）

用户在自己浏览器登录 i志愿官网后，从 Cookie 中提取 IZYZ_org_token
粘贴到工具，工具保存到 token.json，后续所有接口调用带上
Authorization: Bearer <token>。
"""
import json
import os
import time

from config import TOKEN_FILE


def load_token() -> str | None:
    """读取本地保存的 token"""
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        token = data.get("token") or ""
        return token if token else None
    except Exception:
        return None


def save_token(token: str):
    """保存 token 到本地文件"""
    data = {"token": token, "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def clear_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)


def set_token_manual(token: str) -> bool:
    """手动粘贴 token（唯一登录方式）"""
    token = (token or "").strip().strip('"').strip("'")
    if not token:
        return False
    save_token(token)
    return True


if __name__ == "__main__":
    print("登录模块（仅 Token 粘贴方式）")
