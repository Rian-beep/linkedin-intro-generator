import streamlit as st
import pandas as pd
import openai
import os
from io import BytesIO

# --- Streamlit Page Setup ---
st.set_page_config(page_title="AI Intro Generator", layout="centered")

st.title("🎯 Executive Intro Generator")
st.markdown("Upload a CSV with relevant contact info and get a personalized intro for each person.")

# --- API Key Setup ---
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

# --- Event Topics + Toggle ---
st.markdown("### 📝 Event Customization")
topics = st.text_area("Enter key topics for the event (comma separated)",
                      placeholder="cloud security, AI in operations, cost optimization")
is_aws_event = st.toggle("Is this an AWS-hosted event?", value=False)

generate_button = st.button("✨ Generate Intros")

# --- Prompt Builder ---
def build_prompt(row, topics, is_aws):
    name = f"{row['First Name']} {row['Last Name']}"
    title = row.get("Job Title", "").strip()
    company = row.get("Company Name", "").strip()
    description = row.get("Company Description", "").strip()

    topic_list = [t.strip() for t in topics.split(",") if t.strip()]
    topic_snippet = ""
    if topic_list:
        chosen = topic_list[:2]
        topic_snippet = f"focusing on {', '.join(chosen)}"

    opening_line = "I hope this message finds you well."

    if is_aws:
        second_line = (
            f"As a {title.lower()} at {company}, your work in {description.lower()} caught AWS's attention. "
            f"They’d love for you to join a select group of leaders for a private event {topic_snippet}."
        )
    else:
        second_line = (
            f"As a {title.lower()} at {company}, your work in {description.lower()} aligns perfectly with the themes of our upcoming executive event {topic_snippet}."
        )

    return f"{opening_line}\n\n{second_line}".strip()

# --- OpenAI Call ---
def generate_intro_from_prompt(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You write short, 2-sentence cold email intros for executives."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# --- Main ---
if uploaded_file and generate_button:
    df = pd.read_csv(uploaded_file)

    required_cols = ["First Name", "Last Name", "Company Name", "Job Title", "Company Description"]
    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ The CSV must include the following columns: {', '.join(required_cols)}")
    else:
        st.info("Generating personalized intros... ⏳")
        df["Personalised Intro"] = df.apply(lambda row: build_prompt(row, topics, is_aws_event), axis=1)

        st.success("✅ Done! Preview below and download your file.")
        st.dataframe(df.head(10))

        output = BytesIO()
        df.to_csv(output, index=False)
        st.download_button(
            label="📥 Download CSV with Intros",
            data=output.getvalue(),
            file_name="executive_intros.csv",
            mime="text/csv"
        )
