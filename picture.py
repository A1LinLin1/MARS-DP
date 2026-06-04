import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# 1. 论文实验数据注入
# ==========================================
ranges = ['Range A\n(SME)', 'Range B\n(Cloud-Native)', 'Range C\n(Fin-Commerce)', 'Range D\n(Supply Chain)']
cvss_scores = [98, 0, 0, 98]       # 静态 CVSS 基线 (映射到百分制: 9.8 -> 98)
drs_scores = [28.0, 85.0, 76.5, 84.5] # 我们的 DRS 动态风险得分
premium_multipliers = [1.20, 3.12, 3.20, 4.0] # 保费调整乘数

# ==========================================
# 2. 学术风图表配置 (双 Y 轴 + 黑白打印友好)
# ==========================================
# 调整图表比例，使其更适合 IEEE 双栏排版
fig, ax1 = plt.subplots(figsize=(10, 5.5))

x = np.arange(len(ranges))
width = 0.32  # 稍微调窄一点，显得更精致

# 绘制左侧 Y 轴 (风险得分 0-100)
# 增加 hatch 纹理，即使黑白打印也能一眼区分
rects1 = ax1.bar(x - width/2, cvss_scores, width, label='Static CVSS Score (x10)', 
                 color='#E0E0E0', edgecolor='black', hatch='//', linewidth=1.2)
rects2 = ax1.bar(x + width/2, drs_scores, width, label='MARS-DP DRS', 
                 color='#4682B4', edgecolor='black', linewidth=1.2)

ax1.set_ylabel('Risk Score (0 - 100)', fontsize=12, fontweight='bold')
ax1.set_ylim(0, 115) # 稍微拔高，给数据标签留空间
ax1.set_xticks(x)
ax1.set_xticklabels(ranges, fontsize=11, fontweight='bold')
ax1.tick_params(axis='y', labelsize=11)
ax1.grid(axis='y', linestyle=':', alpha=0.6, color='gray') # 改为更轻柔的点状网格

# 为柱状图添加具体数值标签 (顶会刚需)
ax1.bar_label(rects1, padding=3, fmt='%g', fontsize=10)
ax1.bar_label(rects2, padding=3, fmt='%g', fontsize=10, fontweight='bold', color='#104E8B')

# 绘制右侧 Y 轴 (保费乘数)
ax2 = ax1.twinx()
# 改为虚线(--)和显眼的菱形(D)标记点，彻底解决色盲/黑白打印问题
line1 = ax2.plot(x, premium_multipliers, color='#D32F2F', marker='D', markersize=8, 
                 linestyle='--', linewidth=2.5, label='Premium Multiplier (Right Axis)')

ax2.set_ylabel('Premium Multiplier (x)', fontsize=12, fontweight='bold', color='#D32F2F')
ax2.set_ylim(0, 4.8)
ax2.tick_params(axis='y', labelcolor='#D32F2F', labelsize=11)

# 为折线图添加具体数值标签
for i, txt in enumerate(premium_multipliers):
    ax2.annotate(f"{txt}x", (x[i], premium_multipliers[i]), 
                 textcoords="offset points", xytext=(0, 10), ha='center', 
                 fontsize=11, fontweight='bold', color='#D32F2F')

# ==========================================
# 3. 图例与细节优化
# ==========================================
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
# 将图例放在左上角，并设置为单列，显得更规整
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', 
           fontsize=10, framealpha=1, edgecolor='black')

# 标注 Range D 的 "拒保" 极端情况
ax2.annotate('Systemic Melt-down\n(Absolute Rejection)', 
             xy=(3, 4.0), xytext=(2.0, 4.2),
             arrowprops=dict(facecolor='#D32F2F', edgecolor='#D32F2F', arrowstyle='-|>', lw=2),
             fontsize=11, fontweight='bold', color='#D32F2F', 
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#D32F2F", lw=1.5))

# 删除了 plt.title，交由 LaTeX 的 \caption 处理
plt.tight_layout()

# ==========================================
# 4. 导出为高清矢量图
# ==========================================
plt.savefig('actuarial_mismatch.pdf', format='pdf', dpi=300, bbox_inches='tight')
print("✅ 学术高定版图表已成功生成并保存为 actuarial_mismatch.pdf！")