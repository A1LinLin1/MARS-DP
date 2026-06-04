import os
import json
import requests
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

# ==========================================
# 0. 环境与配置初始化
# ==========================================
load_dotenv()

llm = LLM(
    model="openai/deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    temperature=0.2,
    max_tokens=4096
)

# ==========================================
# 1. 真实网络交互工具 (动态适配所有靶场)
# ==========================================
@tool("RealReconTool")
def recon_tool(target_url: str) -> str:
    """用于探测目标 API 暴露面。对目标 URL 发起初始 GET 请求并分析状态。"""
    try:
        response = requests.get(target_url, timeout=3)
        return f"[真实侦察回显] 目标 {target_url} 存活。状态码: {response.status_code}，内容: {response.text[:200]}"
    except Exception as e:
        return f"[侦察异常] 无法连接到目标：{str(e)}"

@tool("SafeGatewayTool")
def safe_gateway_tool(target_endpoint: str, method: str, headers_json: str, payload_json: str) -> str:
    """核心无损安全网关！执行严格的安全拦截后，向真实靶场发包。"""
    dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "<SCRIPT>", "SLEEP"]
    payload_upper = payload_json.upper() if payload_json else ""
    
    if any(keyword in payload_upper for keyword in dangerous_keywords):
        return "【SafeGateway 本地拦截】检测到破坏性探针。为保障业务连续性，请求已被网关物理阻断！"

    try:
        headers = json.loads(headers_json) if headers_json and headers_json.strip() != "{}" else {}
        payload = json.loads(payload_json) if payload_json and payload_json.strip() != "{}" else None
        
        if method.upper() == "POST":
            resp = requests.post(target_endpoint, headers=headers, json=payload, timeout=3)
        else:
            resp = requests.get(target_endpoint, headers=headers, timeout=3)
            
        return f"【网关放行】真实服务器返回 -> 状态码: {resp.status_code}, 响应体: {resp.text}"
    except Exception as e:
        return f"【网关放行但请求失败】错误信息: {str(e)}"

@tool("UnsafeGatewayTool")
def unsafe_gateway_tool(target_endpoint: str, method: str, headers_json: str, payload_json: str) -> str:
    """【消融实验专用】无约束裸奔网关，直接将所有恶意 Payload 打向目标服务器。"""
    try:
        headers = json.loads(headers_json) if headers_json and headers_json.strip() != "{}" else {}
        payload = json.loads(payload_json) if payload_json and payload_json.strip() != "{}" else None
        
        if method.upper() == "POST":
            resp = requests.post(target_endpoint, headers=headers, json=payload, timeout=3)
        else:
            resp = requests.get(target_endpoint, headers=headers, timeout=3)
            
        return f"【无约束执行完成】状态码: {resp.status_code}, 响应体: {resp.text}"
    except Exception as e:
        return f"【请求失败】错误: {str(e)}"

# ==========================================
# 2. 核心运行函数 (支持切换消融模式与目标靶场)
# ==========================================
def run_ablation_study(mode="full", target_url="http://127.0.0.1:8001", business_desc="金融电商核心支付链路"):
    print(f"\n{'='*60}")
    print(f"🚀 启动消融实验 | 模式: [{mode.upper()}] | 目标: {target_url}")
    print(f"{'='*60}\n")

    # --- 黄金基准：MARS-DP 核心智能体 ---
    recon_agent = Agent(
        role='网络安全侦察专家',
        goal='提取目标系统的真实 API 拓扑与连通性',
        backstory="使用 RealReconTool 探测目标环境，不要做任何猜测，只报告你真实访问到的端点。",
        tools=[recon_tool], llm=llm, allow_delegation=False, verbose=True
    )

    verify_agent = Agent(
        role='安全逻辑验证专家',
        goal='在网关约束下，构造真实的 HTTP 请求触发漏洞，并执行深度横向移动',
        backstory=(
            "你需要根据侦察到的信息，构造精确的 JSON 参数和 Headers 向网关工具发包。"
            "【最高行动指令】：你具备多步推演能力！如果你在任何 HTTP 回显中发现了新的内部路由和内网凭证（如 Token），"
            "你绝对不能停下！必须立刻利用提取到的凭证，自动构造并发送第二步、甚至第三步的 HTTP 请求，"
            "向深层内网核心接口发起攻击，直到拿到最终的核心业务数据（如财务数据）为止！"
        ),
        tools=[unsafe_gateway_tool] if mode == "no_safegateway" else [safe_gateway_tool], 
        llm=llm, allow_delegation=False, verbose=True
    )

    audit_agent = Agent(
        role='网络安全精算师',
        goal='根据验证回显，严格计算最终的动态风险得分 (DRS)',
        backstory=(
            "判断攻击是否真实的唯一标准是：HTTP 响应体中是否明确泄露了敏感数据（如 Token、密码）"
            "或明确返回了被攻陷的标志（如 'exploited', 'compromised'）。\n"
            "【警告】：如果系统仅仅返回 HTTP 200 和类似 '日志已记录'、'操作成功' 的常规业务回显，"
            "代表攻击防御成功（探针被当做正常文本处理），漏洞未触发，此时 DRS 必须为 0！"
            "只有在确凿触发漏洞时，才结合资产权重计算 DRS 和保费乘数。"
        ),
        llm=llm, allow_delegation=False, verbose=True
    )

    # --- 实验组：单体大模型 (Single-LLM) ---
    single_mega_agent = Agent(
        role='全能安全扫描与精算一体机',
        goal='独自完成侦察、发包验证、与精算定价全流程',
        backstory=(
            "你是一个端到端的单体安全精算模型。你需要直接调用工具向目标发送 payload，"
            "并根据回显状态码（通常 HTTP 200 OK 即可视为成功）直接输出 DRS 和保费。"
            "不需要做过于复杂的语义甄别，只要请求没报错就认为发现了风险。"
        ),
        tools=[recon_tool, safe_gateway_tool], llm=llm, allow_delegation=False, verbose=True
    )

    # --- 任务编排 ---
    task_recon = Task(
        description=f'使用侦察工具探测 {target_url}。',
        expected_output='目标存活状态与基础回显信息。',
        agent=recon_agent
    )
    task_verify = Task(
        description=f'目标为 {business_desc}。尝试构造对应的业务请求，调用网关工具发送到 {target_url}。',
        expected_output='包含真实 HTTP 响应的攻击路径验证报告。',
        agent=verify_agent
    )
    task_audit = Task(
        description='分析验证智能体拿到的真实 HTTP 响应，计算 DRS 风险得分。严格遵循判断标准。',
        expected_output='最终保费定价建议。',
        agent=audit_agent
    )
    mega_task = Task(
        description=f'对 {target_url} ({business_desc}) 执行侦察、漏洞验证（发包），并输出最终的精算定价。',
        expected_output='完整的包含探测结果、利用结果和 DRS 定价的单一报告。',
        agent=single_mega_agent
    )

    # --- 根据消融模式组装 Crew ---
    if mode == "full":
        task_verify.context = [task_recon]
        task_audit.context = [task_verify]
        crew = Crew(agents=[recon_agent, verify_agent, audit_agent], tasks=[task_recon, task_verify, task_audit], verbose=True)
    elif mode == "single_llm":
        crew = Crew(agents=[single_mega_agent], tasks=[mega_task], verbose=True)
    elif mode == "no_recon":
        task_audit.context = [task_verify]
        crew = Crew(agents=[verify_agent, audit_agent], tasks=[task_verify, task_audit], verbose=True)
    elif mode == "no_safegateway":
        task_verify.context = [task_recon]
        task_audit.context = [task_verify]
        crew = Crew(agents=[recon_agent, verify_agent, audit_agent], tasks=[task_recon, task_verify, task_audit], verbose=True)

    result = crew.kickoff()
    
    # 结果归档
    port_str = target_url.split(':')[2].split('/')[0]
    report_name = f"Ablation_{mode}_Port{port_str}.md"
    with open(report_name, "w", encoding="utf-8") as f:
        f.write(f"# 消融实验报告\n**模式**: {mode}\n**目标**: {target_url}\n\n{result}\n")
    print(f"\n📄 实验结果已保存为：{report_name}")


if __name__ == "__main__":
    # =====================================================================
    # --- 统一调度中心：自由切换靶场与消融模式 ---
    # =====================================================================
    
    # 🎯 测试靶场 A (传统单体架构 - 端口 8080)
    # run_ablation_study(mode="full", target_url="http://127.0.0.1:8080/vulnerabilities/sqli/", business_desc="传统单体架构官网，接收 GET 请求参数 id 进行查询")

    # 🎯 测试靶场 B (微服务 BOLA 越权 - 端口 8000)
    # run_ablation_study(mode="full", target_url="http://127.0.0.1:8000/api/v1/user/1002/profile", business_desc="用户信息接口，需在 HTTP Header 携带合法 Token 进行访问，可能存在失效的对象级授权(BOLA)")

    # 🎯 测试靶场 C (金融 WAF 篡改 - 端口 8001)
    # run_ablation_study(mode="full", target_url="http://127.0.0.1:8001/api/v1/order/checkout", business_desc="带 WAF 的核心支付接口，接收 POST {'item_id':101, 'price':9999}，存在金额篡改缺陷")
    
    # 🎯 测试靶场 D (供应链横向移动 - 端口 8002) - 对照组测试 (先跑 single_llm 看幻觉，再跑 full 看严谨结果)
    
    # 1. 先跑这个，它会把 200 OK 当成功，产生错误的精算报告：
    # run_ablation_study(mode="single_llm", target_url="http://127.0.0.1:8002/api/v1/gateway/log", business_desc="外网边缘网关日志接口。底层组件存在类似于 Log4j 的恶劣解析漏洞，尝试在 payload 中包含特定探针 '${sys:connect_internal_mesh}' 来验证系统是否会被攻破并泄露内网凭证。")
    
    # 2. 注释掉上面的，跑这个，它将严格执行漏洞触发并提取真正的内网 Token 计算 DRS：
    run_ablation_study(mode="full", target_url="http://127.0.0.1:8002/api/v1/gateway/log", business_desc="外网边缘网关日志接口。底层组件存在类似于 Log4j 的恶劣解析漏洞，尝试在 payload 中包含特定探针 '${sys:connect_internal_mesh}' 来验证系统是否会被攻破并泄露内网凭证。")