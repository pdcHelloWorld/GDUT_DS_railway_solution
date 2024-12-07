import random
import math
import tkinter as tk
from tkinter import messagebox
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import rcParams
rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为黑体
rcParams['axes.unicode_minus'] = False    # 正常显示负号
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# 城市类，包含城市的编号和坐标
class City:
    def __init__(self, index, x, y):
        self.index = index
        self.x = x
        self.y = y

# 图类，使用邻接矩阵存储
class Graph:
    def __init__(self, cities):
        self.cities = cities
        self.num_cities = len(cities)
        self.adj_matrix = self.create_adj_matrix()

    # 手动实现邻接矩阵
    def create_adj_matrix(self):
        matrix = []
        for i in range(self.num_cities):
            row = []
            for j in range(self.num_cities):
                if i == j:
                    row.append(0)
                else:
                    # 计算两城市间的距离，作为权值
                    distance = math.hypot(
                        self.cities[i].x - self.cities[j].x,
                        self.cities[i].y - self.cities[j].y)
                    row.append(distance)
            matrix.append(row)
        return matrix

# Prim算法
def prim(graph):
    num_cities = graph.num_cities
    if num_cities == 0:
        return [], 0
    selected = [False] * num_cities
    selected[0] = True
    edges = []
    total_length = 0

    for _ in range(num_cities - 1):
        min_distance = float('inf')
        x = -1
        y = -1
        for i in range(num_cities):
            if selected[i]:
                for j in range(num_cities):
                    if not selected[j] and graph.adj_matrix[i][j] > 0:
                        if graph.adj_matrix[i][j] < min_distance:
                            min_distance = graph.adj_matrix[i][j]
                            x = i
                            y = j
        if y == -1:
            break  # 防止不连通的图导致无限循环
        selected[y] = True
        edges.append((x, y))
        total_length += graph.adj_matrix[x][y]

    return edges, total_length

# Kruskal算法
def kruskal(graph):
    parent = list(range(graph.num_cities))
    edges = []
    total_length = 0

    def find(i):
        while i != parent[i]:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            parent[root_j] = root_i

    all_edges = []
    for i in range(graph.num_cities):
        for j in range(i + 1, graph.num_cities):
            if graph.adj_matrix[i][j] > 0:
                all_edges.append((graph.adj_matrix[i][j], i, j))

    all_edges.sort()

    for weight, i, j in all_edges:
        if find(i) != find(j):
            union(i, j)
            edges.append((i, j))
            total_length += weight

    return edges, total_length

# 可视化界面类
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("城际铁路建设方案")
        self.geometry("1200x800")  # 增加窗口宽度以适应更多控件
        self.cities = []
        self.edges = []
        self.algorithm = tk.StringVar(value="Prim")  # 默认使用Prim算法
        self.total_length = 0
        self.total_length_text = None
        self.create_widgets()

    def create_widgets(self):
        # 左侧控制面板
        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.label = tk.Label(control_frame, text="请选择城市数据的生成方式：")
        self.label.pack(pady=10)

        self.btn_manual = tk.Button(control_frame, text="手动录入城市信息", command=self.input_cities)
        self.btn_manual.pack(pady=5)

        self.btn_random = tk.Button(control_frame, text="随机生成城市信息", command=self.generate_cities)
        self.btn_random.pack(pady=5)

        self.btn_clear = tk.Button(control_frame, text="清空平面图", command=self.reset)
        self.btn_clear.pack(pady=5)

        self.label_algorithm = tk.Label(control_frame, text="请选择算法：")
        self.label_algorithm.pack(pady=10)

        self.radio_prim = tk.Radiobutton(control_frame, text="Prim算法", variable=self.algorithm, value="Prim")
        self.radio_prim.pack(pady=5)

        self.radio_kruskal = tk.Radiobutton(control_frame, text="Kruskal算法", variable=self.algorithm, value="Kruskal")
        self.radio_kruskal.pack(pady=5)

        # 在界面中显示matplotlib图形
        self.figure = Figure(figsize=(8, 8), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("城市分布")
        self.ax.set_xlabel("X 坐标")
        self.ax.set_ylabel("Y 坐标")
        self.ax.grid(True)

        # 设置初始坐标轴范围，防止自动缩放
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

        self.canvas.mpl_connect('button_press_event', self.on_plot_click)
        self.canvas.mpl_connect('scroll_event', self.on_scroll)  # 连接滚轮事件

    def input_cities(self):
        # 清除之前的数据
        self.reset()
        messagebox.showinfo("提示", "请在右侧的图中左键点击添加城市位置，右键点击需要删除的城市。")

    def on_plot_click(self, event):
        if event.inaxes != self.ax:
            return  # 点击不在绘图区域内
        if event.button == 1 and self.btn_manual['state'] != 'disabled':
            # 左键点击，添加城市
            x, y = event.xdata, event.ydata
            if x is not None and y is not None:
                self.add_city_manually(x, y)
        elif event.button == 3 and self.btn_manual['state'] != 'disabled':
            # 右键点击，删除城市
            x, y = event.xdata, event.ydata
            if x is not None and y is not None:
                city_index = self.get_nearest_city(x, y)
                if city_index is not None:
                    self.delete_city(city_index)

    def get_nearest_city(self, x, y, threshold=5.0):  # 增加阈值
        nearest_index = None
        min_distance = float('inf')
        for i, city in enumerate(self.cities):
            distance = math.hypot(city.x - x, city.y - y)
            if distance <= threshold and distance < min_distance:
                nearest_index = i
                min_distance = distance
        return nearest_index

    def delete_city(self, index):
        confirm = messagebox.askyesno("确认删除", f"是否删除该城市？")
        if confirm:
            self.cities.pop(index)
            # 重新为城市编号
            for i in range(index, len(self.cities)):
                self.cities[i].index = i
            self.run_algorithm_and_show()

    def on_scroll(self, event):
        # 滚轮缩放事件处理
        base_scale = 1.2
        if event.button == 'up':
            # 放大
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            # 缩小
            scale_factor = base_scale
        else:
            # 不处理其他事件
            return

        xdata = event.xdata
        ydata = event.ydata
        if xdata is None or ydata is None:
            return

        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

        self.ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
        self.ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        self.canvas.draw()

    def generate_cities(self):
        # 清除之前的数据
        self.reset()

        # 随机生成城市
        num = random.randint(10, 15)
        for i in range(num):
            x = random.uniform(0, 100)
            y = random.uniform(0, 100)
            city = City(i, x, y)
            self.cities.append(city)

        self.run_algorithm_and_show()
        self.btn_manual['state'] = 'disabled'

    def run_algorithm_and_show(self):
        # 获取当前坐标轴范围
        curr_xlim = self.ax.get_xlim()
        curr_ylim = self.ax.get_ylim()

        if len(self.cities) >= 2:
            # 创建图并计算最小生成树
            graph = Graph(self.cities)
            if self.algorithm.get() == "Prim":
                self.edges, self.total_length = prim(graph)
            else:
                self.edges, self.total_length = kruskal(graph)
        else:
            self.edges = []
            self.total_length = 0

        # 清除坐标轴
        self.ax.clear()

        # 重新设置标题、标签和网格
        self.ax.set_title("城际铁路建设方案")
        self.ax.set_xlabel("X 坐标")
        self.ax.set_ylabel("Y 坐标")
        self.ax.grid(True)

        # 设置坐标轴范围
        self.ax.set_xlim(curr_xlim)
        self.ax.set_ylim(curr_ylim)

        # 绘制所有城市
        for city in self.cities:
            self.ax.plot(city.x, city.y, 'bo', picker=5)  # 增加picker参数以提高点击精度
            self.ax.text(city.x + 0.5, city.y + 0.5, f"{city.index}")

        # 绘制最小生成树的边及其距离
        if len(self.edges) >= 1:
            graph = Graph(self.cities)
            for edge in self.edges:
                city1 = self.cities[edge[0]]
                city2 = self.cities[edge[1]]
                self.ax.plot([city1.x, city2.x], [city1.y, city2.y], 'r-')
                # 计算中点
                mid_x = (city1.x + city2.x) / 2
                mid_y = (city1.y + city2.y) / 2
                distance = graph.adj_matrix[edge[0]][edge[1]]
                self.ax.text(mid_x, mid_y, f"{distance:.2f}", color='green')

        # 更新总里程数文本
        if self.total_length_text:
            self.total_length_text.remove()
            self.total_length_text = None

        if len(self.edges) >= 1:
            self.total_length_text = self.figure.text(
                0.95, 0.05, f"总里程数: {self.total_length:.2f}",
                horizontalalignment='right', verticalalignment='bottom',
                fontsize=12, bbox=dict(facecolor='white', alpha=0.5)
            )

        self.canvas.draw()

    def add_city_manually(self, x, y):
        index = len(self.cities)
        city = City(index, x, y)
        self.cities.append(city)
        self.run_algorithm_and_show()

    def reset(self):
        self.cities = []
        self.edges = []
        self.total_length = 0
        if self.total_length_text:
            self.total_length_text.remove()
            self.total_length_text = None

        self.ax.clear()
        self.ax.set_title("城市分布")
        self.ax.set_xlabel("X 坐标")
        self.ax.set_ylabel("Y 坐标")
        self.ax.grid(True)
        # 重置坐标轴范围
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.canvas.draw()
        self.btn_manual['state'] = 'normal'

# 主函数
if __name__ == "__main__":
    app = Application()
    app.mainloop()