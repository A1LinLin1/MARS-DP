# MARS-DP (Multi-Agent Risk System for Dynamic Pricing) 🛡️📊

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/Powered%20by-CrewAI-orange.svg)](https://crewai.com/)
[![LLM: DeepSeek](https://img.shields.io/badge/LLM-DeepSeek-black.svg)](https://www.deepseek.com/)

**MARS-DP** 是一个基于大语言模型（LLM）驱动的多智能体协同 Web 风险评估与网络安全保险动态定价系统。

本项目旨在解决传统自动化扫描工具（如 Nessus、AWVS）在面对现代云原生架构和复杂业务逻辑时产生的高误报率问题。通过引入多智能体协同推理与“无损安全网关（SafeGateway）”，系统能够自动化推演 API 越权、逻辑篡改及高隐蔽性攻击路径，并将技术风险精准映射为保险精算的动态保费。

---

## ✨ 核心特性 (Key Features)

* **🤖 多智能体协同 (Multi-Agent Orchestration)**
  解耦传统扫描器的线性逻辑，构建了 Recon（侦察）、Verify（验证）、Audit（审计）三大智能体，实现“发现-验证-定价”的闭环。
* **🛡️ 无损安全验证 (SafeGateway Verification)**
  内置严格的 AST/正则中间件网关，限制大模型的破坏性指令（如 `DROP`、`DELETE`），确保漏洞深度验证过程不影响目标业务的连续性，满足保险核保红线。
* **🧠 复杂业务逻辑推演 (Business Logic Deduction)**
  有效检测现代微服务架构中的 API 越权（BOLA/IDOR）、支付逻辑漏洞以及高隐蔽性 SQL 注入变种，克服静态规则扫描的盲区。
* **💰 动态精算映射 (Actuarial Mapping)**
  结合多步攻击路径成功率与核心资产权重（$W_{asset}$），自动计算动态风险得分（DRS, Dynamic Risk Score），直接赋能网络安全保险的费率厘定。

---

## 🏗️ 系统架构 (Architecture)

1. **Recon Agent (侦察智能体)**：动态提取目标系统的业务拓扑、API 暴露面及 WAF 防护指纹。
2. **Verify Agent (验证智能体)**：接收侦察数据，通过多轮上下文推理生成探测 Payload，在 SafeGateway 约束下进行真实可利用性验证。
3. **Audit Agent (审计智能体)**：综合验证结果与资产核心价值，输出金融级风险定级与保费调整倍数。

---

## 🚀 快速开始 (Quick Start)

### 1. 环境准备

确保您的系统中已安装 Python 3.10 或更高版本。

```bash
# 克隆仓库
git clone https://github.com/yourusername/MARS-DP.git
cd MARS-DP

# 创建并激活虚拟环境
python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 2. 安装依赖

本项目底层依赖 `crewai` 和 `litellm`（以及若干辅助库）。推荐先尝试：

```bash
pip install -r requirements.txt
```

如果仓库中没有 `requirements.txt`，请手动安装必需包：

```bash
pip install crewai litellm python-dotenv langchain-openai
```

### 3. 配置环境变量

在项目根目录创建一个 `.env` 文件，填入您的 LLM API 密钥（示例使用 DeepSeek）：

```text
# .env
DEEPSEEK_API_KEY="sk-您的API密钥"
```

如果您使用 OpenAI/Claude 等服务，请按对应 SDK 要求设置相应的环境变量。

### 4. 运行系统

启动项目入口（示例）：

```bash
python main.py
```

执行后，终端将输出智能体的协同过程日志与最终的精算得分（或将结果写入报告文件，取决于实现）。

### 📂 目录结构 (Repository Structure)

```
MARS-DP/
├── main.py                # 系统入口与 CrewAI 任务编排
├── tools/                 # 智能体工具库
│   ├── safe_gateway.py    # 无损安全验证网关实现
│   └── recon_tool.py      # 资产指纹与 API 探测脚本
├── agents/                # 智能体角色与 Prompt 定义
├── config/                # 靶场环境与资产权重配置
├── docs/                  # 学术论文与架构图文档
├── .env.example           # 环境变量模板
└── README.md              # 项目说明
```

### 学术引用 (Citation)

如果您在研究或工作中使用了 MARS-DP 代码或思想，请引用我们的相关论文（Submitted to CSDP 2026）：

```
@inproceedings{marsdp2026,
  title={Multi-Agent Collaborative Web Risk Assessment for Dynamic Pricing in Cyber Insurance},
  author={您的名字},
  booktitle={Proceedings of the Cybersecurity and Data Protection Conference (CSDP)},
  year={2026}
}
```

### 许可证 (License)

本项目基于 MIT License 开源。欢迎安全研究人员与精算师提交 Pull Requests 或探讨合作！