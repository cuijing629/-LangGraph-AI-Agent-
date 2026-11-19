import httpx
import streamlit as st

API = "http://127.0.0.1:8000"
st.set_page_config(page_title="智能任务助手", page_icon="🗂️")
st.title("智能任务助手")


def request(method, path, **kwargs):
    try:
        response = httpx.request(method, API + path, timeout=120, **kwargs)
        if response.is_success:
            return response.json()
        st.error(str(response.json().get("detail", f"HTTP {response.status_code}")))
    except (httpx.HTTPError, ValueError):
        st.error("无法读取后端响应，请检查 FastAPI 终端。")
    return None


def open_session(result):
    st.query_params["session"] = result["session_id"]
    st.rerun()


session = st.query_params.get("session")
with st.sidebar:
    if st.button("新建会话"):
        st.query_params.clear()
        st.rerun()
    value = st.text_input("会话 ID", value=session or "")
    if st.button("恢复会话") and value.strip():
        result = request("GET", "/api/agent/history/" + value.strip())
        if result:
            open_session(result)
    health = request("GET", "/health")
    if health:
        st.caption(f"模型：{health['mode']}")
        st.caption("知识库已连接" if health["rag_reachable"] else "知识库未连接")
    st.subheader("任务列表")
    tasks = request("GET", "/api/tasks")
    if tasks:
        for task in tasks["tasks"]:
            st.text(f"#{task['id']} {task['title']} · {task['status']}")

view = request("GET", f"/api/agent/history/{session}") if session else None
if view:
    for message in view["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["text"])
    if view["trace"]:
        with st.expander("本轮工具轨迹", expanded=True):
            st.dataframe(view["trace"], hide_index=True, use_container_width=True)
    if view["status"] == "running" and st.button("恢复执行"):
        result = request("POST", f"/api/agent/recover/{session}")
        if result:
            open_session(result)
    if approval := view["approval"]:
        st.subheader("待审批操作")
        st.write(approval["tool_name"])
        st.json(approval["arguments"])
        yes, no = st.columns(2)
        approved = yes.button("确认执行", type="primary")
        denied = no.button("拒绝执行")
        if approved or denied:
            result = request("POST", "/api/agent/confirm", json={
                "session_id": session, "approval_id": approval["approval_id"], "approved": approved
            })
            if result:
                open_session(result)

if message := st.chat_input("输入任务", disabled=bool(view and view["status"] != "completed")):
    with st.spinner("正在执行…"):
        result = request("POST", "/api/agent/chat", json={"session_id": session, "message": message})
    if result:
        open_session(result)
