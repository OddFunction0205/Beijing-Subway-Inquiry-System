import math
import gradio as gr
import datetime
# 获取当前时间, 其中中包含了year, month, hour, 需要import datetime


# 定义节点的结构体：
class Node:
    def __init__(self, num, name):
        self.num = num  # 记录站点的编号
        self.name = name  # 记录站点的名字
        self.lines = ["" for i in range(5)]  # 属于几号线(由于可能有换乘站，所以要用数组存)
        self.line_num = 0  # 有几条线通过这个站点


class LaunchTime:  # 记录每一个发车时间
    def __init__(self, line_name, is_forward):
        self.line_name = line_name  # 记录是第几号线的发车时间
        self.launch_time = [0.0]
        self.is_forward = is_forward  # 记录是往哪个方向发车


inf = 100
total_station_num = 0  # 记录全部的站点数
station = [Node(0, "") for i in range(500)]  # 记录各个站点的列表
time_map = [[inf for i in range(500)] for j in range(500)]  # 建立一个500*500的二维数组，来存储时间的邻接矩阵.初始化为无穷大（都不相连）
dist_map = [[inf for i in range(500)] for j in range(500)]  # 建立一个500*500的二维数组，来存储距离的邻接矩阵.初始化为无穷大（都不相连）
S = [0 for i in range(500)]  # 记录下第i个节点是否有被添加
Time = [inf for i in range(500)]  # 记录下起点到顶点i的时间
Dist = [inf for i in range(500)]  # 记录下起点到顶点i的路径长度
Path = [0 for i in range(500)]  # 记录下起点到顶点i的路径
whether_to_transfer = [False for i in range(500)]  # 用来记录在某条特定线上，哪些站需要换乘
have_been_deleted = [[False, ""] for i in range(500)]  # 用来记录某个站点是否被删除过.记录下：是否被删除，从哪条线被删除


def load_station_data():
    # 声明全局变量
    global total_station_num
    global station
    global time_map
    global dist_map
    global Time
    global S
    global Dist
    global Path
    # 建立一个列表，来储存所有单词：
    words = []
    with open('source//subway.txt', 'r') as data:  # 将文件打开为data
        words = data.read().split()  # 将文件中的所有单词写入words列表
        for i in range(500):
            words.append("")  # 对words进行一个扩容，防止接下来访问越界
    line_num = int(words[0])  # 记录下文件里面的第一个单词（表示总共有几条地铁线）

    word_index = 1  # 记录下正在读取第几个单词
    # 对每一条线进行遍历：
    for i in range(line_num):
        # 读取这条地铁线的名字
        line_name = words[word_index]
        word_index += 1

        # 读取这条地铁线中有几个站点
        station_num = int(words[word_index])  # 将节点数写入station_num
        word_index += 1

        # 读取地铁线的速度
        velocity = float(words[word_index])
        word_index += 1

        # 对该线路的每个站点进行遍历
        for j in range(total_station_num, total_station_num + station_num):
            station_name = words[word_index]
            word_index += 1
            station[j].name = station_name
            t = search_num(station_name)

            if t != 0:  # 如果当前站是换乘站
                station[t].lines[station[t].line_num] = line_name
                station[t].line_num += 1
                dist = float(words[word_index])
                tt = search_num(words[word_index + 1])  # 搜索一下下一站第一次出现的编号,看一下是不是换乘站
                if tt != 0:  # 如果下一站是换乘站
                    time_map[t][tt] = time_map[tt][t] = dist / velocity
                    dist_map[t][tt] = dist_map[tt][t] = dist
                if tt == 0:  # 如果下一站不是换乘站
                    time_map[t][j + 1] = time_map[j + 1][t] = dist / velocity  # 在邻接表中存储时间
                    dist_map[t][j + 1] = dist_map[j + 1][t] = dist

            if t == 0:  # 如果当前站不是换乘站
                station[j].lines[station[j].line_num] = line_name
                station[j].line_num += 1
                dist = float(words[word_index])
                tt = search_num(words[word_index + 1])  # 搜索一下下一站第一次出现的编号,看一下是不是换乘站
                if tt != 0:  # 如果下一站出现过了（是换乘站）
                    time_map[j][tt] = time_map[tt][j] = dist / velocity
                    dist_map[j][tt] = dist_map[tt][j] = dist
                if tt == 0:  # 如果下一站没出现过（不是换乘站）
                    time_map[j][j + 1] = time_map[j + 1][j] = dist / velocity  # 在邻接表中存储时间
                    dist_map[j][j + 1] = dist_map[j + 1][j] = dist
            word_index += 1
        total_station_num += station_num
    print("-----------------")
    print("所有站点加载完毕!")
    print("-----------------")


def search_num(station_name):  # 根据站点名称，找出第一次出现的编号。如果没有找到，返回0
    global total_station_num
    global station
    global time_map
    global dist_map
    global Time
    global S
    global Dist
    global Path
    for i in range(total_station_num):
        if station[i].name == station_name:
            return i
    return 0


def find_min():
    global total_station_num
    global station
    global time_map
    global dist_map
    global Time
    global S
    global Dist
    global Path
    k = 0
    minium = inf
    for i in range(total_station_num):
        if not S[i] and minium > Time[i]:
            minium = Time[i]
            k = i
    if min == inf:
        return -1
    return k


def print_way_min_time(end_num):
    global total_station_num
    global station
    global time_map
    global dist_map
    global Time
    global S
    global Dist
    global Path
    string_way = ""  # 用来记录乘车方案的字符串
    string_time = ""  # 用来记录乘车时间的字符串
    string_dist = ""  # 用来记录乘车距离的字符串
    string_price = ""  # 用来记录票价的字符串
    stack = [station[end_num].name]  # 用队列来模拟栈,并且先把终点站入栈
    pre = Path[end_num]
    while pre != -1:
        stack.append(station[pre].name)
        pre = Path[pre]
    # 计算需要经过几站：
    stop_time = len(stack)  # 有几站就停留几分钟
    # 计算换乘需要的时间（按照一站五分钟来计算）
    transfer_num = count_transfer_station(end_num)
    string_way += "最短时间乘坐路线为：\n"
    while len(stack) != 0:
        temp = stack.pop()
        string_way += temp + "\n"
        if whether_to_transfer[search_num(temp)]:  # 如果是换乘站
            string_way += f"|在{station[search_num(temp)].name}乘{station[search_num(stack[len(stack) - 1])].lines[0]}|\n"
    total_time = Time[end_num] * 60 + stop_time  # 计算总共的时间（分钟）
    hour = 0
    minute = math.ceil(total_time)
    while total_time >= 60:
        total_time -= 60
        hour += 1
        minute = math.ceil(total_time)  # 向上取整
    string_time += f"预计需要{hour}小时{minute}分钟"
    total_dist = Dist[end_num] * 1000
    string_dist += f"{int(total_dist)}米"
    price = 0
    if total_dist <= 6000:
        price = 3
    elif total_dist <= 12000:
        price = 4
    elif total_dist <= 22000:
        price = 5
    elif total_dist <= 32000:
        price = 6
    else:
        price = 7
    string_price += f"{price}元"
    return string_way, string_time, string_dist, string_price


def count_transfer_station(end_num):  # 计算一条线路上换乘站的数量
    transfer_station_num = 0
    stack = [station[end_num].name]  # 用队列来模拟栈,并且先把终点站入栈
    pre = Path[end_num]
    while pre != -1:
        stack.append(station[pre].name)
        pre = Path[pre]
    if len(stack) != 0:
        pre_station = stack.pop()
    if len(stack) != 0:
        now_station = stack.pop()
    if len(stack) != 0:
        next_station = stack.pop()
    while len(stack) != 0:
        if station[search_num(now_station)].line_num > 1:  # 如果当前是换乘站
            flag = True  # 表示是否换乘.True表示换乘
            # 比较之前和之后的两个站点，看看是不是真的换乘了。如果换乘了，前后两个站点应该完全没有一样的线路
            for i in range(station[search_num(pre_station)].line_num):
                for j in range(station[search_num(next_station)].line_num):
                    if station[search_num(pre_station)].lines[i] == station[search_num(next_station)].lines[j]:
                                flag = False  # 一旦有相同的线，就表示没有换乘。旗帜倒下。
            if flag:  # 如果没有倒下
                transfer_station_num += 1  # 换乘站数量+1
                whether_to_transfer[search_num(now_station)] = True
        pre_station = now_station
        now_station = next_station
        next_station = stack.pop()
    return transfer_station_num


def short_time(s, e):  # 计算最短时间
    global station
    gr.Info("开始查询")
    start = search_num(s)
    end = search_num(e)
    if start == 0 or end == 0:
        raise gr.Error("输入不合法，请重新输入")
        return
    if station[start].line_num == 0 or station[end].line_num == 0:
        raise gr.Error("输入不合法，请重新输入")
        return
    if start == end:
        raise gr.Error("起点和终点不能相同")
        return
    global total_station_num
    global time_map
    global dist_map
    global S
    global Dist
    global Time
    global Path
    # 初始化辅助数组：
    for i in range(total_station_num):
        S[i] = False  # 都标记为没有被添加
        Time[i] = time_map[start][i]  # 将与起点直接连接的加入Time
        Dist[i] = dist_map[start][i]  # 将与起点直接连接的加入Dist
        if Time[i] != inf:
            Path[i] = start
        else:
            Path[i] = -1  # 一开始初始化为无前驱
    S[start] = True  # 起点到起点的最短路径已经被找到
    Time[start] = 0  # 起点到起点时间为0
    Dist[start] = 0  # 起点到起点距离为0

    for i in range(total_station_num):
        v = find_min()
        if find_min() == -1:  # 如果全是不相邻的
            return
        S[v] = True
        for j in range(total_station_num):  # 查找到j的距离,并更新
            pre_station = Path[v]  # 记录下之前的站点
            now_station = v  # 记录下当前的站点
            next_station = j  # 记录下下一个站点

            # 接下来这个模块是判断是否换乘的：
            if station[now_station].line_num > 1:  # 如果当前是换乘站
                flag = True  # 表示是否换乘.True表示换乘
                # 比较之前和之后的两个站点，看看是不是真的换乘了。如果换乘了，前后两个站点应该完全没有一样的线路
                for k in range(station[pre_station].line_num):
                    for m in range(station[next_station].line_num):
                        if station[pre_station].lines[k] == station[next_station].lines[m]:
                            flag = False  # 一旦有相同的线，就表示没有换乘。旗帜倒下。
                if pre_station == "西二旗" and next_station == "上地":  # 对这两站的特判
                    flag = True
                if flag:  # 如果换乘了，应该考虑进换乘时间0.083小时
                    if S[j] != 1 and Time[j] >= time_map[v][j] + Time[v] + 0.083:  # 如果找到了更短的，更新
                        Time[j] = time_map[v][j] + Time[v] + 0.083
                        Dist[j] = dist_map[v][j] + Dist[v]
                        Path[j] = v
                else:  # 如果没换乘，就不考虑换乘的时间。
                    if S[j] != 1 and Time[j] >= time_map[v][j] + Time[v]:  # 如果找到了更短的，更新
                        Time[j] = time_map[v][j] + Time[v]
                        Dist[j] = dist_map[v][j] + Dist[v]
                        Path[j] = v
            else:  # 如果当前站不是换乘站，就按照正常的来
                if S[j] != 1 and Time[j] >= time_map[v][j] + Time[v]:  # 如果找到了更短的，更新
                    Time[j] = time_map[v][j] + Time[v]
                    Dist[j] = dist_map[v][j] + Dist[v]
                    Path[j] = v
    string_way, string_time, string_dist, string_price = print_way_min_time(end)
    return string_way, string_time, string_dist, string_price


def print_way_min_transfer(end_num):
    global total_station_num
    global station
    global time_map
    global dist_map
    global Time
    global S
    global Dist
    global Path
    string_way = ""  # 用来记录乘车方案的字符串
    string_time = ""  # 用来记录乘车时间的字符串
    string_dist = ""  # 用来记录乘车距离的字符串
    string_price = ""  # 用来记录票价的字符串
    stack = [station[end_num].name]  # 用队列来模拟栈,并且先把终点站入栈
    pre = Path[end_num]
    while pre != -1:
        stack.append(station[pre].name)
        pre = Path[pre]
    # 计算需要经过几站：
    stop_time = len(stack)  # 有几站就停留几分钟
    # 计算换乘需要的时间（按照一站五分钟来计算）
    transfer_num = count_transfer_station(end_num)
    string_way += "最少换乘乘坐路线为：\n"
    while len(stack) != 0:
        temp = stack.pop()
        string_way += temp + "\n"
        if whether_to_transfer[search_num(temp)]:  # 如果是换乘站
            string_way += f"|在{station[search_num(temp)].name}乘{station[search_num(stack[len(stack) - 1])].lines[0]}|\n"
    total_time = Time[end_num] * 60 + stop_time - 60 * transfer_num  # 计算总共的时间（分钟）
    hour = 0
    minute = math.ceil(total_time)
    while total_time >= 60:
        total_time -= 60
        hour += 1
        minute = math.ceil(total_time)  # 向上取整
    string_time += f"预计需要{hour}小时{minute}分钟"
    total_dist = Dist[end_num] * 1000
    string_dist += f"{int(total_dist)}米"
    price = 0
    if total_dist <= 6000:
        price = 3
    elif total_dist <= 12000:
        price = 4
    elif total_dist <= 22000:
        price = 5
    elif total_dist <= 32000:
        price = 6
    else:
        price = 7
    string_price += f"{price}元"
    return string_way, string_time, string_dist, string_price


def min_transfer(s, e):  # 计算最小换乘站
    gr.Info("开始查询")
    start = search_num(s)
    end = search_num(e)
    if start == 0 or end == 0:
        raise gr.Error("输入不合法，请重新输入")
        return
    if start == end:
        raise gr.Error("起点和终点不能相同")
        return
    global total_station_num
    global station
    global time_map
    global dist_map
    global S
    global Dist
    global Time
    global Path
    # 初始化辅助数组：
    for i in range(total_station_num):
        S[i] = False  # 都标记为没有被添加
        Time[i] = time_map[start][i]  # 将与起点直接连接的加入Time
        Dist[i] = dist_map[start][i]  # 将与起点直接连接的加入Dist
        if Time[i] != inf:
            Path[i] = start
        else:
            Path[i] = -1  # 一开始初始化为无前驱
    S[start] = True  # 起点到起点的最短路径已经被找到
    Time[start] = 0  # 起点到起点时间为0
    Dist[start] = 0  # 起点到起点距离为0

    for i in range(total_station_num):
        v = find_min()
        if find_min() == -1:  # 如果全是不相邻的
            return
        S[v] = True
        for j in range(total_station_num):  # 查找到j的距离,并更新
            pre_station = Path[v]  # 记录下之前的站点
            now_station = v  # 记录下当前的站点
            next_station = j  # 记录下下一个站点

            # 接下来这个模块是判断是否换乘的：
            if station[now_station].line_num > 1:  # 如果当前是换乘站
                flag = True  # 表示是否换乘.True表示换乘
                # 比较之前和之后的两个站点，看看是不是真的换乘了。如果换乘了，前后两个站点应该完全没有一样的线路
                for k in range(station[pre_station].line_num):
                    for m in range(station[next_station].line_num):
                        if station[pre_station].lines[k] == station[next_station].lines[m]:
                                flag = False  # 一旦有相同的线，就表示没有换乘。旗帜倒下。
                if flag:  # 如果换乘了，应该考虑进换乘时间1.083小时
                    if S[j] != 1 and Time[j] >= time_map[v][j] + Time[v] + 1.083:  # 如果找到了更短的，更新
                        Time[j] = time_map[v][j] + Time[v] + 1.083
                        Dist[j] = dist_map[v][j] + Dist[v]
                        Path[j] = v
                else:  # 如果没换乘，就不考虑换乘的时间。
                    if S[j] != 1 and Time[j] >= time_map[v][j] + Time[v]:  # 如果找到了更短的，更新
                        Time[j] = time_map[v][j] + Time[v]
                        Dist[j] = dist_map[v][j] + Dist[v]
                        Path[j] = v
            else:  # 如果当前站不是换乘站，就按照正常的来
                if S[j] != 1 and Time[j] >= time_map[v][j] + Time[v]:  # 如果找到了更短的，更新
                    Time[j] = time_map[v][j] + Time[v]
                    Dist[j] = dist_map[v][j] + Dist[v]
                    Path[j] = v
    string_way, string_time, string_dist, string_price = print_way_min_transfer(end)
    return string_way, string_time, string_dist, string_price


def delete_line(line_name):
    global total_station_num
    global station
    global time_map
    global dist_map
    global Time
    global S
    global Dist
    global Path
    deleted_station = ""
    flag = False  # 标记是否删除成功
    for i in range(total_station_num):
        for j in range(station[i].line_num):
            if station[i].lines[j] == line_name:
                del station[i].lines[j]
                station[i].line_num -= 1
                have_been_deleted[i][0] = True
                have_been_deleted[i][1] = line_name
                deleted_station += station[i].name + "\n"
                flag = True
    if flag:
        return f"删除{line_name}成功。\n删除了{line_name}上的以下站点：\n" + deleted_station
    else:
        raise gr.Error("删除失败。请重新检查输入格式。")


def add_line(line_name):
    global total_station_num
    global station
    global time_map
    global dist_map
    global Time
    global S
    global Dist
    global Path
    added_station = ""
    for i in range(total_station_num):
        flag = False  # 表示某站点是否应该被恢复
        if have_been_deleted[i][0]:  # 如果有被删除过
            if have_been_deleted[i][1] == line_name:  # 并且是从这条线路上删除的
                flag = True  # 确实应该被恢复
        # 进行恢复：
        if flag:
            station[i].lines.append(line_name)
            station[i].line_num += 1
            added_station += station[i].name + "\n"
    return f"添加{line_name}成功。\n添加了{line_name}上的以下站点：\n" + added_station


def get_time():
    return datetime.datetime.strftime(datetime.datetime.now(), '%Y年%m月%d日 %H:%M:%S')


def visualize():
    with gr.Blocks() as demo:
        gr.Markdown("# **北京地铁查询系统**")
        with gr.Tab("最短时间"):
            with gr.Row():
                gr.Image(label="北京地铁线路图", value="source//map.png", scale=10)
                with gr.Column():
                    gr.Textbox(label="版权声明",
                            value="作者:\n北京邮电大学\n人工智能学院\n吴黄璇\n创建于2023年9月", scale=1)
                    start = gr.Textbox(lines=1, label="起点", placeholder="输入起点...", scale=1)
                    end = gr.Textbox(lines=1, label="终点", placeholder="输入终点...", scale=1)
                    now_time = gr.Textbox(label="查询时的时刻", placeholder="点击查询以获得查询时的时间...", scale=1)
                    button = gr.Button("查询", scale=1)
                    way = gr.Textbox(label="乘车方案", scale=1)
                    time = gr.Textbox(label="乘车时间", scale=1)
                    dist = gr.Textbox(label="乘车距离", scale=1)
                    price = gr.Textbox(label="票价", scale=1)
            button.click(short_time,
                        inputs=[start, end],
                        outputs=[way, time, dist, price]
                        )
            button.click(get_time, outputs=now_time)
        with gr.Tab("最少换乘"):
            with gr.Row():
                gr.Image(label="北京地铁线路图", value="source//map.png", scale=10)
                with gr.Column():
                    gr.Textbox(label="版权声明",
                            value="作者:\n北京邮电大学\n人工智能学院\n吴黄璇\n创建于2023年9月", scale=1)
                    start = gr.Textbox(lines=1, label="起点", placeholder="输入起点...", scale=1)
                    end = gr.Textbox(lines=1, label="终点", placeholder="输入终点...", scale=1)
                    now_time = gr.Textbox(label="查询时的时刻", placeholder="点击查询以获得查询时的时间...", scale=1)
                    button = gr.Button("查询", scale=1)
                    way = gr.Textbox(label="乘车方案", scale=1)
                    time = gr.Textbox(label="乘车时间", scale=1)
                    dist = gr.Textbox(label="乘车距离", scale=1)
                    price = gr.Textbox(label="票价", scale=1)
            button.click(min_transfer,
                        inputs=[start, end],
                        outputs=[way, time, dist, price]
                        )
            button.click(get_time, outputs=now_time)
        with gr.Tab("删除线路"):
            with gr.Row():
                gr.Image(value="source//palace_museum.jpg", show_label=False, show_download_button=False)
                with gr.Column():
                    command = gr.Textbox(label="待删线路",
                                        placeholder="请全部中文输入，例如：“一号线”，“昌平线”(S1号线和亦庄T1线除外)\n注意：\n一号线和八通线合称一号线\n四号线和大兴线合称四号线",
                                        lines=4)
                    result = gr.Textbox(label="结果")
                    button = gr.Button("删除")
                    button.click(delete_line, inputs=command, outputs=result)
        with gr.Tab("增加线路"):
            with gr.Row():
                gr.Image(value="source//palace_museum.jpg", show_label=False, show_download_button=False)
                with gr.Column():
                    command = gr.Textbox(label="待添线路",
                                        placeholder="请全部中文输入，例如：“一号线”，“昌平线”(S1号线和亦庄T1线除外)\n注意：\n一号线和八通线合称一号线\n四号线和大兴线合称四号线",
                                        lines=4)
                    result = gr.Textbox(label="结果")
                    button = gr.Button("添加")
                    button.click(add_line, inputs=command, outputs=result)
    demo.launch()


if __name__ == "__main__":
    load_station_data()
    print("启动WebUI：")
    visualize()
