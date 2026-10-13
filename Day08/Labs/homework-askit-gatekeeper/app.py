import streamlit as st

from gatekeeper import needs_approval, route, safe_to_remember

st.set_page_config(page_title="AskIT Gatekeeper", page_icon="🛡️")
st.title("AskIT Gatekeeper")
st.caption("Safety checks for routing, approvals, and memory retention.")

text_input = st.text_area(
    "Ticket or fact text",
    placeholder="Type a ticket message or fact to evaluate...",
    height=180,
)

route_col, approval_col, remember_col = st.columns(3)

with route_col:
    if st.button("Route team"):
        try:
            result = route(text_input)
            st.success(f"Route result: {result}")
        except ValueError as exc:
            st.error(str(exc))

with approval_col:
    if st.button("Check approval"):
        action = st.selectbox(
            "Action",
            ["search_kb", "get_ticket", "reset_password", "update_ticket", "grant_access"],
            index=2,
            key="approval_action",
        )
        user_id = st.text_input("User ID", value="EMP-1002", key="approval_user")
        hour = st.number_input("Hour", min_value=0, max_value=23, value=10, key="approval_hour")

        try:
            result = needs_approval(action, user_id, int(hour))
            st.success(f"Approval result: {result}")
        except ValueError as exc:
            st.error(str(exc))

with remember_col:
    if st.button("Check memory safety"):
        try:
            result = safe_to_remember(text_input)
            if result:
                st.success("Safe to remember: True")
            else:
                st.warning("Safe to remember: False")
        except ValueError as exc:
            st.error(str(exc))
