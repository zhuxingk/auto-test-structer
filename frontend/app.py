import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
import os
import time
from datetime import datetime
import io

# 配置页面
st.set_page_config(
    page_title="自动化测试平台",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 版本号
VERSION = "v1.1"

# API基础URL
API_BASE_URL = "http://localhost:8000/api"

# 初始化session_state
if "refresh_data" not in st.session_state:
    st.session_state.refresh_data = False

if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = 0

if "download_report_id" not in st.session_state:
    st.session_state.download_report_id = None

# 侧边栏
with st.sidebar:
    st.title("自动化测试平台")
    st.markdown("---")

    # 导航选项
    nav_options = ["测试用例管理", "任务管理", "测试报告查看", "任务历史记录"]
    selected_nav = st.radio("导航", nav_options, index=st.session_state.selected_tab)
    st.session_state.selected_tab = nav_options.index(selected_nav)

    st.markdown("---")

    # 刷新数据按钮
    if st.button("刷新数据"):
        st.session_state.refresh_data = True

    st.markdown("---")
    st.info(f"版本: {VERSION}")


# 辅助函数
def fetch_data(endpoint):
    """从API获取数据"""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"获取数据失败: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"请求异常: {str(e)}")
        return []


def delete_item(endpoint, item_id):
    """删除项目"""
    try:
        response = requests.delete(f"{API_BASE_URL}/{endpoint}/{item_id}")
        if response.status_code == 200:
            st.success("删除成功!")
            st.session_state.refresh_data = True
            return True
        else:
            st.error(f"删除失败: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"请求异常: {str(e)}")
        return False


def upload_file(endpoint, file, file_type):
    """上传文件"""
    try:
        files = {"file": (file.name, file, file.type)}
        response = requests.post(
            f"{API_BASE_URL}/{endpoint}",
            files=files,
            data={"file_type": file_type}
        )
        if response.status_code == 200:
            st.success("上传成功!")
            st.session_state.refresh_data = True
            return True
        else:
            st.error(f"上传失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"请求异常: {str(e)}")
        return False


def download_file(endpoint, file_id, file_name):
    """下载文件"""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}/{file_id}")
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"下载失败: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"请求异常: {str(e)}")
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


def get_status_color(status):
    """获取状态对应的颜色"""
    status_colors = {
        "成功": "green",
        "失败": "red",
        "运行中": "blue",
        "等待中": "orange",
        "已取消": "gray"
    }
    return status_colors.get(status, "black")


# 创建标签页
tabs = st.tabs(["测试用例管理", "任务管理", "测试报告查看", "任务历史记录"])

# 1. 测试用例管理
with tabs[0]:
    st.header("测试用例管理")

    # 上传测试用例
    with st.expander("上传测试用例", expanded=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            uploaded_file = st.file_uploader(
                "选择测试用例文件",
                type=["py"],
                accept_multiple_files=False,
                help="支持Python文件(.py)，文件大小不超过10MB"
            )
        with col2:
            file_type = st.selectbox(
                "文件类型",
                ["Web测试", "API测试", "移动测试"],
                help="选择测试用例的类型"
            )
            upload_button = st.button("上传", use_container_width=True)

        if upload_button:
            if uploaded_file:
                # 检查文件大小
                if uploaded_file.size > 10 * 1024 * 1024:  # 10MB
                    st.error("文件大小超过10MB限制")
                else:
                    upload_file("testcases", uploaded_file, file_type)
            else:
                st.warning("请先选择文件")

    # 测试用例列表
    st.subheader("测试用例列表")

    # 获取测试用例数据
    testcases = fetch_data("testcases")

    if testcases:
        # 转换为DataFrame
        df_testcases = pd.DataFrame(testcases)

        # 格式化创建时间
        if "created_at" in df_testcases.columns:
            df_testcases["created_at"] = pd.to_datetime(df_testcases["created_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")

        # 添加操作列
        df_testcases["操作"] = ["删除" for _ in range(len(df_testcases))]

        # 显示表格
        edited_df = st.data_editor(
            df_testcases,
            column_config={
                "id": st.column_config.TextColumn("ID", width="small"),
                "name": st.column_config.TextColumn("名称", width="medium"),
                "type": st.column_config.TextColumn("类型", width="small"),
                "created_at": st.column_config.TextColumn("创建时间", width="medium"),
                "操作": st.column_config.ButtonColumn(
                    "操作",
                    help="点击执行操作",
                    width="small"
                )
            },
            use_container_width=True,
            hide_index=True,
            disabled=["id", "name", "type", "created_at"]
        )

        # 处理按钮点击
        for i, row in edited_df.iterrows():
            if row["操作"] == "删除":
                if st.button(f"确认删除 {row['name']}", key=f"confirm_delete_tc_{row['id']}"):
                    if delete_item("testcases", row["id"]):
                        st.experimental_rerun()
    else:
        st.info("暂无测试用例")

    # 测试用例类型统计
    if testcases:
        st.subheader("测试用例类型统计")
        type_counts = df_testcases["type"].value_counts().reset_index()
        type_counts.columns = ["类型", "数量"]

        fig = px.pie(
            type_counts,
            values="数量",
            names="类型",
            title="测试用例类型分布",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

# 2. 任务管理
with tabs[1]:
    st.header("任务管理")

    # 创建测试任务
    with st.expander("创建测试任务", expanded=True):
        with st.form("create_task_form"):
            task_name = st.text_input("任务名称", help="输入任务的名称，不超过50个字符")

            # 获取测试用例列表供选择
            testcases = fetch_data("testcases")
            if not testcases:
                st.warning("没有可用的测试用例，请先上传测试用例")
                testcase_options = []
                testcase_ids = []
            else:
                testcase_options = [f"{tc['name']} ({tc['type']})" for tc in testcases]
                testcase_ids = [tc["id"] for tc in testcases]

            selected_testcases = st.multiselect(
                "选择测试用例",
                options=testcase_options,
                help="可以选择多个测试用例"
            )

            selected_ids = []
            if selected_testcases:
                selected_ids = [testcase_ids[testcase_options.index(tc)] for tc in selected_testcases]

            schedule_type = st.selectbox(
                "调度类型",
                ["立即执行", "定时执行"],
                help="选择任务的执行方式"
            )

            schedule_time = None
            if schedule_type == "定时执行":
                col1, col2 = st.columns(2)
                with col1:
                    schedule_date = st.date_input("选择日期")
                with col2:
                    schedule_time_input = st.time_input("选择时间")
                schedule_time = datetime.combine(schedule_date, schedule_time_input).isoformat()

            col1, col2 = st.columns(2)
            with col1:
                submit_button = st.form_submit_button("创建任务", use_container_width=True)
            with col2:
                cancel_button = st.form_submit_button("取消", use_container_width=True)

            if submit_button:
                if not task_name:
                    st.error("请输入任务名称")
                elif len(task_name) > 50:
                    st.error("任务名称不能超过50个字符")
                elif not selected_testcases:
                    st.error("请选择至少一个测试用例")
                else:
                    try:
                        payload = {
                            "name": task_name,
                            "testcase_ids": selected_ids,
                            "schedule_type": schedule_type,
                            "schedule_time": schedule_time
                        }

                        response = requests.post(f"{API_BASE_URL}/tasks", json=payload)

                        if response.status_code == 200:
                            st.success("任务创建成功!")
                            st.session_state.refresh_data = True
                        else:
                            st.error(f"任务创建失败: {response.status_code} - {response.text}")
                    except Exception as e:
                        st.error(f"请求异常: {str(e)}")

    # 任务列表
    st.subheader("任务列表")

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

        # 添加操作列
        df_tasks["操作"] = ["删除" for _ in range(len(df_tasks))]

        # 显示表格
        edited_df = st.data_editor(
            df_tasks,
            column_config={
                "id": st.column_config.TextColumn("ID", width="small"),
                "name": st.column_config.TextColumn("名称", width="medium"),
                "status": st.column_config.TextColumn(
                    "状态",
                    width="small",
                    help="任务当前的执行状态"
                ),
                "created_at": st.column_config.TextColumn("创建时间", width="medium"),
                "schedule_type": st.column_config.TextColumn("调度类型", width="small"),
                "schedule_time": st.column_config.TextColumn("调度时间", width="medium"),
                "操作": st.column_config.ButtonColumn(
                    "操作",
                    help="点击执行操作",
                    width="small"
                )
            },
            use_container_width=True,
            hide_index=True,
            disabled=["id", "name", "status", "created_at", "schedule_type", "schedule_time"]
        )

        # 处理按钮点击
        for i, row in edited_df.iterrows():
            if row["操作"] == "删除":
                if st.button(f"确认删除 {row['name']}", key=f"confirm_delete_task_{row['id']}"):
                    if delete_item("tasks", row["id"]):
                        st.experimental_rerun()

        # 任务状态统计
        st.subheader("任务状态统计")
        status_counts = df_tasks["status"].value_counts().reset_index()
        status_counts.columns = ["状态", "数量"]

        fig = px.bar(
            status_counts,
            x="状态",
            y="数量",
            title="任务状态分布",
            color="状态",
            color_discrete_map={
                "成功": "green",
                "失败": "red",
                "运行中": "blue",
                "等待中": "orange",
                "已取消": "gray"
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无任务")

# 3. 测试报告查看
with tabs[2]:
    st.header("测试报告查看")

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
        df_reports["通过率"] = df_reports["通过率"].apply(lambda x: f"{x}%")

        # 添加操作列
        df_reports["操作"] = ["下载" for _ in range(len(df_reports))]

        # 显示表格
        edited_df = st.data_editor(
            df_reports,
            column_config={
                "id": st.column_config.TextColumn("ID", width="small"),
                "task_id": st.column_config.TextColumn("任务ID", width="small"),
                "task_name": st.column_config.TextColumn("任务名称", width="medium"),
                "total_cases": st.column_config.NumberColumn("总用例数", width="small"),
                "passed": st.column_config.NumberColumn("通过数", width="small"),
                "failed": st.column_config.NumberColumn("失败数", width="small"),
                "通过率": st.column_config.TextColumn("通过率", width="small"),
                "created_at": st.column_config.TextColumn("创建时间", width="medium"),
                "操作": st.column_config.ButtonColumn(
                    "操作",
                    help="点击执行操作",
                    width="small"
                )
            },
            use_container_width=True,
            hide_index=True,
            disabled=["id", "task_id", "task_name", "total_cases", "passed", "failed", "通过率", "created_at"]
        )

        # 处理按钮点击
        for i, row in edited_df.iterrows():
            if row["操作"] == "下载":
                st.session_state.download_report_id = row["id"]

        # 处理下载
        if st.session_state.download_report_id:
            report_id = st.session_state.download_report_id
            report_content = download_file("reports", report_id, f"report_{report_id}.html")
            if report_content:
                st.download_button(
                    label="点击下载报告",
                    data=report_content,
                    file_name=f"report_{report_id}.html",
                    mime="text/html",
                    key=f"download_report_{report_id}"
                )
                # 重置下载ID
                if st.button("取消下载"):
                    st.session_state.download_report_id = None
                    st.experimental_rerun()

        # 显示测试结果图表
        st.subheader("测试结果统计")

        # 准备图表数据
        chart_data = df_reports[["task_name", "passed", "failed", "total_cases"]].copy()
        chart_data["通过率"] = (chart_data["passed"] / chart_data["total_cases"] * 100).round(2)

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
    else:
        st.info("暂无测试报告")

# 4. 任务历史记录
with tabs[3]:
    st.header("任务历史记录")

    # 获取历史数据
    history = fetch_data("history")

    if history:
        # 转换为DataFrame
        df_history = pd.DataFrame(history)

        # 格式化时间
        if "start_time" in df_history.columns:
            df_history["start_time"] = pd.to_datetime(df_history["start_time"]).dt.strftime("%Y-%m-%d %H:%M:%S")

        if "end_time" in df_history.columns:
            df_history["end_time"] = df_history["end_time"].apply(
                lambda x: pd.to_datetime(x).strftime("%Y-%m-%d %H:%M:%S") if x else "未完成"
            )

        # 格式化持续时间
        if "duration" in df_history.columns:
            df_history["duration"] = df_history["duration"].apply(format_duration)

        # 显示表格
        st.dataframe(
            df_history,
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

        # 选择任务查看详情
        selected_task_id = st.selectbox(
            "选择任务查看详情",
            options=df_history["task_id"].unique(),
            format_func=lambda x: f"任务 {x} - {df_history[df_history['task_id'] == x]['task_name'].values[0]}"
        )

        if selected_task_id:
            # 获取任务详情
            task_details = fetch_data(f"history/{selected_task_id}")

            if task_details:
                st.subheader("任务执行详情")

                # 基本信息
                status = task_details.get("status", "未知")
                status_color = get_status_color(status)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("任务名称", task_details.get("task_name", "未知"))
                with col2:
                    st.markdown(f"<h3 style='color: {status_color}'>状态: {status}</h3>", unsafe_allow_html=True)
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

                # 测试用例执行详情
                st.subheader("测试用例执行详情")

                if "testcases" in task_details and task_details["testcases"]:
                    df_testcase_details = pd.DataFrame(task_details["testcases"])

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
                        df_testcase_details["duration"] = df_testcase_details["duration"].apply(format_duration)

                    st.dataframe(
                        df_testcase_details,
                        column_config={
                            "id": st.column_config.TextColumn("ID", width="small"),
                            "name": st.column_config.TextColumn("名称", width="medium"),
                            "status": st.column_config.TextColumn("状态", width="small"),
                            "start_time": st.column_config.TextColumn("开始时间", width="medium"),
                            "end_time": st.column_config.TextColumn("结束时间", width="medium"),
                            "duration": st.column_config.TextColumn("持续时间", width="medium")
                        },
                        use_container_width=True,
                        hide_index=True
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
                            "成功": "green",
                            "失败": "red",
                            "运行中": "blue",
                            "等待中": "orange",
                            "已取消": "gray"
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
            else:
                st.info("暂无任务详情")
    else:
        st.info("暂无任务历史记录")

# 如果需要刷新数据，重新加载页面
if st.session_state.refresh_data:
    st.session_state.refresh_data = False
    st.experimental_rerun()
