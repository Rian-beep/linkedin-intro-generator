import streamlit as st
import pandas as pd
import openai
import os
from io import BytesIO

# --- Streamlit Page Setup ---
st.set_page_config(page_title="AI Intro Generator", layout="centered")

st.title("🎯 Executive Intro Generator")
st.markdown("Upload a CSV with the required fields and generate a short, personalized intro for each contact.")

# --- Set your OpenAI API Key ---
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# --- Event Configuration ---
st.markdown("### 📝 Event Topics")
event_topics = st.text_area("List the topics for your upcoming executive event (comma-separated)", "IT and Endpoint Management, Cybersecurity, Digital Transformation, Data Strategy, Cloud Infrastructure")
is_aws_event = st.toggle("Is this an AWS Event?", value=False)

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

# --- Prompt Template ---
def generate_prompt(job_title, company_name, company_description, topic):
    base_intro = "I hope this message finds you well."
    second_line = f"As a leader in {job_title.lower()} at {company_name}, your expertise in overseeing complex and innovative environments aligns perfectly with the themes of our upcoming executive event, focusing on {topic}."
    if is_aws_event:
        second_line = f"AWS would like to invite you to join a select group of executives. As a leader in {job_title.lower()} at {company_name}, your expertise in overseeing complex and innovative environments aligns perfectly with the themes of our upcoming executive event, focusing on {topic}."
    return f"{base_intro} {second_line}"

# --- Generate Intros ---
def generate_intro(row, topics):
    try:
        job_title = str(row.get("Job Title", ""))
        company_name = str(row.get("Company Name", ""))
        company_description = str(row.get("Company Description", ""))
        selected_topic = select_best_topic(job_title, topics)

        prompt = f"""
Write one sentence only. Follow this exact structure:

"I hope this message finds you well. As a leader in [function] at [Company], your expertise in [area of responsibility] aligns perfectly with the themes of our upcoming executive event, focusing on [topic]."

Use the following information to complete it:
- Job Title: {job_title}
- Company Name: {company_name}
- Company Description: {company_description}
- Topic of Event: {selected_topic}

Use a professional and warm tone.
Do not include a greeting like “Hi” or “Dear”.
Do not mention their name in the sentence.
Do not invent or exaggerate — keep the sentence factual.
Only choose one topic that best fits the person's role and expertise.
"""

        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes concise, relevant intros for executive outreach."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=120,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# --- Topic Selection Helper ---
def select_best_topic(job_title, topics):
    job_title = job_title.lower()
    for topic in topics:
        if topic.lower() in job_title:
            return topic
    return topics[0]  # fallback to first topic if no match

# --- Main Logic ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    required_columns = ["First Name", "Last Name", "Email", "Company Name", "Job Title", "Company Description"]
    if not all(col in df.columns for col in required_columns):
        st.error(f"❌ The uploaded CSV must contain the following columns: {', '.join(required_columns)}")
    else:
        st.info("Generating personalized intros... This may take a moment ⏳")
        topic_list = [t.strip() for t in event_topics.split(",") if t.strip()]

        df["Personalised Intro"] = df.apply(lambda row: generate_intro(row, topic_list), axis=1)

        st.success("✅ Done! Download your enriched CSV below.")

        # Preview table
        st.dataframe(df[["First Name", "Last Name", "Job Title", "Company Name", "Personalised Intro"]].head(10))

        # Download output
        output = BytesIO()
        df.to_csv(output, index=False)
        st.download_button(
            label="📥 Download CSV with Intros",
            data=output.getvalue(),
            file_name="intros_with_personalisation.csv",
            mime="text/csv"
        )
