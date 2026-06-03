import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# 1. 论文实验数据注入
# ==========================================
ranges = ['Range A\n(SME Monolith)', 'Range B\n(Cloud-Native)', 'Range C\n(Fin-Commerce)', 'Range D\n(Supply Chain)']
cvss_scores = [98, 0, 0, 98]       # 静态 CVSS 基线 (映射到百分制方便对比: 9.8 -> 98)
drs_scores = [28.0, 85.0, 76.5, 84.5] # 我们的 DRS 动态风险得分
premium_multipliers = [1.20, 3.125, 3.20, 4.0] # 保费调整乘数 (Range D 用 4.0 示意最高惩罚/拒保阈值)

# ==========================================
# 2. 学术风图表配置 (双 Y 轴设计)
# ==========================================
fig, ax1 = plt.subplots(figsize=(10, 6))

# 设置柱状图宽度和 X 轴偏移
x = np.arange(len(ranges))
width = 0.35

# 绘制左侧 Y 轴 (风险得分 0-100)
# 静态 CVSS 柱子 (浅灰色，代表传统、刻板)
rects1 = ax1.bar(x - width/2, cvss_scores, width, label='Static CVSS Score (x10)', color='#B0BEC5', edgecolor='black')
# 动态 DRS 柱子 (深蓝色，代表咱们的核心技术)
rects2 = ax1.bar(x + width/2, drs_scores, width, label='MARS-DP DRS', color='#1f77b4', edgecolor='black')

ax1.set_ylabel('Risk Score (0 - 100)', fontsize=12, fontweight='bold')
ax1.set_ylim(0, 110)
ax1.set_xticks(x)
ax1.set_xticklabels(ranges, fontsize=11)
ax1.tick_params(axis='y', labelsize=11)
ax1.grid(axis='y', linestyle='--', alpha=0.7)

# 绘制右侧 Y 轴 (保费乘数)
ax2 = ax1.twinx()
# 保费折线 (红色，带有明显的标记点，代表金融制裁)
line1 = ax2.plot(x, premium_multipliers, color='#d62728', marker='o', markersize=8, linewidth=2.5, label='Premium Multiplier (Right Axis)')

ax2.set_ylabel('Premium Multiplier (x)', fontsize=12, fontweight='bold', color='#d62728')
ax2.set_ylim(0, 4.5)
ax2.tick_params(axis='y', labelcolor='#d62728', labelsize=11)

# ==========================================
# 3. 图例与细节优化
# ==========================================
# 合并图例
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', fontsize=11, framealpha=0.9)

# 标注 Range D 的 "拒保 (Rejection)" 极端情况
ax2.annotate('Systemic Melt-down\n(Absolute Rejection)', 
             xy=(3, 4.0), xytext=(2.2, 4.1),
             arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.5),
             fontsize=11, fontweight='bold', color='red')

plt.title('Actuarial Mismatch: Static CVSS vs. MARS-DP Dynamic Pricing', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()

# ==========================================
# 4. 导出为高清矢量图 (顶会必备)
# ==========================================
plt.savefig('actuarial_mismatch.pdf', format='pdf', dpi=300)
print("图表已成功生成并保存为 actuarial_mismatch.pdf！")
# plt.show() # 如果你想在本地先预览，可以取消这行的注释