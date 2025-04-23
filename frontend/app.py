import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
import os
import time
from datetime import datetime
import io
import uuid
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.stateful_button import button
import extra_streamlit_components as stx

# 配置页面
st.set_page_config(
    page_title="自动化测试平台",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 版本号
VERSION = "v1.2"

# API基础URL
API_BASE_URL = "http://localhost:8000/api"

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4257B2;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #888888;
        margin-bottom: 2rem;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-failed {
        color: #dc3545;
        font-weight: bold;
    }
    .status-running {
        color: #007bff;
        font-weight: bold;
    }
    .status-waiting {
        color: #ffc107;
        font-weight: bold;
    }
    .status-canceled {
        color: #6c757d;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 4rem;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 0.5rem 0.5rem 0 0;
        gap: 0.5rem;
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4257B2;
        color: white;
    }
    div[data-testid="stForm"] {
        border: 1px solid #ddd;
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
    }
    .upload-area {
        border: 2px dashed #ddd;
        border-radius: 0.5rem;
        padding: 2rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .card-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
    }
    .card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
        flex: 1;
        min-width: 200px;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session_state
if "refresh_data" not in st.session_state:
    st.session_state.refresh_data = False

if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = 0

if "download_report_id" not in st.session_state:
    st.session_state.download_report_id = None

if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False

if "last_refresh_time" not in st.session_state:
    st.session_state.last_refresh_time = datetime.now()

if "upload_progress" not in st.session_state:
    st.session_state.upload_progress = 0

if "temp_files" not in st.session_state:
    st.session_state.temp_files = []

if "notification_queue" not in st.session_state:
    st.session_state.notification_queue = []


# 辅助函数
def show_notifications():
    """显示通知队列中的消息"""
    if st.session_state.notification_queue:
        for msg_type, msg in st.session_state.notification_queue:
            if msg_type == "success":
                st.toast(f"✅ {msg}")
            elif msg_type == "error":
                st.toast(f"❌ {msg}")
            elif msg_type == "info":
                st.toast(f"ℹ️ {msg}")
            elif msg_type == "warning":
                st.toast(f"⚠️ {msg}")
        st.session_state.notification_queue = []


def add_notification(msg_type, msg):
    """添加通知到队列"""
    st.session_state.notification_queue.append((msg_type, msg))


def fetch_data(endpoint):
    """从API获取数据"""
    with st.spinner(f"正在获取数据..."):
        try:
            response = requests.get(f"{API_BASE_URL}/{endpoint}")
            if response.status_code == 200:
                add_notification("success", f"成功获取{endpoint}数据")
                return response.json()
            else:
                add_notification("error", f"获取数据失败: {response.status_code}")
                return []
        except Exception as e:
            add_notification("error", f"请求异常: {str(e)}")
            return []


def delete_item(endpoint, item_id, item_name):
    """删除项目"""
    with st.spinner(f"正在删除 {item_name}..."):
        try:
            response = requests.delete(f"{API_BASE_URL}/{endpoint}/{item_id}")
            if response.status_code == 200:
                add_notification("success", f"成功删除: {item_name}")
                st.session_state.refresh_data = True
                return True
            else:
                add_notification("error", f"删除失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            add_notification("error", f"请求异常: {str(e)}")
            return False


def upload_file(endpoint, file, file_type, additional_data=None):
    """上传文件"""
    if not file:
        add_notification("warning", "请先选择文件")
        return False

    # 检查文件大小
    if file.size > 10 * 1024 * 1024:  # 10MB
        add_notification("error", "文件大小超过10MB限制")
        return False

    # 模拟上传进度
    progress_bar = st.progress(0)
    for i in range(101):
        # 更新进度条
        progress_bar.progress(i)
        st.session_state.upload_progress = i
        if i < 70:
            time.sleep(0.01)  # 前70%进度快一些
        else:
            time.sleep(0.03)  # 后30%进度慢一些

    try:
        files = {"file": (file.name, file, file.type)}
        data = {"file_type": file_type}

        # 添加额外数据
        if additional_data:
            data.update(additional_data)

        with st.spinner("正在上传文件到服务器..."):
            response = requests.post(
                f"{API_BASE_URL}/{endpoint}",
                files=files,
                data=data
            )

        if response.status_code == 200:
            add_notification("success", f"成功上传: {file.name}")
            # 记录临时文件，以便后续清理
            st.session_state.temp_files.append(file.name)
            st.session_state.refresh_data = True
            return True
        else:
            add_notification("error", f"上传失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        add_notification("error", f"请求异常: {str(e)}")
        return False
    finally:
        # 清除进度条
        progress_bar.empty()
        st.session_state.upload_progress = 0


def download_file(endpoint, file_id, file_name):
    """下载文件"""
    with st.spinner(f"正在准备下载 {file_name}..."):
        try:
            response = requests.get(f"{API_BASE_URL}/{endpoint}/{file_id}")
            if response.status_code == 200:
                add_notification("success", f"准备下载: {file_name}")
                return response.content
            else:
                add_notification("error", f"下载失败: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            add_notification("error", f"请求异常: {str(e)}")
            return None


def format_duration(seconds):
    """格式化持续时间"""
    if seconds is None:
        return "未完成"

    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)

    if hours > 0:
        return f"{hours}小时 {minutes}分钟 {seconds}秒"
    elif minutes > 0:
        return f"{minutes}分钟 {seconds}秒"
    else:
        return f"{seconds}秒"


def get_status_icon_and_color(status):
    """获取状态对应的图标和颜色"""
    status_map = {
        "成功": ("✅", "status-success"),
        "失败": ("❌", "status-failed"),
        "运行中": ("🔄", "status-running"),
        "等待中": ("⏳", "status-waiting"),
        "已取消": ("⏹️", "status-canceled")
    }
    return status_map.get(status, ("❓", ""))


def render_status(status):
    """渲染带有图标和颜色的状态"""
    icon, css_class = get_status_icon_and_color(status)
    return f'<span class="{css_class}">{icon} {status}</span>'


def clean_temp_files():
    """清理临时文件"""
    for file_name in st.session_state.temp_files:
        try:
            if os.path.exists(file_name):
                os.remove(file_name)
        except Exception as e:
            st.warning(f"清理临时文件失败: {str(e)}")

    st.session_state.temp_files = []
    add_notification("info", "已清理临时文件")


def render_metric_card(title, value, delta=None, icon=None):
    """渲染指标卡片"""
    icon_html = f'<span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>' if icon else ''
    delta_html = f'<span style="color: {"green" if delta >= 0 else "red"}; font-size: 0.9rem;">{"+" if delta >= 0 else ""}{delta}%</span>' if delta is not None else ''

    return f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: #666;">{icon_html}{title}</div>
        <div style="font-size: 1.8rem; font-weight: bold; margin: 0.5rem 0;">{value} {delta_html}</div>
    </div>
    """


# 侧边栏
with st.sidebar:
    st.image("https://www.python.org/static/community_logos/python-logo-generic.svg", width=200)
    st.title("自动化测试平台")
    st.caption(f"版本: {VERSION}")
    st.markdown("---")

    # 导航选项
    nav_options = ["📊 仪表盘", "📝 测试用例管理", "🔧 任务管理", "📈 测试报告查看", "📜 任务历史记录"]
    selected_nav = st.radio("导航", nav_options, index=st.session_state.selected_tab)
    st.session_state.selected_tab = nav_options.index(selected_nav)

    st.markdown("---")

    # 自动刷新选项
    auto_refresh = st.checkbox("自动刷新数据", value=st.session_state.auto_refresh)
    if auto_refresh != st.session_state.auto_refresh:
        st.session_state.auto_refresh = auto_refresh
        if auto_refresh:
            add_notification("info", "已开启自动刷新")
        else:
            add_notification("info", "已关闭自动刷新")

    refresh_interval = st.slider("刷新间隔(秒)", min_value=5, max_value=60, value=15, step=5, disabled=not auto_refresh)

    # 手动刷新按钮
    if st.button("🔄 刷新数据", use_container_width=True):
        st.session_state.refresh_data = True
        add_notification("info", "正在刷新数据...")

    # 清理临时文件
    if st.button("🧹 清理临时文件", use_container_width=True):
        clean_temp_files()

    st.markdown("---")

    # 系统信息
    st.markdown("### 系统信息")
    st.info(f"""
    - 🕒 最后刷新: {st.session_state.last_refresh_time.strftime('%H:%M:%S')}
    - 💾 临时文件: {len(st.session_state.temp_files)}个
    """)

    st.markdown("---")
    st.caption("© 2025 自动化测试平台")

# 自动刷新逻辑
if st.session_state.auto_refresh:
    current_time = datetime.now()
    time_diff = (current_time - st.session_state.last_refresh_time).total_seconds()

    if time_diff >= refresh_interval:
        st.session_state.refresh_data = True
        st.session_state.last_refresh_time = current_time

# 显示通知
show_notifications()

# 页面标题
st.markdown('<h1 class="main-header">自动化测试平台</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">高效管理和执行自动化测试任务的一站式解决方案</p>', unsafe_allow_html=True)

# 创建标签页
tab_icons = ["📊", "📝", "🔧", "📈", "📜"]
tab_labels = ["仪表盘", "测试用例管理", "任务管理", "测试报告查看", "任务历史记录"]
tabs = st.tabs([f"{icon} {label}" for icon, label in zip(tab_icons, tab_labels)])

# 0. 仪表盘
with tabs[0]:
    colored_header(
        label="系统仪表盘",
        description="查看系统整体运行状态和关键指标",
        color_name="blue-70"
    )

    # 获取统计数据
    testcases = fetch_data("testcases")
    tasks = fetch_data("tasks")
    reports = fetch_data("reports")
    history = fetch_data("history")

    # 计算关键指标
    total_testcases = len(testcases)
    total_tasks = len(tasks)
    total_reports = len(reports)
    total_history = len(history)

    # 计算成功率
    success_rate = 0
    if tasks:
        success_count = sum(1 for task in tasks if task.get("status") == "成功")
        success_rate = round((success_count / len(tasks)) * 100, 2)

    # 计算平均执行时间
    avg_duration = 0
    if history:
        durations = [h.get("duration", 0) for h in history if h.get("duration") is not None]
        if durations:
            avg_duration = sum(durations) / len(durations)

    # 显示关键指标卡片
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            render_metric_card("测试用例总数", total_testcases, icon="📝"),
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            render_metric_card("任务总数", total_tasks, icon="🔧"),
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            render_metric_card("成功率", f"{success_rate}%", icon="✅"),
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            render_metric_card("平均执行时间", format_duration(avg_duration), icon="⏱️"),
            unsafe_allow_html=True
        )

    # 任务状态分布
    st.subheader("📊 任务状态分布")
    if tasks:
        status_counts = pd.DataFrame(tasks).get("status", pd.Series()).value_counts().reset_index()
        status_counts.columns = ["状态", "数量"]

        fig = px.pie(
            status_counts,
            values="数量",
            names="状态",
            title="任务状态分布",
            color="状态",
            color_discrete_map={
                "成功": "#28a745",
                "失败": "#dc3545",
                "运行中": "#007bff",
                "等待中": "#ffc107",
                "已取消": "#6c757d"
            },
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无任务数据")

    # 最近任务执行情况
    st.subheader("📈 最近任务执行情况")
    if history:
        df_history = pd.DataFrame(history)

        # 格式化时间
        if "start_time" in df_history.columns:
            df_history["start_time"] = pd.to_datetime(df_history["start_time"])
            df_history["date"] = df_history["start_time"].dt.date

        # 按日期统计任务数量和成功率
        daily_stats = df_history.groupby("date").agg(
            任务数=("id", "count"),
            成功数=("status", lambda x: (x == "成功").sum())
        ).reset_index()

        daily_stats["成功率"] = (daily_stats["成功数"] / daily_stats["任务数"] * 100).round(2)
        daily_stats["date"] = pd.to_datetime(daily_stats["date"])
        daily_stats = daily_stats.sort_values("date")

        # 绘制趋势图
        fig = px.line(
            daily_stats,
            x="date",
            y=["任务数", "成功率"],
            title="任务执行趋势",
            labels={"value": "数值", "date": "日期", "variable": "指标"},
            color_discrete_map={"任务数": "#4257B2", "成功率": "#28a745"}
        )

        fig.update_layout(
            xaxis_title="日期",
            yaxis_title="任务数",
            yaxis2=dict(
                title="成功率 (%)",
                overlaying="y",
                side="right",
                range=[0, 100]
            ),
            legend_title="指标"
        )

        # 将成功率映射到右侧Y轴
        fig.update_traces(
            yaxis="y2",
            selector=dict(name="成功率")
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无历史数据")

    # 最近执行的任务
    st.subheader("🕒 最近执行的任务")
    if history:
        df_recent = pd.DataFrame(history).sort_values("start_time", ascending=False).head(5)

        # 格式化时间
        if "start_time" in df_recent.columns:
            df_recent["start_time"] = pd.to_datetime(df_recent["start_time"]).dt.strftime("%Y-%m-%d %H:%M:%S")

        if "end_time" in df_recent.columns:
            df_recent["end_time"] = df_recent["end_time"].apply(
                lambda x: pd.to_datetime(x).strftime("%Y-%m-%d %H:%M:%S") if x else "未完成"
            )

        # 格式化持续时间
        if "duration" in df_recent.columns:
            df_recent["duration"] = df_recent["duration"].apply(format_duration)

        # 显示表格
        st.dataframe(
            df_recent,
            column_config={
                "id": st.column_config.TextColumn("ID", width="small"),
                "task_id": st.column_config.TextColumn("任务ID", width="small"),
                "task_name": st.column_config.TextColumn("任务名称", width="medium"),
                "status": st.column_config.TextColumn(
                    "状态",
                    width="small",
                    help="任务执行的最终状态"
                ),
                "start_time": st.column_config.TextColumn("开始时间", width="medium"),
                "end_time": st.column_config.TextColumn("结束时间", width="medium"),
                "duration": st.column_config.TextColumn("持续时间", width="medium")
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("暂无历史数据")

# 1. 测试用例管理
with tabs[1]:
    colored_header(
        label="测试用例管理",
        description="上传、查看和管理测试用例",
        color_name="blue-70"
    )

    # 上传测试用例
    with st.expander("📤 上传测试用例", expanded=True):
        # 使用两列布局
        col1, col2 = st.columns([2, 1])

        with col1:
            # 创建拖放上传区域
            st.markdown('<div class="upload-area">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "拖拽文件到此处或点击选择文件",
                type=["py"],
                accept_multiple_files=False,
                help="支持Python文件(.py)，文件大小不超过10MB",
                key="testcase_uploader"
            )

            if uploaded_file:
                st.success(f"已选择文件: {uploaded_file.name} ({round(uploaded_file.size / 1024, 2)} KB)")

            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("### 文件信息")

            file_type = st.selectbox(
                "测试类型",
                ["Web测试", "API测试", "移动测试", "性能测试", "安全测试"],
                help="选择测试用例的类型"
            )

            test_id = st.text_input("测试ID", help="输入测试用例的唯一标识符", placeholder="例如: TC001")
            test_author = st.text_input("作者", help="输入测试用例的作者", placeholder="例如: 张三")
            test_version = st.text_input("版本", help="输入测试用例的版本", placeholder="例如: 1.0.0")

            # 上传按钮
            upload_button = st.button("📤 上传测试用例", use_container_width=True, type="primary")

            if upload_button:
                if uploaded_file:
                    # 准备额外数据
                    additional_data = {
                        "test_id": test_id,
                        "author": test_author,
                        "version": test_version
                    }

                    # 上传文件
                    upload_success = upload_file("testcases", uploaded_file, file_type, additional_data)

                    if upload_success:
                        # 清空上传器
                        st.session_state["testcase_uploader"] = None
                else:
                    add_notification("warning", "请先选择文件")

    # 测试用例列表
    st.subheader("📋 测试用例列表")

    # 获取测试用例数据
    testcases = fetch_data("testcases")

    if testcases:
        # 转换为DataFrame
        df_testcases = pd.DataFrame(testcases)

        # 添加额外字段
        if "author" not in df_testcases.columns:
            df_testcases["author"] = "未知"

        if "version" not in df_testcases.columns:
            df_testcases["version"] = "1.0.0"

        if "test_id" not in df_testcases.columns:
            df_testcases["test_id"] = ["TC" + str(i + 1).zfill(3) for i in range(len(df_testcases))]

        # 格式化创建时间
        if "created_at" in df_testcases.columns:
            df_testcases["created_at"] = pd.to_datetime(df_testcases["created_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")

        # 添加操作列
        df_testcases["操作"] = ["操作" for _ in range(len(df_testcases))]

        # 添加筛选选项
        col1, col2, col3 = st.columns(3)

        with col1:
            filter_type = st.multiselect(
                "按类型筛选",
                options=df_testcases["type"].unique(),
                default=[]
            )

        with col2:
            filter_author = st.multiselect(
                "按作者筛选",
                options=df_testcases["author"].unique(),
                default=[]
            )

        with col3:
            search_term = st.text_input("搜索测试用例", placeholder="输入关键词搜索")

        # 应用筛选
        filtered_df = df_testcases.copy()

        if filter_type:
            filtered_df = filtered_df[filtered_df["type"].isin(filter_type)]

        if filter_author:
            filtered_df = filtered_df[filtered_df["author"].isin(filter_author)]

        if search_term:
            filtered_df = filtered_df[
                filtered_df["name"].str.contains(search_term, case=False) |
                filtered_df["test_id"].str.contains(search_term, case=False)
                ]

        # 显示表格
        edited_df = st.data_editor(
            filtered_df,
            column_config={
                "id": st.column_config.TextColumn("ID", width="small"),
                "test_id": st.column_config.TextColumn("测试ID", width="small"),
                "name": st.column_config.TextColumn("名称", width="medium"),
                "type": st.column_config.SelectboxColumn(
                    "类型",
                    width="small",
                    options=["Web测试", "API测试", "移动测试", "性能测试", "安全测试"],
                    required=True
                ),
                "author": st.column_config.TextColumn("作者", width="small"),
                "version": st.column_config.TextColumn("版本", width="small"),
                "created_at": st.column_config.TextColumn("创建时间", width="medium"),
                "操作": st.column_config.ButtonColumn(
                    "操作",
                    help="点击执行操作",
                    width="small"
                )
            },
            use_container_width=True,
            hide_index=True,
            disabled=["id", "test_id", "name", "created_at"],
            num_rows="dynamic"
        )

        # 处理按钮点击
        for i, row in edited_df.iterrows():
            if row["操作"] == "操作":
                # 创建唯一行ID
                row_id = f"tc_{row['id']}"

                # 创建操作按钮容器
                with st.expander(f"测试用例: {row['name']} 的操作", expanded=False):
                    action_col1, action_col2, action_col3 = st.columns(3)

                    with action_col1:
                        if st.button(f"🗑️ 删除", key=f"delete_{row_id}"):
                            if delete_item("testcases", row["id"], row["name"]):
                                st.experimental_rerun()

                    with action_col2:
                        if st.button(f"📋 复制路径", key=f"copy_{row_id}"):
                            # 复制路径到剪贴板 (在网页中无法直接实现，使用显示代替)
                            st.code(f"/path/to/testcases/{row['name']}")
                            add_notification("success", f"已复制路径: {row['name']}")

                    with action_col3:
                        if st.button(f"⬇️ 下载", key=f"download_{row_id}"):
                            file_content = download_file("testcases", row["id"], row["name"])
                            if file_content:
                                st.download_button(
                                    label="点击下载文件",
                                    data=file_content,
                                    file_name=row["name"],
                                    mime="text/x-python",
                                    key=f"download_button_{row_id}"
                                )

        # 测试用例类型统计
        st.subheader("📊 测试用例类型统计")
        type_counts = df_testcases["type"].value_counts().reset_index()
        type_counts.columns = ["类型", "数量"]

        # 使用两列布局
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            fig1 = px.pie(
                type_counts,
                values="数量",
                names="类型",
                title="测试用例类型分布",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig1, use_container_width=True)

        with chart_col2:
            fig2 = px.bar(
                type_counts,
                x="类型",
                y="数量",
                title="测试用例类型数量",
                color="类型",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            st.plotly_chart(fig2, use_container_width=True)

        # 作者统计
        st.subheader("👨‍💻 作者统计")
        author_counts = df_testcases["author"].value_counts().reset_index()
        author_counts.columns = ["作者", "数量"]

        fig3 = px.bar(
            author_counts,
            x="作者",
            y="数量",
            title="各作者测试用例数量",
            color="作者",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("暂无测试用例")
        st.markdown("""
                ### 开始使用
                1. 点击上方的"上传测试用例"
                2. 选择或拖拽Python测试文件
                3. 填写测试类型和其他信息
                4. 点击"上传测试用例"按钮
                """)

    # 2. 任务管理
    with tabs[2]:
        colored_header(
            label="任务管理",
            description="创建和管理测试任务",
            color_name="blue-70"
        )

        # 创建测试任务
        with st.expander("🔧 创建测试任务", expanded=True):
            with st.form("create_task_form", clear_on_submit=True):
                st.markdown("### 基本信息")

                task_name = st.text_input(
                    "任务名称",
                    help="输入任务的名称，不超过50个字符",
                    placeholder="例如: 登录功能测试-2025-04-23"
                )

                task_desc = st.text_area(
                    "任务描述",
                    help="输入任务的详细描述",
                    placeholder="例如: 测试系统登录功能的各种场景",
                    max_chars=200
                )

                st.markdown("### 测试用例选择")

                # 获取测试用例列表供选择
                testcases = fetch_data("testcases")
                if not testcases:
                    st.warning("没有可用的测试用例，请先上传测试用例")
                    testcase_options = []
                    testcase_ids = []
                else:
                    # 转换为DataFrame以便更好地展示
                    df_tc = pd.DataFrame(testcases)

                    # 添加测试ID列（如果没有）
                    if "test_id" not in df_tc.columns:
                        df_tc["test_id"] = ["TC" + str(i + 1).zfill(3) for i in range(len(df_tc))]

                    # 创建选项列表
                    testcase_options = [f"{tc['test_id']} - {tc['name']} ({tc['type']})" for _, tc in df_tc.iterrows()]
                    testcase_ids = df_tc["id"].tolist()

                # 按类型分组显示测试用例
                if testcases:
                    # 获取所有类型
                    test_types = df_tc["type"].unique()

                    # 为每种类型创建一个选择器
                    selected_ids = []

                    for test_type in test_types:
                        st.markdown(f"#### {test_type}")

                        # 过滤该类型的测试用例
                        type_testcases = df_tc[df_tc["type"] == test_type]

                        # 创建选项列表
                        type_options = [f"{tc['test_id']} - {tc['name']}" for _, tc in type_testcases.iterrows()]
                        type_ids = type_testcases["id"].tolist()

                        # 多选框
                        selected_type_cases = st.multiselect(
                            f"选择{test_type}用例",
                            options=type_options,
                            default=[],
                            key=f"multiselect_{test_type}"
                        )

                        # 收集选中的ID
                        if selected_type_cases:
                            for case in selected_type_cases:
                                idx = type_options.index(case)
                                selected_ids.append(type_ids[idx])
                else:
                    selected_ids = []

                st.markdown("### 调度设置")

                schedule_type = st.selectbox(
                    "调度类型",
                    ["立即执行", "定时执行", "周期执行"],
                    help="选择任务的执行方式"
                )

                schedule_time = None
                if schedule_type in ["定时执行", "周期执行"]:
                    col1, col2 = st.columns(2)
                    with col1:
                        schedule_date = st.date_input("选择日期")
                    with col2:
                        schedule_time_input = st.time_input("选择时间")
                    schedule_time = datetime.combine(schedule_date, schedule_time_input).isoformat()

                    if schedule_type == "周期执行":
                        repeat_option = st.selectbox(
                            "重复周期",
                            ["每天", "每周", "每月"]
                        )

                st.markdown("### 执行环境")

                env_col1, env_col2 = st.columns(2)

                with env_col1:
                    target_env = st.selectbox(
                        "目标环境",
                        ["开发环境", "测试环境", "预发布环境", "生产环境"]
                    )

                with env_col2:
                    browser = st.selectbox(
                        "浏览器",
                        ["Chrome", "Firefox", "Edge", "Safari"],
                        disabled=not any("Web测试" in tc for tc in testcase_options if tc in selected_testcases)
                    )

                # 提交按钮
                col1, col2 = st.columns(2)
                with col1:
                    submit_button = st.form_submit_button("✅ 创建任务", use_container_width=True, type="primary")
                with col2:
                    cancel_button = st.form_submit_button("❌ 取消", use_container_width=True)

                if submit_button:
                    if not task_name:
                        add_notification("error", "请输入任务名称")
                    elif len(task_name) > 50:
                        add_notification("error", "任务名称不能超过50个字符")
                    elif not selected_ids:
                        add_notification("error", "请选择至少一个测试用例")
                    else:
                        try:
                            payload = {
                                "name": task_name,
                                "description": task_desc,
                                "testcase_ids": selected_ids,
                                "schedule_type": schedule_type,
                                "schedule_time": schedule_time,
                                "target_env": target_env,
                                "browser": browser if "Web测试" in df_tc[df_tc["id"].isin(selected_ids)][
                                    "type"].values else None
                            }

                            with st.spinner("正在创建任务..."):
                                response = requests.post(f"{API_BASE_URL}/tasks", json=payload)

                                if response.status_code == 200:
                                    add_notification("success", "任务创建成功!")
                                    st.session_state.refresh_data = True
                                else:
                                    add_notification("error", f"任务创建失败: {response.status_code} - {response.text}")
                        except Exception as e:
                            add_notification("error", f"请求异常: {str(e)}")

        # 任务列表
        st.subheader("📋 任务列表")

        # 获取任务数据
        tasks = fetch_data("tasks")

        if tasks:
            # 转换为DataFrame
            df_tasks = pd.DataFrame(tasks)

            # 格式化创建时间和调度时间
            if "created_at" in df_tasks.columns:
                df_tasks["created_at"] = pd.to_datetime(df_tasks["created_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")

            if "schedule_time" in df_tasks.columns:
                df_tasks["schedule_time"] = df_tasks["schedule_time"].apply(
                    lambda x: pd.to_datetime(x).strftime("%Y-%m-%d %H:%M:%S") if x else "无"
                )

            # 添加状态HTML渲染
            df_tasks["状态HTML"] = df_tasks["status"].apply(render_status)

            # 添加操作列
            df_tasks["操作"] = ["操作" for _ in range(len(df_tasks))]

            # 添加筛选选项
            col1, col2, col3 = st.columns(3)

            with col1:
                filter_status = st.multiselect(
                    "按状态筛选",
                    options=df_tasks["status"].unique(),
                    default=[]
                )

            with col2:
                filter_schedule = st.multiselect(
                    "按调度类型筛选",
                    options=df_tasks["schedule_type"].unique(),
                    default=[]
                )

            with col3:
                search_task = st.text_input("搜索任务", placeholder="输入关键词搜索")

            # 应用筛选
            filtered_df = df_tasks.copy()

            if filter_status:
                filtered_df = filtered_df[filtered_df["status"].isin(filter_status)]

            if filter_schedule:
                filtered_df = filtered_df[filtered_df["schedule_type"].isin(filter_schedule)]

            if search_task:
                filtered_df = filtered_df[
                    filtered_df["name"].str.contains(search_task, case=False) |
                    filtered_df["id"].astype(str).str.contains(search_task, case=False)
                    ]

            # 显示表格
            st.dataframe(
                filtered_df,
                column_config={
                    "id": st.column_config.TextColumn("ID", width="small"),
                    "name": st.column_config.TextColumn("名称", width="medium"),
                    "status": st.column_config.TextColumn("状态", width="small"),
                    "状态HTML": st.column_config.Column("状态", width="small"),
                    "created_at": st.column_config.TextColumn("创建时间", width="medium"),
                    "schedule_type": st.column_config.TextColumn("调度类型", width="small"),
                    "schedule_time": st.column_config.TextColumn("调度时间", width="medium"),
                    "target_env": st.column_config.TextColumn("目标环境", width="small"),
                    "操作": st.column_config.ButtonColumn(
                        "操作",
                        help="点击执行操作",
                        width="small"
                    )
                },
                use_container_width=True,
                hide_index=True,
                column_order=["id", "name", "状态HTML", "created_at", "schedule_type", "schedule_time", "target_env",
                              "操作"]
            )

            # 处理按钮点击
            for i, row in filtered_df.iterrows():
                if row["操作"] == "操作":
                    # 创建唯一行ID
                    row_id = f"task_{row['id']}"

                    # 创建操作按钮容器
                    with st.expander(f"任务: {row['name']} 的操作", expanded=False):
                        action_col1, action_col2, action_col3, action_col4 = st.columns(4)

                        with action_col1:
                            if st.button(f"🗑️ 删除", key=f"delete_{row_id}"):
                                if delete_item("tasks", row["id"], row["name"]):
                                    st.experimental_rerun()

                        with action_col2:
                            if st.button(f"▶️ 执行", key=f"run_{row_id}",
                                         disabled=row["status"] in ["运行中", "等待中"]):
                                try:
                                    with st.spinner(f"正在启动任务 {row['name']}..."):
                                        response = requests.post(f"{API_BASE_URL}/tasks/{row['id']}/run")

                                        if response.status_code == 200:
                                            add_notification("success", f"任务 {row['name']} 已启动")
                                            st.session_state.refresh_data = True
                                        else:
                                            add_notification("error",
                                                             f"启动任务失败: {response.status_code} - {response.text}")
                                except Exception as e:
                                    add_notification("error", f"请求异常: {str(e)}")

                        with action_col3:
                            if st.button(f"⏹️ 停止", key=f"stop_{row_id}",
                                         disabled=row["status"] not in ["运行中", "等待中"]):
                                try:
                                    with st.spinner(f"正在停止任务 {row['name']}..."):
                                        response = requests.post(f"{API_BASE_URL}/tasks/{row['id']}/stop")

                                        if response.status_code == 200:
                                            add_notification("success", f"任务 {row['name']} 已停止")
                                            st.session_state.refresh_data = True
                                        else:
                                            add_notification("error",
                                                             f"停止任务失败: {response.status_code} - {response.text}")
                                except Exception as e:
                                    add_notification("error", f"请求异常: {str(e)}")

                        with action_col4:
                            if st.button(f"📋 查看报告", key=f"report_{row_id}",
                                         disabled=row["status"] not in ["成功", "失败"]):
                                # 切换到报告页面
                                st.session_state.selected_tab = 3  # 报告页面索引
                                st.session_state.selected_task_report = row["id"]
                                st.experimental_rerun()

            # 任务状态统计
            st.subheader("📊 任务状态统计")
            status_counts = df_tasks["status"].value_counts().reset_index()
            status_counts.columns = ["状态", "数量"]

            # 使用两列布局
            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                fig1 = px.pie(
                    status_counts,
                    values="数量",
                    names="状态",
                    title="任务状态分布",
                    color="状态",
                    color_discrete_map={
                        "成功": "#28a745",
                        "失败": "#dc3545",
                        "运行中": "#007bff",
                        "等待中": "#ffc107",
                        "已取消": "#6c757d"
                    }
                )
                fig1.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig1, use_container_width=True)

            with chart_col2:
                fig2 = px.bar(
                    status_counts,
                    x="状态",
                    y="数量",
                    title="任务状态数量",
                    color="状态",
                    color_discrete_map={
                        "成功": "#28a745",
                        "失败": "#dc3545",
                        "运行中": "#007bff",
                        "等待中": "#ffc107",
                        "已取消": "#6c757d"
                    }
                )
                st.plotly_chart(fig2, use_container_width=True)

            # 调度类型统计
            st.subheader("📅 调度类型统计")
            schedule_counts = df_tasks["schedule_type"].value_counts().reset_index()
            schedule_counts.columns = ["调度类型", "数量"]

            fig3 = px.pie(
                schedule_counts,
                values="数量",
                names="调度类型",
                title="任务调度类型分布",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig3.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("暂无任务")
            st.markdown("""
                ### 开始使用
                1. 点击上方的"创建测试任务"
                2. 填写任务名称和描述
                3. 选择要执行的测试用例
                4. 设置调度方式和执行环境
                5. 点击"创建任务"按钮
                """)

    # 3. 测试报告查看
    with tabs[3]:
        colored_header(
            label="测试报告查看",
            description="查看和分析测试报告",
            color_name="blue-70"
        )

        # 获取报告数据
        reports = fetch_data("reports")

        if reports:
            # 转换为DataFrame
            df_reports = pd.DataFrame(reports)

            # 格式化创建时间
            if "created_at" in df_reports.columns:
                df_reports["created_at"] = pd.to_datetime(df_reports["created_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")

            # 计算通过率
            df_reports["通过率"] = (df_reports["passed"] / (df_reports["passed"] + df_reports["failed"]) * 100).round(2)
            df_reports["通过率文本"] = df_reports["通过率"].apply(lambda x: f"{x}%")

            # 添加状态列
            df_reports["状态"] = df_reports.apply(
                lambda row: "成功" if row["failed"] == 0 else "部分成功" if row["passed"] > 0 else "失败",
                axis=1
            )

            # 添加状态HTML渲染
            df_reports["状态HTML"] = df_reports["状态"].apply(render_status)

            # 添加操作列
            df_reports["操作"] = ["操作" for _ in range(len(df_reports))]

            # 添加筛选选项
            col1, col2, col3 = st.columns(3)

            with col1:
                filter_status = st.multiselect(
                    "按状态筛选",
                    options=df_reports["状态"].unique(),
                    default=[]
                )

            with col2:
                min_pass_rate = st.slider("最低通过率", 0, 100, 0, 5)

            with col3:
                search_report = st.text_input("搜索报告", placeholder="输入关键词搜索")

            # 应用筛选
            filtered_df = df_reports.copy()

            if filter_status:
                filtered_df = filtered_df[filtered_df["状态"].isin(filter_status)]

            filtered_df = filtered_df[filtered_df["通过率"] >= min_pass_rate]

            if search_report:
                filtered_df = filtered_df[
                    filtered_df["task_name"].str.contains(search_report, case=False) |
                    filtered_df["id"].astype(str).str.contains(search_report, case=False) |
                    filtered_df["task_id"].astype(str).str.contains(search_report, case=False)
                    ]

            # 显示表格
            st.dataframe(
                filtered_df,
                column_config={
                    "id": st.column_config.TextColumn("ID", width="small"),
                    "task_id": st.column_config.TextColumn("任务ID", width="small"),
                    "task_name": st.column_config.TextColumn("任务名称", width="medium"),
                    "total_cases": st.column_config.NumberColumn("总用例数", width="small"),
                    "passed": st.column_config.NumberColumn("通过数", width="small", format="%d"),
                    "failed": st.column_config.NumberColumn("失败数", width="small", format="%d"),
                    "通过率": st.column_config.ProgressColumn(
                        "通过率",
                        width="medium",
                        format="%d%%",
                        min_value=0,
                        max_value=100
                    ),
                    "状态HTML": st.column_config.Column("状态", width="small"),
                    "created_at": st.column_config.TextColumn("创建时间", width="medium"),
                    "操作": st.column_config.ButtonColumn(
                        "操作",
                        help="点击执行操作",
                        width="small"
                    )
                },
                use_container_width=True,
                hide_index=True,
                column_order=["id", "task_id", "task_name", "total_cases", "passed", "failed", "通过率", "状态HTML",
                              "created_at", "操作"]
            )

            # 处理按钮点击
            for i, row in filtered_df.iterrows():
                if row["操作"] == "操作":
                    # 创建唯一行ID
                    row_id = f"report_{row['id']}"

                    # 创建操作按钮容器
                    with st.expander(f"报告: {row['task_name']} 的操作", expanded=False):
                        action_col1, action_col2 = st.columns(2)

                        with action_col1:
                            if st.button(f"⬇️ 下载报告", key=f"download_{row_id}"):
                                report_content = download_file("reports", row["id"], f"report_{row['id']}.html")
                                if report_content:
                                    st.download_button(
                                        label="点击下载HTML报告",
                                        data=report_content,
                                        file_name=f"report_{row['id']}.html",
                                        mime="text/html",
                                        key=f"download_button_{row_id}"
                                    )

                        with action_col2:
                            if st.button(f"📊 查看详情", key=f"view_{row_id}"):
                                st.session_state.selected_report_id = row["id"]
                                st.session_state.selected_report_name = row["task_name"]

            # 显示选中的报告详情
            if "selected_report_id" in st.session_state and st.session_state.selected_report_id:
                report_id = st.session_state.selected_report_id
                report_name = st.session_state.selected_report_name

                st.markdown(f"## 报告详情: {report_name}")

                # 获取报告详情
                report_details = fetch_data(f"reports/{report_id}")

                if report_details:
                    # 基本信息
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("总用例数", report_details.get("total_cases", 0))

                    with col2:
                        st.metric("通过数", report_details.get("passed", 0))

                    with col3:
                        st.metric("失败数", report_details.get("failed", 0))

                    with col4:
                        pass_rate = 0
                        if report_details.get("total_cases", 0) > 0:
                            pass_rate = (report_details.get("passed", 0) / report_details.get("total_cases",
                                                                                              0) * 100).round(2)
                        st.metric("通过率", f"{pass_rate}%")

                    # 测试用例详情
                    if "test_cases" in report_details and report_details["test_cases"]:
                        st.subheader("测试用例详情")

                        df_cases = pd.DataFrame(report_details["test_cases"])

                        # 添加状态HTML渲染
                        df_cases["状态HTML"] = df_cases["status"].apply(render_status)

                        # 格式化时间
                        if "start_time" in df_cases.columns:
                            df_cases["start_time"] = pd.to_datetime(df_cases["start_time"]).dt.strftime(
                                "%Y-%m-%d %H:%M:%S")

                        if "end_time" in df_cases.columns:
                            df_cases["end_time"] = df_cases["end_time"].apply(
                                lambda x: pd.to_datetime(x).strftime("%Y-%m-%d %H:%M:%S") if x else "未完成"
                            )

                        # 格式化持续时间
                        if "duration" in df_cases.columns:
                            df_cases["duration"] = df_cases["duration"].apply(format_duration)

                        st.dataframe(
                            df_cases,
                            column_config={
                                "id": st.column_config.TextColumn("ID", width="small"),
                                "name": st.column_config.TextColumn("名称", width="medium"),
                                "status": st.column_config.TextColumn("状态", width="small"),
                                "状态HTML": st.column_config.Column("状态", width="small"),
                                "start_time": st.column_config.TextColumn("开始时间", width="medium"),
                                "end_time": st.column_config.TextColumn("结束时间", width="medium"),
                                "duration": st.column_config.TextColumn("持续时间", width="medium"),
                                "error_message": st.column_config.TextColumn("错误信息", width="large")
                            },
                            use_container_width=True,
                            hide_index=True,
                            column_order=["id", "name", "状态HTML", "start_time", "end_time", "duration",
                                          "error_message"]
                        )

                        # 测试用例状态统计
                        st.subheader("测试用例状态统计")
                        status_counts = df_cases["status"].value_counts().reset_index()
                        status_counts.columns = ["状态", "数量"]

                        # 使用两列布局
                        chart_col1, chart_col2 = st.columns(2)

                        with chart_col1:
                            fig1 = px.pie(
                                status_counts,
                                values="数量",
                                names="状态",
                                title="测试用例状态分布",
                                color="状态",
                                color_discrete_map={
                                    "成功": "#28a745",
                                    "失败": "#dc3545",
                                    "运行中": "#007bff",
                                    "等待中": "#ffc107",
                                    "已取消": "#6c757d"
                                }
                            )
                            fig1.update_traces(textposition='inside', textinfo='percent+label')
                            st.plotly_chart(fig1, use_container_width=True)

                        with chart_col2:
                            # 计算每个测试用例的执行时间
                            if "duration" in df_cases.columns:
                                # 确保duration是数值类型
                                df_cases_duration = df_cases.copy()
                                df_cases_duration["duration_seconds"] = pd.to_numeric(
                                    df_cases_duration["duration"].apply(
                                        lambda x: 0 if x == "未完成" else int(x.split("秒")[0]) if "分钟" not in x
                                        else int(x.split("分钟")[0]) * 60 + int(x.split("分钟")[1].split("秒")[0])
                                    ),
                                    errors="coerce"
                                )

                                # 按持续时间排序，取前10个
                                top_duration = df_cases_duration.sort_values("duration_seconds", ascending=False).head(
                                    10)

                                fig2 = px.bar(
                                    top_duration,
                                    x="name",
                                    y="duration_seconds",
                                    title="执行时间最长的10个测试用例(秒)",
                                    color="status",
                                    color_discrete_map={
                                        "成功": "#28a745",
                                        "失败": "#dc3545",
                                        "运行中": "#007bff",
                                        "等待中": "#ffc107",
                                        "已取消": "#6c757d"
                                    }
                                )
                                fig2.update_layout(xaxis_title="测试用例", yaxis_title="执行时间(秒)")
                                st.plotly_chart(fig2, use_container_width=True)

                        # 错误分析
                    if "test_cases" in report_details and report_details["test_cases"]:
                        failed_cases = [case for case in report_details["test_cases"] if case.get("status") == "失败"]

                        if failed_cases:
                            st.subheader("❌ 失败用例分析")

                            # 错误类型统计
                            error_types = {}
                            for case in failed_cases:
                                error_msg = case.get("error_message", "未知错误")
                                error_type = error_msg.split(":")[0] if ":" in error_msg else error_msg
                                error_types[error_type] = error_types.get(error_type, 0) + 1

                            error_df = pd.DataFrame({"错误类型": error_types.keys(), "数量": error_types.values()})

                            fig = px.bar(
                                error_df,
                                x="错误类型",
                                y="数量",
                                title="错误类型分布",
                                color="错误类型"
                            )
                            st.plotly_chart(fig, use_container_width=True)

                            # 失败用例详情
                            for i, case in enumerate(failed_cases):
                                with st.expander(f"失败用例 {i + 1}: {case.get('name', '未命名')}"):
                                    st.markdown(f"**错误信息**: {case.get('error_message', '未知错误')}")

                                    if "screenshot" in case:
                                        st.image(case["screenshot"], caption="错误截图")

                                    if "logs" in case:
                                        st.markdown("**详细日志**:")
                                        st.code(case["logs"])

                        # 报告HTML内容
                    if "html_content" in report_details and report_details["html_content"]:
                        with st.expander("查看完整HTML报告", expanded=False):
                            st.components.v1.html(report_details["html_content"], height=600, scrolling=True)

                        # 下载按钮
                    report_content = download_file("reports", report_id, f"report_{report_id}.html")
                    if report_content:
                        st.download_button(
                            label="⬇️ 下载完整HTML报告",
                            data=report_content,
                            file_name=f"report_{report_id}.html",
                            mime="text/html"
                        )

                    # 关闭详情按钮
                    if st.button("关闭详情"):
                        del st.session_state.selected_report_id
                        del st.session_state.selected_report_name
                        st.experimental_rerun()
                else:
                    st.error("获取报告详情失败")

                    # 显示测试结果图表
                st.subheader("📈 测试结果统计")

                # 准备图表数据
                chart_data = df_reports[["task_name", "passed", "failed", "total_cases", "通过率"]].copy()

                # 创建两列布局
                col1, col2 = st.columns(2)

                # 绘制柱状图
                with col1:
                    fig1 = px.bar(
                        chart_data,
                        x="task_name",
                        y=["passed", "failed"],
                        title="测试用例通过/失败数量",
                        labels={"value": "数量", "task_name": "任务名称", "variable": "结果类型"},
                        barmode="group",
                        color_discrete_map={"passed": "green", "failed": "red"}
                    )
                    fig1.update_layout(legend_title_text="结果")
                    st.plotly_chart(fig1, use_container_width=True)

                # 绘制通过率图表
                with col2:
                    fig2 = px.line(
                        chart_data,
                        x="task_name",
                        y="通过率",
                        title="测试用例通过率",
                        labels={"通过率": "通过率 (%)", "task_name": "任务名称"},
                        markers=True
                    )
                    fig2.update_traces(line_color="green")
                    fig2.update_layout(yaxis_range=[0, 100])
                    st.plotly_chart(fig2, use_container_width=True)

                # 通过率趋势
                st.subheader("📊 通过率趋势")

                # 按时间排序
                trend_data = df_reports.copy()
                trend_data["created_at"] = pd.to_datetime(trend_data["created_at"])
                trend_data = trend_data.sort_values("created_at")

                # 计算移动平均
                trend_data["通过率_MA"] = trend_data["通过率"].rolling(window=3, min_periods=1).mean()

                fig3 = px.line(
                    trend_data,
                    x="created_at",
                    y=["通过率", "通过率_MA"],
                    title="通过率趋势与3点移动平均线",
                    labels={"value": "通过率 (%)", "created_at": "时间", "variable": "指标"},
                    color_discrete_map={"通过率": "#4257B2", "通过率_MA": "#28a745"}
                )
                fig3.update_layout(yaxis_range=[0, 100])
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("暂无测试报告")
                st.markdown("""
                                ### 开始使用
                                1. 先创建并执行测试任务
                                2. 任务完成后，测试报告将自动生成
                                3. 在此页面查看测试结果和详细分析
                                """)

            # 4. 任务历史记录
            with tabs[4]:
                colored_header(
                    label="任务历史记录",
                    description="查看历史任务执行记录",
                    color_name="blue-70"
                )

                # 获取历史数据
                history = fetch_data("history")

                if history:
                    # 转换为DataFrame
                    df_history = pd.DataFrame(history)

                    # 格式化时间
                    if "start_time" in df_history.columns:
                        df_history["start_time"] = pd.to_datetime(df_history["start_time"])
                        df_history["start_time_display"] = df_history["start_time"].dt.strftime("%Y-%m-%d %H:%M:%S")

                    if "end_time" in df_history.columns:
                        df_history["end_time"] = df_history["end_time"].apply(
                            lambda x: pd.to_datetime(x) if x else None
                        )
                        df_history["end_time_display"] = df_history["end_time"].apply(
                            lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if x else "未完成"
                        )

                    # 格式化持续时间
                    if "duration" in df_history.columns:
                        df_history["duration_display"] = df_history["duration"].apply(format_duration)

                    # 添加状态HTML渲染
                    df_history["状态HTML"] = df_history["status"].apply(render_status)

                    # 添加筛选选项
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        filter_status = st.multiselect(
                            "按状态筛选",
                            options=df_history["status"].unique(),
                            default=[]
                        )

                    with col2:
                        date_range = st.date_input(
                            "日期范围",
                            value=(
                                df_history["start_time"].min().date() if not df_history[
                                    "start_time"].isna().all() else datetime.now().date(),
                                datetime.now().date()
                            ),
                            max_value=datetime.now().date()
                        )

                    with col3:
                        search_history = st.text_input("搜索历史记录", placeholder="输入关键词搜索")

                    # 应用筛选
                    filtered_df = df_history.copy()

                    if filter_status:
                        filtered_df = filtered_df[filtered_df["status"].isin(filter_status)]

                    if len(date_range) == 2:
                        start_date, end_date = date_range
                        filtered_df = filtered_df[
                            (filtered_df["start_time"].dt.date >= start_date) &
                            (filtered_df["start_time"].dt.date <= end_date)
                            ]

                    if search_history:
                        filtered_df = filtered_df[
                            filtered_df["task_name"].str.contains(search_history, case=False) |
                            filtered_df["id"].astype(str).str.contains(search_history, case=False) |
                            filtered_df["task_id"].astype(str).str.contains(search_history, case=False)
                            ]

                    # 显示表格
                    st.dataframe(
                        filtered_df,
                        column_config={
                            "id": st.column_config.TextColumn("ID", width="small"),
                            "task_id": st.column_config.TextColumn("任务ID", width="small"),
                            "task_name": st.column_config.TextColumn("任务名称", width="medium"),
                            "状态HTML": st.column_config.Column("状态", width="small"),
                            "start_time_display": st.column_config.TextColumn("开始时间", width="medium"),
                            "end_time_display": st.column_config.TextColumn("结束时间", width="medium"),
                            "duration_display": st.column_config.TextColumn("持续时间", width="medium")
                        },
                        use_container_width=True,
                        hide_index=True,
                        column_order=["id", "task_id", "task_name", "状态HTML", "start_time_display",
                                      "end_time_display", "duration_display"]
                    )

                    # 选择任务查看详情
                    selected_task_id = st.selectbox(
                        "选择任务查看详情",
                        options=filtered_df["task_id"].unique(),
                        format_func=lambda
                            x: f"任务 {x} - {filtered_df[filtered_df['task_id'] == x]['task_name'].values[0]}"
                    )

                    if selected_task_id:
                        # 获取任务详情
                        task_details = fetch_data(f"history/{selected_task_id}")

                        if task_details:
                            st.subheader("任务执行详情")

                            # 基本信息
                            status = task_details.get("status", "未知")
                            icon, status_class = get_status_icon_and_color(status)

                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("任务名称", task_details.get("task_name", "未知"))
                            with col2:
                                st.markdown(f"<h3 class='{status_class}'>{icon} {status}</h3>", unsafe_allow_html=True)
                            with col3:
                                st.metric("持续时间", format_duration(task_details.get("duration", 0)))

                            # 执行时间信息
                            col1, col2 = st.columns(2)
                            with col1:
                                start_time = task_details.get("start_time", "")
                                if start_time:
                                    start_time = pd.to_datetime(start_time).strftime("%Y-%m-%d %H:%M:%S")
                                st.metric("开始时间", start_time or "未开始")
                            with col2:
                                end_time = task_details.get("end_time", "")
                                if end_time:
                                    end_time = pd.to_datetime(end_time).strftime("%Y-%m-%d %H:%M:%S")
                                st.metric("结束时间", end_time or "未完成")

                            # 环境信息
                            st.subheader("环境信息")
                            env_col1, env_col2, env_col3 = st.columns(3)

                            with env_col1:
                                st.metric("目标环境", task_details.get("target_env", "未指定"))

                            with env_col2:
                                st.metric("浏览器", task_details.get("browser", "未指定"))

                            with env_col3:
                                st.metric("执行节点", task_details.get("node", "本地"))

                            # 测试用例执行详情
                            st.subheader("测试用例执行详情")

                            if "testcases" in task_details and task_details["testcases"]:
                                df_testcase_details = pd.DataFrame(task_details["testcases"])

                                # 添加状态HTML渲染
                                df_testcase_details["状态HTML"] = df_testcase_details["status"].apply(render_status)

                                # 格式化时间
                                if "start_time" in df_testcase_details.columns:
                                    df_testcase_details["start_time"] = pd.to_datetime(
                                        df_testcase_details["start_time"]).dt.strftime("%Y-%m-%d %H:%M:%S")

                                if "end_time" in df_testcase_details.columns:
                                    df_testcase_details["end_time"] = df_testcase_details["end_time"].apply(
                                        lambda x: pd.to_datetime(x).strftime("%Y-%m-%d %H:%M:%S") if x else "未完成"
                                    )

                                # 格式化持续时间
                                if "duration" in df_testcase_details.columns:
                                    df_testcase_details["duration"] = df_testcase_details["duration"].apply(
                                        format_duration)

                                st.dataframe(
                                    df_testcase_details,
                                    column_config={
                                        "id": st.column_config.TextColumn("ID", width="small"),
                                        "name": st.column_config.TextColumn("名称", width="medium"),
                                        "状态HTML": st.column_config.Column("状态", width="small"),
                                        "start_time": st.column_config.TextColumn("开始时间", width="medium"),
                                        "end_time": st.column_config.TextColumn("结束时间", width="medium"),
                                        "duration": st.column_config.TextColumn("持续时间", width="medium"),
                                        "error_message": st.column_config.TextColumn("错误信息", width="large")
                                    },
                                    use_container_width=True,
                                    hide_index=True,
                                    column_order=["id", "name", "状态HTML", "start_time", "end_time", "duration",
                                                  "error_message"]
                                )

                                # 测试用例状态统计
                                st.subheader("测试用例状态统计")
                                status_counts = df_testcase_details["status"].value_counts().reset_index()
                                status_counts.columns = ["状态", "数量"]

                                fig = px.pie(
                                    status_counts,
                                    values="数量",
                                    names="状态",
                                    title="测试用例状态分布",
                                    color="状态",
                                    color_discrete_map={
                                        "成功": "#28a745",
                                        "失败": "#dc3545",
                                        "运行中": "#007bff",
                                        "等待中": "#ffc107",
                                        "已取消": "#6c757d"
                                    }
                                )
                                fig.update_traces(textposition='inside', textinfo='percent+label')
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("暂无测试用例执行详情")

                            # 日志信息
                            if "logs" in task_details and task_details["logs"]:
                                st.subheader("执行日志")
                                with st.expander("查看完整日志", expanded=False):
                                    st.code(task_details["logs"])
                            else:
                                st.info("暂无执行日志")

                            # 如果有报告，添加查看报告按钮
                            if "report_id" in task_details and task_details["report_id"]:
                                if st.button("📊 查看完整报告"):
                                    st.session_state.selected_tab = 3  # 报告页面索引
                                    st.session_state.selected_report_id = task_details["report_id"]
                                    st.session_state.selected_report_name = task_details["task_name"]
                                    st.experimental_rerun()
                        else:
                            st.info("暂无任务详情")

                    # 历史趋势
                    st.subheader("📈 历史执行趋势")

                    # 按日期分组统计
                    df_history["date"] = df_history["start_time"].dt.date
                    daily_stats = df_history.groupby("date").agg(
                        任务数=("id", "count"),
                        成功数=("status", lambda x: (x == "成功").sum()),
                        失败数=("status", lambda x: (x == "失败").sum()),
                        平均持续时间=("duration", lambda x: x.mean() if x.notna().any() else 0)
                    ).reset_index()

                    daily_stats["成功率"] = (daily_stats["成功数"] / daily_stats["任务数"] * 100).round(2)
                    daily_stats["date"] = pd.to_datetime(daily_stats["date"])
                    daily_stats = daily_stats.sort_values("date")

                    # 绘制趋势图
                    fig = px.line(
                        daily_stats,
                        x="date",
                        y=["任务数", "成功数", "失败数", "成功率"],
                        title="任务执行历史趋势",
                        labels={"value": "数值", "date": "日期", "variable": "指标"},
                        color_discrete_map={
                            "任务数": "#4257B2",
                            "成功数": "#28a745",
                            "失败数": "#dc3545",
                            "成功率": "#ffc107"
                        }
                    )
                    fig.update_layout(xaxis_title="日期", yaxis_title="数量")
                    st.plotly_chart(fig, use_container_width=True)

                    # 平均持续时间趋势
                    fig2 = px.line(
                        daily_stats,
                        x="date",
                        y="平均持续时间",
                        title="平均任务持续时间趋势",
                        labels={"平均持续时间": "平均持续时间(秒)", "date": "日期"},
                        markers=True
                    )
                    fig2.update_traces(line_color="#4257B2")
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("暂无任务历史记录")
                    st.markdown("""
                                ### 开始使用
                                1. 先创建并执行测试任务
                                2. 任务执行后，历史记录将自动生成
                                3. 在此页面查看历史执行情况和趋势
                                """)

            # 如果需要刷新数据，重新加载页面
            if st.session_state.refresh_data:
                st.session_state.refresh_data = False
                st.session_state.last_refresh_time = datetime.now()
                st.experimental_rerun()


