import streamlit as st
import pandas as pd
import openai
import os
from io import BytesIO

# --- Streamlit Page Setup ---
st.set_page_config(page_title="AI Intro Generator", layout="centered")

st.title("🎯 Executive Intro Generator")
st.markdown("Upload a CSV file with columns like **First Name, Last Name, Company Name, Job Title, Company Description** to generate a short, personalized intro for each person.")

# --- Set your OpenAI API Key (replace or use env variable) ---
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# --- Event Context Input ---
st.markdown("### 🎯 Event Context")
event_topics = st.text_area("List the key topics of the event (comma-separated):", placeholder="e.g. IT, Endpoint Management, Cybersecurity")
is_aws_event = st.toggle("Is this an AWS-sponsored event?", value=False)

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

# --- Prompt Generator ---
def generate_prompt(row, topics, aws_event):
    job_title = row.get("Job Title", "")
    company = row.get("Company Name", "")
    description = row.get("Company Description", "")
    topic_list = [t.strip() for t in topics.split(",") if t.strip()]
    selected_topics = ", ".join(topic_list[:2]) if topic_list else "key industry challenges"

    if aws_event:
        return f"""
I hope this message finds you well.
AWS would like to invite you to a private executive event. Your role in {job_title} at {company}, particularly your work in {description}, aligns strongly with our focus on {selected_topics}.
"""
    else:
        return f"""
I hope this message finds you well.
As a leader in {job_title} at {company}, your work in {description} aligns perfectly with the themes of our upcoming executive event, particularly around {selected_topics}.
"""

# --- Generate Intro Using OpenAI ---
def generate_intro(row, topics, aws_event):
    try:
        prompt = generate_prompt(row, topics, aws_event)
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who writes short, professional cold outreach intros."},
                {"role": "user", "content": prompt.strip()}
            ],
            temperature=0.7,
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# --- Main Logic ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    required_cols = ["Job Title", "Company Name", "Company Description"]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
    else:
        if not event_topics.strip():
            st.warning("✏️ Please enter some event topics before generating intros.")
        else:
            if st.button("🚀 Generate Personalised Intros"):
                st.info("Generating intros... This may take a moment ⏳")
                df["Personalised Intro"] = df.apply(lambda row: generate_intro(row, event_topics, is_aws_event), axis=1)

                st.success("✅ Done! Download your enriched CSV below.")

                # Display preview
                st.dataframe(df.head(10))

                # Download button
                output = BytesIO()
                df.to_csv(output, index=False)
                st.download_button(
                    label="📥 Download CSV with Intros",
                    data=output.getvalue(),
                    file_name="intros_with_personalisation.csv",
                    mime="text/csv"
                )
