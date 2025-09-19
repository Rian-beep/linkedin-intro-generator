import streamlit as st
import pandas as pd
import openai
import os
import re
from io import BytesIO

# --- Streamlit Page Setup ---
st.set_page_config(page_title="AI Intro Generator", layout="centered")

st.title("🎯 Executive Intro Generator")
st.markdown("Upload a CSV file with columns like **First Name**, **Last Name**, **Job Title**, **Company Name**, and **Company Description** to generate personalized intros for outreach.")

# --- Set your OpenAI API Key ---
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# --- Topic Input and AWS Toggle ---
st.markdown("### 📌 Event Topics")
topics = st.text_area("Enter 3–5 key topics of the event (separated by commas)")
is_aws_event = st.toggle("Is this an AWS Event?", value=False)

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

# --- Prompt Template ---
def generate_prompt(first_name, last_name, title, company, description, topics, is_aws):
    topic_list = [t.strip() for t in topics.split(",") if t.strip()]
    selected_topics = ", ".join(topic_list[:2]) if topic_list else "enterprise innovation"

    role_segment = f"As a leader in {title.lower()} at {company}," if title and company else "In your role,"
    theme_segment = f"aligns perfectly with the themes of our upcoming executive event, focusing on {selected_topics}."

    if is_aws:
        return (
            f"I hope this message finds you well. {role_segment} your expertise aligns with AWS's mission to support executives "
            f"driving innovation and transformation across industries. AWS would like you to join a select group of peers for a private discussion {theme_segment}"
        )
    else:
        return (
            f"I hope this message finds you well. {role_segment} your expertise {theme_segment}"
        )

# --- Generate Intros ---
def generate_intro(row):
    try:
        prompt = generate_prompt(
            row.get("First Name", ""),
            row.get("Last Name", ""),
            row.get("Job Title", ""),
            row.get("Company Name", ""),
            row.get("Company Description", ""),
            topics,
            is_aws_event
        )

        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who writes short intros for cold outreach emails."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=150,
        )

        # Clean output
        content = response.choices[0].message.content.strip()
        content = re.sub(r'^[\"“”\']+|[\"“”\']+$', '', content)
        return content

    except Exception as e:
        return f"Error: {e}"

# --- Main Logic ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    required_cols = ["First Name", "Last Name", "Job Title", "Company Name", "Company Description"]
    missing = [col for col in required_cols if col not in df.columns]

    if missing:
        st.error(f"❌ Missing required columns: {', '.join(missing)}")
    elif not topics:
        st.warning("⚠️ Please enter event topics before generating intros.")
    else:
        st.info("Generating personalized intros... This may take a moment ⏳")

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
