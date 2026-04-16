import streamlit as st
from groq import Groq
import json
import os
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SENDER_EMAIL = "r15908325@gmail.com"
APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECEIVER_EMAIL = "r15908325@gmail.com"

with open("runbook.json", "r") as f:
    runbook = json.load(f)

runbook_text = "\n".join([
    f"Issue: {item['issue']}\nSteps: {item['steps']}"
    for item in runbook["issues"]
])

def generate_ticket_id():
    return "DESK-" + "".join(random.choices(string.digits, k=5))

def send_email(ticket_id, issue, l1_response, l2_response):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = f"[DeskAI] Developer Escalation - {ticket_id}"
    body = f"""
DeskAI Escalation Report
========================
Ticket ID: {ticket_id}

Issue Reported:
{issue}

L1 Agent Response:
{l1_response}

L2 Agent Response:
{l2_response}

Action Required:
This issue could not be resolved by L1 or L2. Please investigate and resolve.
    """
    msg.attach(MIMEText(body, "plain"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

def l1_agent(issue):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": f"""You are an L1 IT support agent. 
You have access to the following runbook:

{runbook_text}

Try to resolve the user's issue using the runbook.
If you can resolve it, start your response with RESOLVED: and provide the steps.
If you cannot resolve it with the runbook, start your response with ESCALATE: and briefly explain why."""
            },
            {"role": "user", "content": issue}
        ]
    )
    return response.choices[0].message.content

def l2_agent(issue, l1_response):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are an L2 IT support specialist with deep technical knowledge.
L1 could not resolve this issue.
Perform a deeper diagnosis and provide advanced troubleshooting steps.
If you can resolve it, start your response with RESOLVED: and provide detailed steps.
If this needs a developer, start your response with ESCALATE_DEV: and explain what needs to be fixed."""
            },
            {"role": "user", "content": f"Original issue: {issue}\n\nL1 attempted: {l1_response}"}
        ]
    )
    return response.choices[0].message.content

st.set_page_config(page_title="DeskAI", page_icon="🤖", layout="centered")
st.title("🤖 DeskAI - IT Support")
st.caption("Intelligent L1/L2 support powered by AI")

if "ticket_log" not in st.session_state:
    st.session_state.ticket_log = []

issue = st.text_area("Describe your IT issue:", placeholder="e.g. My VPN is not connecting...")

if st.button("Submit Ticket"):
    if issue.strip() == "":
        st.warning("Please describe your issue first.")
    else:
        ticket_id = generate_ticket_id()
        st.caption(f"Ticket ID: {ticket_id}")

        with st.spinner("L1 Agent is analysing your issue..."):
            l1_response = l1_agent(issue)

        st.write("**L1 Response:**")
        st.write(l1_response)

        if "RESOLVED" in l1_response.upper():
            st.success("L1 Resolved")
            st.session_state.ticket_log.append({
                "ticket_id": ticket_id,
                "issue": issue,
                "resolved_by": "L1",
                "resolution": l1_response
            })

        elif "ESCALATE" in l1_response.upper():
            st.warning("L1 could not resolve. Escalating to L2...")

            with st.spinner("L2 Agent is diagnosing..."):
                l2_response = l2_agent(issue, l1_response)

            st.write("**L2 Response:**")
            st.write(l2_response)

            if "RESOLVED" in l2_response.upper():
                st.success("L2 Resolved")
                st.session_state.ticket_log.append({
                    "ticket_id": ticket_id,
                    "issue": issue,
                    "resolved_by": "L2",
                    "resolution": l2_response
                })

            elif "ESCALATE_DEV" in l2_response.upper():
                st.error("Needs Developer. Raising escalation email...")

                try:
                    send_email(ticket_id, issue, l1_response, l2_response)
                    st.success(f"Escalation email sent. Ticket ID: {ticket_id}")
                except Exception as e:
                    st.error(f"Email failed: {str(e)}")

                st.session_state.ticket_log.append({
                    "ticket_id": ticket_id,
                    "issue": issue,
                    "resolved_by": "Developer Required",
                    "resolution": l2_response
                })

if st.session_state.ticket_log:
    st.divider()
    st.subheader("Ticket Log")
    for i, ticket in enumerate(st.session_state.ticket_log):
        with st.expander(f"{ticket['ticket_id']} - {ticket['resolved_by']}"):
            st.write(f"**Issue:** {ticket['issue']}")
            st.write(f"**Resolution:** {ticket['resolution']}")