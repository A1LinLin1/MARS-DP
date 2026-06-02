# target_b_api.py
from fastapi import FastAPI, Header, HTTPException
import uvicorn

app = FastAPI(title="模拟 SaaS 微服务 (靶场 B)")

# 模拟数据库：两个隔离的租户数据
FAKE_DB = {
    "1001": {"name": "Alice", "role": "user", "sensitive_data": "Alice的私人财务报表"},
    "1002": {"name": "Bob", "role": "admin", "sensitive_data": "Bob的SaaS核心机密数据"}
}

@app.get("/")
def read_root():
    return {"message": "SaaS API 服务运行中"}

# 模拟登录接口：返回身份 Token
@app.post("/api/v1/login/{user_id}")
def login(user_id: str):
    if user_id in FAKE_DB:
        # 极简模拟：给用户颁发一个固定的 Token
        return {"access_token": f"token_for_user_{user_id}"}
    raise HTTPException(status_code=404, detail="用户不存在")

# 核心漏洞接口：获取用户信息
@app.get("/api/v1/user/{target_user_id}/profile")
def get_user_profile(target_user_id: str, authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少 Authorization 头")
    
    # 【💣 严重漏洞点 (BOLA/IDOR)】：
    # 系统只检查了有没有 Token，但没有校验该 Token 是否属于 target_user_id！
    # 只要带着合法的 Token，就能随意遍历 target_user_id 获取其他人的数据。
    
    if target_user_id in FAKE_DB:
        return {"data": FAKE_DB[target_user_id]}
    raise HTTPException(status_code=404, detail="目标用户不存在")

if __name__ == "__main__":
    print("🚀 靶场 B (云原生 API) 启动在 http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)