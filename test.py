import matplotlib.pyplot as plt

# Enable Chinese font
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# Data
仓库名称 = ['Django', 'SymPy', 'Matplotlib', 'Sphinx', 'Scikit-learn',
        'Astropy', 'Pytest', 'Xarray', 'Requests', 'Pylint', 'Flask']
总问题数 = [127, 80, 18, 15, 12, 10, 20, 8, 4, 4, 2]
已解决数 = [75, 50, 12, 10, 8, 6, 15, 5, 4, 4, 2]

# Build labels with total/solved
labels = [f"{name} ({total}/{solved})" for name, total, solved in zip(仓库名称, 总问题数, 已解决数)]

# Pie chart for 总问题数
plt.figure(figsize=(8, 8))
plt.pie(总问题数, labels=labels, autopct='%1.1f%%', startangle=90)
plt.axis('equal')  # Keep the pie round

plt.show()


