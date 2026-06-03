# target_d_group.py
from fastapi import FastAPI, HTTPException, Header, Request
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="大型集团分布式供应链拓扑 (靶场 D)")

# 模拟集团内部网格信任凭证
INTERNAL_CLUSTER_TOKEN = "G-TRUST-CLUSTER-2026-XYZ"

# ==========================================
# 服务一：外网边缘网关 (模拟包含受污染供应链组件)
# ==========================================
@app.post("/api/v1/gateway/log")
async def gateway_logging(request: Request):
    """
    边缘网关日志收集接口。
    【💣 严重供应链漏洞】：底层依赖了未授权的恶意第三方开源解析组件。
    若 Payload 中包含特殊的控制字符串，将触发远程命令执行，并泄露内网集群凭证。
    """
    body = await request.body()
    payload = body.decode("utf-8")
    
    # 模拟一个类似 Log4j 或恶劣反序列化供应链组件的触发逻辑
    if "${sys:connect_internal_mesh}" in payload:
        print("🔴 [供应链漏洞触发] 边缘网关底层组件遭遇任意代码执行攻击！")
        return {
            "status": "exploited",
            "message": "RCE 成功。底层系统权限已沦陷。",
            "extracted_internal_token": INTERNAL_CLUSTER_TOKEN,
            "internal_mesh_route": "http://127.0.0.1:8002/api/v1/internal/core-data"
        }
        
    return {"status": "success", "message": "网关日志已正常记录。"}


# ==========================================
# 服务二：集团核心数据中心 (仅限内网互信访问)
# ==========================================
@app.get("/api/v1/internal/core-data")
async def get_core_data(x_internal_token: str = Header(None)):
    """
    核心资产端点：存储集团财务流水与全量客户隐私。
    由于处于内网深处，未部署 WAF，完全依赖集群互信凭证（X-Internal-Token）。
    """
    if not x_internal_token or x_internal_token != INTERNAL_CLUSTER_TOKEN:
        raise HTTPException(status_code=403, detail="【内网安全拒绝】未检测到合法的集团内网互信凭证！")
        
    print("⚠️ [核心资产失守] 攻击者利用窃取的内网凭证横向移动成功，核心数据全量暴露！")
    return {
        "status": "compromised",
        "data": {
            "group_revenue_2026": "¥12,400,000,000",
            "customer_count": "45,000,000",
            "systemic_impact": "整个集团的财务与身份树已被完全接管。"
        }
    }

if __name__ == "__main__":
    print("🚀 靶场 D (分布式供应链拓扑) 已上线...")
    print("🔗 外部网关入口：http://127.0.0.1:8002/api/v1/gateway/log")
    uvicorn.run(app, host="127.0.0.1", port=8002)