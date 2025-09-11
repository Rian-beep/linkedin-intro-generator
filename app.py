import streamlit as st
import pandas as pd
import openai
import os
from io import BytesIO

# --- Streamlit Page Setup ---
st.set_page_config(page_title="AI Intro Generator", layout="centered")

st.title("🎯 Executive Intro Generator")
st.markdown("Upload a CSV with columns for **First Name**, **Last Name**, **Job Title**, **Company**, and **Company Description**.")

# --- Set your OpenAI API Key ---
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# --- Event Topics & Toggle ---
st.markdown("### 🎯 Event Topics")
event_topics = st.text_area("Add key topics for the event (comma-separated)")
is_aws_event = st.toggle("Is this an AWS Event?", value=False)

# --- File Upload ---
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

# --- Prompt Generator ---
def generate_prompt(row, topics):
    job = row.get("Job Title", "").strip()
    company = row.get("Company", "").strip()
    description = row.get("Company Description", "").strip()

    intro_context = (
        f"You are helping write a short intro paragraph for a cold email invite to a private executive event.\n"
        f"Write 1–2 short paragraphs introducing the event to someone who is a {job} at {company}.\n"
        f"Use something relevant from their company description: {description}\n"
        f"Only mention 1 or 2 of these topics if relevant: {topics}.\n"
    )

    if is_aws_event:
        intro_context += "Make it clear AWS is inviting them."
    else:
        intro_context += "Write it in the voice of a warm, curious peer extending a personal invite."

    return intro_context

# --- Generate Intro Function ---
def generate_intro(row, topics):
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You write short, thoughtful email intros for executive invites."},
                {"role": "user", "content": generate_prompt(row, topics)}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# --- Generate Intros ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    required_cols = ["First Name", "Last Name", "Job Title", "Company", "Company Description"]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
    else:
        if st.button("🚀 Generate Intros"):
            st.info("Generating intros... This may take a moment ⏳")
            df["Personalised Intro"] = df.apply(lambda row: generate_intro(row, event_topics), axis=1)

            st.success("✅ Done! Download your enriched CSV below.")
            st.dataframe(df.head(10))

            output = BytesIO()
            df.to_csv(output, index=False)
            st.download_button(
                label="📥 Download CSV with Intros",
                data=output.getvalue(),
                file_name="intros_with_personalisation.csv",
                mime="text/csv"
            )

