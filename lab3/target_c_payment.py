# target_c_payment.py
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="模拟金融电商核心支付链路 (靶场 C)")

# 模拟真实的商品库
PRODUCTS = {
    101: {"name": "企业级防火墙硬件", "real_price": 9999.00}
}

# 1. 模拟商业云 WAF (全局拦截器)
@app.middleware("http")
async def waf_middleware(request: Request, call_next):
    # 读取请求体进行 WAF 规则匹配
    body = await request.body()
    payload = body.decode("utf-8").upper()
    
    # 典型 SQLi 和 XSS 黑名单特征
    waf_keywords = ["SELECT", "UNION", "OR 1=1", "DROP", "<SCRIPT>", "SLEEP"]
    
    if any(keyword in payload for keyword in waf_keywords):
        print(f"🔴 [WAF 拦截] 检测到恶意特征: {payload}")
        # 直接阻断，返回 403
        return fastapi.responses.JSONResponse(
            status_code=403, 
            content={"error": "WAF: 您的请求包含恶意特征，已被拦截！"}
        )
    
    response = await call_next(request)
    return response

# 接收的支付数据模型
class CheckoutRequest(BaseModel):
    item_id: int
    price: float

# 2. 核心漏洞接口：支付核销 (业务逻辑缺陷)
@app.post("/api/v1/order/checkout")
async def checkout(order: CheckoutRequest):
    if order.item_id not in PRODUCTS:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    product = PRODUCTS[order.item_id]
    
    # 【💣 严重漏洞点 (业务逻辑篡改)】：
    # 后端竟然直接信任了前端传过来的 price 参数，没有和数据库里的 real_price 进行比对！
    if order.price <= 0:
        raise HTTPException(status_code=400, detail="金额不能为负数或零")
    
    if order.price < product["real_price"]:
        print(f"⚠️ [高危警报] 订单异常生成！原价 {product['real_price']}，实付 {order.price}")
        return {
            "status": "success", 
            "message": f"支付成功！您以 {order.price} 元购买了价值 {product['real_price']} 元的 {product['name']}",
            "danger_level": "CRITICAL"
        }
    
    return {"status": "success", "message": "支付成功，金额正常。"}

if __name__ == "__main__":
    import fastapi.responses
    print("🚀 靶场 C (带 WAF 的金融支付) 启动在 http://127.0.0.1:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001)