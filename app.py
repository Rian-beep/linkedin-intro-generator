import streamlit as st
import pandas as pd
import openai
import os
from io import BytesIO

# --- Streamlit Page Setup ---
st.set_page_config(page_title="AI Intro Generator", layout="centered")

st.title("🎯 Executive Intro Generator")
st.markdown("Upload a CSV with fields like **First Name**, **Last Name**, **Job Title**, **Company**, and **Company Description**. This tool will generate a short, professional intro for each contact to use in email outreach.")

# --- Set your OpenAI API Key ---
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# --- File Upload and Topics Input ---
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
event_topics = st.text_area("🔍 Event Topics (1 per line, max 5)", placeholder="Example: IT Management\nEndpoint Security\nCloud Strategy")
is_aws_event = st.toggle("Is this an AWS Event?", value=False)

def generate_prompt(first_name, last_name, title, company, company_desc, topics, is_aws):
    topic_list = [t.strip() for t in topics.splitlines() if t.strip()][:5]
    topic_text = ", ".join(topic_list)
    invitation = (
        "AWS would like to invite you to join a select group of peers"
        if is_aws else
        "We’re inviting you to a private executive event"
    )

    return f"""
You are a helpful assistant writing short, professional email intros for executive outreach. 
Each intro must follow this strict format:

- Two short, clear sentences.
- Do **not** mention the person’s name.
- Do **not** use greetings like “Hi” or “Dear”.
- The first sentence should start: “I hope this message finds you well.”
- The second sentence should reference their job title, company, and company description, rewritten into a clear and accurate English sentence (even if the original was messy or in another language).
- Only mention 1–2 relevant topics from this list that match their role: {topic_text}.
- The tone must be professional, warm, and factually accurate.
- Do **not** make up or assume anything not in the input.

Here is the input:
Job Title: {title}
Company: {company}
Company Description: {company_desc}

Write the intro in English:
"""

def generate_intro(row):
    try:
        prompt = generate_prompt(
            row.get("First Name", ""),
            row.get("Last Name", ""),
            row.get("Job Title", ""),
            row.get("Company Name", ""),
            row.get("Company Description", ""),
            event_topics,
            is_aws_event
        )
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who writes short intros for cold outreach emails."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# --- Main Logic ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    required_cols = ["First Name", "Last Name", "Job Title", "Company Name", "Company Description"]
    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ Missing one or more required columns: {', '.join(required_cols)}")
    elif not event_topics.strip():
        st.warning("⚠️ Please enter 1–5 event topics to generate relevant intros.")
    else:
        if st.button("✨ Generate Intros"):
            st.info("Generating intros... This may take a moment ⏳")
            df["Personalised Intro"] = df.apply(generate_intro, axis=1)

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

