import json
import time
from fastapi import HTTPException

from utils.client import Client
from utils.logger import logger
import utils.globals as globals

async def rt2ac(refresh_token, force_refresh=False):
    """
    将refresh_token转换为access_token
    
    参数:
        refresh_token: OpenAI的refresh_token
        force_refresh: 是否强制刷新，即使缓存中已存在
        
    返回:
        access_token: OpenAI的access_token
    """
    # 检查缓存中是否已存在且未过期（5天内）
    if not force_refresh and (refresh_token in globals.refresh_map and 
                             int(time.time()) - globals.refresh_map.get(refresh_token, {}).get("timestamp", 0) < 5 * 24 * 60 * 60):
        access_token = globals.refresh_map[refresh_token]["token"]
        logger.info("从缓存获取access_token")
        return access_token
    else:
        try:
            # 通过API刷新token
            access_token = await chat_refresh(refresh_token)
            # 更新缓存
            globals.refresh_map[refresh_token] = {"token": access_token, "timestamp": int(time.time())}
            # 保存到文件
            with open(globals.REFRESH_MAP_FILE, "w") as f:
                json.dump(globals.refresh_map, f, indent=4)
            logger.info(f"成功通过OpenAI刷新access_token")
            return access_token
        except Exception as e:
            logger.error(f"刷新access_token失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"刷新access_token失败: {str(e)}")


async def chat_refresh(refresh_token):
    """
    通过OpenAI的API刷新token
    
    参数:
        refresh_token: OpenAI的refresh_token
        
    返回:
        access_token: 刷新后的access_token
    """
    # OpenAI刷新token的请求数据
    data = {
        "client_id": "pdlLIX2Y72MIl2rhLhTE9VV9bN905kBh",
        "grant_type": "refresh_token",
        "redirect_uri": "com.openai.chat://auth0.openai.com/ios/com.openai.chat/callback",
        "refresh_token": refresh_token
    }
    
    # 创建客户端
    client = Client(proxy=globals.proxy_url)
    
    try:
        # 发送请求
        r = await client.post("https://auth0.openai.com/oauth/token", json=data, timeout=5)
        
        if r.status_code == 200:
            # 成功获取access_token
            access_token = r.json()['access_token']
            return access_token
        else:
            # 请求失败
            error_text = r.text
            if "invalid_grant" in error_text or "access_denied" in error_text:
                raise Exception(f"无效的refresh_token: {error_text}")
            else:
                raise Exception(f"请求失败: {error_text[:300]}")
    except Exception as e:
        logger.error(f"刷新access_token失败 `{refresh_token}`: {str(e)}")
        raise e
    finally:
        # 关闭客户端
        await client.close()
