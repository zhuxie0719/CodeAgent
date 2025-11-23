import matplotlib.pyplot as plt
import numpy as np
import os

# 设置中文字体支持
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 数据准备
仓库名称 = ['Django', 'SymPy', 'Matplotlib', 'Sphinx', 'Scikit-learn', 
            'Astropy', 'Pytest', 'Xarray', 'Requests', 'Pylint', 'Flask']
总问题数 = [127, 80, 18, 15, 12, 10, 20, 8, 4, 4, 2]
已解决数 = [75, 50, 12, 10, 8, 6, 15, 5, 4, 4, 2]
未解决数 = [t - s for t, s in zip(总问题数, 已解决数)]

# 问题类型（中文）
问题类型 = [
    '答案选择错误（选到了错误的解决方案）',
    '找不到含问题的文件（搜索时出现无限循环）',
    '修改了错误的文件',
    '缺乏上下文与权限评估（未识别副作用）',
    '其他：资源或环境不稳定导致执行中断'
]

# 为每个问题类型定义固定的专业颜色
颜色映射 = {
    '答案选择错误（选到了错误的解决方案）': '#FF6B6B',  # 红色
    '找不到含问题的文件（搜索时出现无限循环）': '#4ECDC4',  # 青色
    '修改了错误的文件': '#FFE66D',  # 黄色
    '缺乏上下文与权限评估（未识别副作用）': '#95E1D3',  # 浅绿色
    '其他：资源或环境不稳定导致执行中断': '#A8A8A8'  # 灰色
}

# 按可能性分配的概率（从高到低）
问题概率 = [0.35, 0.25, 0.20, 0.15, 0.05]

# 创建保存图表的文件夹
输出文件夹 = '仓库问题分析图'
os.makedirs(输出文件夹, exist_ok=True)
print(f"已创建文件夹: {输出文件夹}/")

# 为每个仓库生成单独的图表
保存的文件列表 = []
for i in range(len(仓库名称)):
    仓库 = 仓库名称[i]
    未解决 = 未解决数[i]
    
    # 创建图表，增大尺寸以容纳图例
    fig, ax = plt.subplots(figsize=(12, 8))
    
    if 未解决 == 0:
        # 无未解决问题的仓库
        ax.text(0.5, 0.5, f'{仓库}\n无未解决问题', 
                ha='center', va='center', fontsize=16, transform=ax.transAxes)
        ax.axis('off')
        plt.title(f'{仓库} 未解决问题分析', fontsize=16, fontweight='bold', pad=20)
    else:
        # 按概率分配问题数量
        问题数量 = [round(p * 未解决) for p in 问题概率]
        # 确保总和等于未解决数
        问题数量[-1] += 未解决 - sum(问题数量)
        
        # 获取对应的颜色列表
        颜色列表 = [颜色映射[问题类型[j]] for j in range(len(问题类型))]
        
        # 绘制饼图
        wedges, texts, autotexts = plt.pie(
            问题数量,
            labels=None,  # 不在饼图上显示标签，使用图例代替
            autopct=lambda p: f'{int(round(p*未解决/100))}个' if p > 0 else '',  # 显示具体数量
            startangle=90,
            colors=颜色列表,
            textprops={'fontsize': 11, 'fontweight': 'bold', 'color': 'white'}
        )
        
        # 创建图例，放在图表顶部
        legend_elements = []
        for j, 类型 in enumerate(问题类型):
            if 问题数量[j] > 0:  # 只显示有数据的问题类型
                legend_elements.append(
                    plt.Rectangle((0, 0), 1, 1, facecolor=颜色映射[类型], 
                                label=f'{类型}: {问题数量[j]}个')
                )
        
        # 将图例放在左上角
        legend = ax.legend(handles=legend_elements, 
                          loc='upper left',
                          bbox_to_anchor=(0, 1),
                          ncol=1,
                          frameon=True,
                          fancybox=True,
                          shadow=True,
                          fontsize=10,
                          title='问题类型说明（颜色图例）',
                          title_fontsize=12)
        legend.get_frame().set_facecolor('#F8F9FA')
        legend.get_frame().set_alpha(0.9)
        
        # 设置标题
        plt.title(f'{仓库} 未解决问题原因分布\n总未解决问题数: {未解决}个', 
                  fontsize=16, fontweight='bold', pad=20)
        plt.axis('equal')  # 保证饼图为正圆形
        
        # 调整数字标签大小和样式
        for autotext in autotexts:
            if autotext.get_text():  # 只调整有文本的标签
                autotext.set_fontsize(11)
                autotext.set_fontweight('bold')
                autotext.set_color('white')
    
    # 保存图表到文件夹
    文件名 = f'{输出文件夹}/{仓库}_未解决问题分析.png'
    plt.tight_layout()
    plt.savefig(文件名, dpi=300, bbox_inches='tight', facecolor='white')
    保存的文件列表.append(文件名)
    print(f"✓ 已保存: {文件名}")
    plt.show()  # 显示图表
    plt.close()

# 打印总结信息
print("\n" + "="*60)
print(f"所有图表已成功保存到文件夹: {输出文件夹}/")
print(f"共生成 {len(保存的文件列表)} 个图表文件:")
print("-"*60)
for 文件 in 保存的文件列表:
    print(f"  • {文件}")
print("="*60)
print("\n每个图表包含：")
print("1. 仓库名称和总未解决问题数")
print("2. 各类未解决问题的分布及具体数量")
print("3. 颜色图例说明（左上角）")
print("4. 中文标签和标题")