# MARS-DP (Multi-Agent Risk System for Dynamic Pricing) 🛡️📊

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/Powered%20by-CrewAI-orange.svg)](https://crewai.com/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![LLM: DeepSeek](https://img.shields.io/badge/LLM-DeepSeek-black.svg)](https://www.deepseek.com/)

MARS-DP 是一个由大语言模型（LLM）驱动的多智能体协同 Web 风险评估与网络安全保险动态定价系统，面向研究与工程复现。

本项目旨在解决传统 DAST 工具（如 ZAP、AWVS）在云原生与复杂业务逻辑场景下的漏报与语义盲区问题。通过基于 ReAct 的多智能体协同推理与“无损安全网关（SafeGateway）”，系统实现“拓扑感知 → 深层验证 → 精算定价”的闭环，并将技术风险映射为可量化的动态保费。

---

## ✨ 核心特性

- **🤖 多智能体架构 (Multi-Agent Orchestration)**：解耦传统扫描器的线性流程，包含 Recon（侦察）、Verify（验证）、Audit（审计）三大智能体，支持多轮交互与上下文记忆。
- **🛡️ 无损安全验证 (SafeGateway Verification)**：基于 AST 与正则规则的中间件，对大模型生成的验证载荷做物理级别过滤，拦截破坏性指令，保证“零损害”验证。
- **🧠 复杂逻辑漏洞推演 (Business Logic Deduction)**：自动化推演 API 越权（BOLA/IDOR）、支付逻辑篡改、以及高隐蔽性攻击链路。
- **💰 动态精算映射 (Actuarial Mapping)**：将多步攻击路径成功概率与资产权重（`W_asset`）结合，计算动态风险得分（`DRS`），支持精算级别的保费调整。

---

## 🎯 实验靶场与评估范围

项目内置四个基于 FastAPI 与 Docker 的典型企业数字孪生靶场（Range A–D），用于验证不同风险场景：

- **Range A (SME Monolith)**：传统单体架构，测试基础漏洞与高隐蔽性 SQL 注入变种。
- **Range B (Cloud-Native SaaS)**：微服务架构，测试智能体在合法 Token 流转下能否发现 API 越权（BOLA）。
- **Range C (Hybrid Enterprise)**：带有 WAF 的支付接口，验证是否能用合法载荷（如 `{"price": 0.01}`）篡改业务逻辑。
- **Range D (Critical Infrastructure)**：边缘网关与供应链缺陷场景，测试多步横向移动链路（RCE → 内网凭证提取 → 数据外泄）。

---

## 🚀 快速开始

确保 Python 3.10+ 与 Docker（仅当需要运行本地靶场时）已安装。

1. 克隆仓库并进入目录：

```bash
git clone https://github.com/cuihang/MARS-DP.git
cd MARS-DP
```

2. 创建并激活虚拟环境：

```bash
python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

若无 `requirements.txt`，可按需安装主要依赖：

```bash
pip install crewai litellm python-dotenv langchain-openai requests fastapi uvicorn
```

4. 配置环境变量：复制 `.env.example` 为 `.env`，并填入 LLM API Key（示例使用 DeepSeek）：

```text
# .env
DEEPSEEK_API_KEY="sk-your-api-key-here"
```

5. 启动消融实验与精算评估（示例）：

```bash
# 启动多智能体协同评估（默认对 Range D 进行推演）
python ablation_runner.py
```

执行后，终端将打印智能体的思维链日志（CoT）、SafeGateway 拦截记录，并在项目目录下生成 Markdown 格式的最终评估报告。

---

## 📂 目录结构（示意）

```text
MARS-DP/
├── ablation_runner.py     # 系统主入口与消融实验调度
├── requirements.txt       # 可选：项目依赖
├── tools/                 # 智能体工具库（SafeGateway、Recon 等）
├── target_ranges/         # 本地 FastAPI 靶场（Range A-D）
├── agents/                # 智能体角色与 Prompt 定义
├── docs/                  # 架构与精算映射文档
├── .env.example           # 环境变量模板
└── README.md              # 项目说明
```

---

## 🎓 学术引用

若在学术或工程工作中使用本项目，请引用：

```
@inproceedings{cui2026marsdp,
	title={Multi-Agent Collaborative Web Risk Assessment for Dynamic Pricing in Cyber Insurance},
	author={Cui, Hang and others},
	booktitle={Proceedings of the IEEE Symposium on Security and Privacy (S&P)},
	year={2026}
}
```

---

## 📜 许可证

本项目基于 MIT License 开源。欢迎提交 PR 与讨论合作。

---

