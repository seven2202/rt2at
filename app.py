from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import os

# 导入token转换服务
from token_service import rt2ac

# 创建FastAPI应用
app = FastAPI(title="OpenAI Token 转换工具")

# 设置模板目录
templates = Jinja2Templates(directory="templates")

# 创建数据目录（如果不存在）
if not os.path.exists("data"):
    os.makedirs("data")

# 定义请求模型
class TokenRequest(BaseModel):
    refresh_token: str

# 首页路由
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Token转换API
@app.post("/api/convert")
async def convert_token(request: TokenRequest):
    try:
        # 调用token转换服务
        access_token = await rt2ac(request.refresh_token)
        return {"access_token": access_token}
    except Exception as e:
        # 处理错误
        raise HTTPException(status_code=500, detail=str(e))

# 启动应用
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
