import random

class Client:
    def __init__(self, proxy=None, timeout=15):
        self.proxies = {"http": proxy, "https": proxy}
        self.timeout = timeout
        
    async def post(self, url, json=None, timeout=None):
        import aiohttp
        
        timeout = timeout or self.timeout
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=json, proxy=self.proxies.get("https"), timeout=timeout) as response:
                    return ClientResponse(
                        status_code=response.status,
                        text=await response.text(),
                        json_data=await response.json() if response.headers.get('Content-Type') == 'application/json' else None
                    )
            except Exception as e:
                from .logger import logger
                logger.error(f"请求失败: {str(e)}")
                raise e
    
    async def close(self):
        # 简化版本不需要特殊的关闭操作
        pass


class ClientResponse:
    def __init__(self, status_code, text, json_data=None):
        self.status_code = status_code
        self._text = text
        self._json = json_data
        
    @property
    def text(self):
        return self._text
        
    def json(self):
        if self._json is not None:
            return self._json
        
        import json
        try:
            return json.loads(self._text)
        except:
            return {}
