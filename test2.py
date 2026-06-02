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
    return (f"[模拟侦察结果] 目标 {target_url} 采用现代云原生微服务架构 (FastAPI)。"
            f"未检测到 WAF。暴露了以下 RESTful API：\n"
            f"1. POST /api/v1/login/{{user_id}} (返回 access_token)\n"
            f"2. GET /api/v1/user/{{target_user_id}}/profile (需要 Header: Authorization: token_xxx)\n"
            f"提示：系统存在两个已知用户ID：1001 (普通用户) 和 1002 (高权限租户)。")

@tool("SafeGatewayTool")
def safe_gateway_tool(payload: str) -> str:
    """无损安全网关。输入测试 Payload（如状态探测语句或越权 Token），返回系统回显。"""
    # 真实实验中，这里将部署极其严格的 AST 解析或正则黑名单
    dangerous_keywords = ["DROP", "DELETE", "UPDATE", "TRUNCATE"]
    
    if any(keyword in payload.upper() for keyword in dangerous_keywords):
        return "【网关拦截】警告：检测到破坏性指令，根据无损验证原则，该操作已被网关强行拦截！"
    
    return "【网关放行】HTTP 200 OK。捕获到目标逻辑响应，验证测试成功落地。"

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
    print("🚀 正在启动多智能体网络安全保险评估系统...\n")
    
    # 模拟启动对靶场 B（SaaS 云原生，中高价值资产）的动态评估
    result = insurance_assessment_crew.kickoff(inputs={
        'target_url': 'http://127.0.0.1:8000',
        'business_type': 'SaaS云原生平台租户隔离数据（涉及中高价值的企业隐私数据，核心业务）'
    })

    # 将评估结果写入 Markdown 报告文件（覆盖同名文件）
    from datetime import datetime
    report_path = os.path.join(os.path.dirname(__file__), "最终报告2.md")
    report_content = (
        f"# 最终精算报告\n\n"
        f"**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"## 评估结果\n\n"
        f"{result}\n"
    )
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    # 仅输出简短确认信息（不打印完整结果）
    print(f"📄 报告已保存为：{report_path}")