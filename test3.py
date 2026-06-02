import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from langchain_openai import ChatOpenAI

# ==========================================
# 0. 环境与配置初始化
# ==========================================
# 加载 .env 文件中的环境变量
load_dotenv()

# 初始化 DeepSeek 模型
llm = LLM(
    model="openai/deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1", # 标准的兼容接口需要带上 /v1
    temperature=0.2,
    max_tokens=4096
)

# ==========================================
# 1. 定义安全评估工具 (Tools)
# ==========================================
@tool("ReconTool")
def recon_tool(target_url: str) -> str:
    """用于探测目标架构和 WAF 指纹。输入目标 URL，返回资产架构信息。"""
    return (f"[模拟侦察结果] 目标 {target_url} 是一家大型金融电商平台。\n"
            f"架构：Java Spring Boot + K8s集群。\n"
            f"防护：前端部署了严格的商业云 WAF（如阿里云WAF/Cloudflare），会拦截所有常规 SQLi 和 XSS 探针。\n"
            f"高价值端点：发现暴露的支付核销接口 POST /api/v1/order/checkout。\n"
            f"参数结构推测：该接口接收 JSON 格式数据，包含 item_id (商品ID) 和 price (支付金额)。")

@tool("SafeGatewayTool")
def safe_gateway_tool(payload: str) -> str:
    """无损安全网关与 WAF 模拟器。输入测试 Payload，返回系统回显。"""
    
    # 1. 模拟商业 WAF 的特征拦截
    waf_keywords = ["SELECT", "UNION", "OR", "AND", "DROP", "SCRIPT", "1=1", "SLEEP"]
    if any(keyword in payload.upper() for keyword in waf_keywords):
        return "【WAF 拦截】HTTP 403 Forbidden。您的请求包含恶意特征，已被安全组件拦截并封禁IP！"
    
    # 2. 模拟无损网关的安全底线
    if "DELETE" in payload.upper() or "TRUNCATE" in payload.upper():
        return "【无损网关拦截】警告：检测到破坏性指令，操作已被拦截！"
    
    # 3. 模拟业务逻辑漏洞（支付参数篡改）
    if "price" in payload.lower() and ("0.01" in payload or "-" in payload):
        return ("【网关放行】HTTP 200 OK。系统回显：订单生成成功！"
                "警告：后端未对 price 参数与商品原价进行一致性校验，"
                "您已成功使用篡改后的极低金额拉起了支付网关！")
    
    return "【网关放行】HTTP 200 OK。系统回显：常规参数验证失败或订单按原价生成。"

# ==========================================
# 2. 实例化 Agents (注入完整提示词)
# ==========================================
recon_agent = Agent(
    role='高级数字资产架构师与侦察专家',
    goal='提取目标系统的业务拓扑与API端点暴露面',
    backstory=(
        "你是一个顶级的企业 IT 架构分析师。你的任务是分析目标 URL，"
        "识别其底层技术栈、WAF 防护类型、以及暴露的 RESTful API 端点和鉴权机制。"
        "你需要客观、准确地描绘目标的数字暴露面图谱。"
    ),
    tools=[recon_tool],
    llm=llm,
    allow_delegation=False,
    verbose=True # 开启日志，方便你写论文时提取智能体的思考过程
)

verify_agent = Agent(
    role='高级安全逻辑验证与渗透专家',
    goal='进行多步逻辑推演与无损可利用性验证',
    backstory=(
        "你是一个具备极高职业操守的高级白帽黑客。你需要基于前置的资产画像，"
        "推理出可能的攻击路径（如 API 越权、支付逻辑篡改、SQL注入变种检测）。"
        "【最高指令】：你被严格限制在 SafeGatewayTool 网关内操作，严禁执行破坏性指令。"
        "请描述你的验证步骤、生成无损的 Payload，并评估漏洞真实利用成功率。"
    ),
    tools=[safe_gateway_tool],
    llm=llm,
    allow_delegation=False,
    verbose=True
)

audit_agent = Agent(
    role='网络安全精算师与风险评估官',
    goal='将技术风险转化为动态风险得分 (DRS) 并给出保险定价建议',
    backstory=(
        "你是一位精通网络安全与金融精算的双料专家。你接收到验证报告后需要：\n"
        "1. 判定资产权重（如：涉及支付数据的权重设为 0.9）。\n"
        "2. 结合攻击路径的利用成功率与资产权重，计算 0-100 的动态风险得分 (DRS)。\n"
        "3. 根据 DRS 给出明确的保费调整倍数或拒保建议。"
    ),
    llm=llm,
    allow_delegation=False,
    verbose=True
)

# ==========================================
# 3. 实例化 Tasks (任务依赖链条)
# ==========================================
task_recon = Task(
    description='对目标 {target_url} 调用侦察工具进行架构收集。',
    expected_output='包含技术栈、API端点、WAF指纹的资产报告。',
    agent=recon_agent
)

task_verify = Task(
    description='基于侦察报告，针对 {business_type} 尝试调用安全网关进行逻辑绕过与无损验证。',
    expected_output='攻击路径报告，包含绕过策略、拦截情况及利用成功率。',
    agent=verify_agent,
    dependencies=[task_recon]
)

task_audit = Task(
    description='综合漏洞真实验证情况与资产价值，推演并计算该企业的动态风险得分 (DRS)。',
    expected_output='详细的精算报告，包含 DRS 计算逻辑与最终动态保费建议。',
    agent=audit_agent,
    dependencies=[task_verify]
)

# ==========================================
# 4. 组建 Crew 并启动
# ==========================================
insurance_assessment_crew = Crew(
    agents=[recon_agent, verify_agent, audit_agent],
    tasks=[task_recon, task_verify, task_audit],
    process=Process.sequential, 
    verbose=True
)

if __name__ == "__main__":
    print("🚀 正在启动 MARS-DP 挑战靶场 C (带 WAF 的金融电商)...\n")
    
    # 模拟启动对靶场 C（极高价值资产）的动态评估
    result = insurance_assessment_crew.kickoff(inputs={
        'target_url': 'http://127.0.0.1:8001',
        'business_type': '金融电商核心支付与清算链路（涉及企业核心资金池，极高价值资产）'
    })

    # 将评估结果写入 Markdown 报告文件（覆盖同名文件）
    import os
    from datetime import datetime
    report_path = os.path.join(os.path.dirname(__file__), "最终报告_靶场C.md")
    report_content = (
        f"# 最终精算报告 (靶场C)\n\n"
        f"**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"## 评估结果\n\n"
        f"{result}\n"
    )
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"\n✅ 靶场 C 评估完成！报告已保存为：{report_path}")