import streamlit as st
import pandas as pd
import openai
import os
from io import BytesIO

# --- Streamlit Page Setup ---
st.set_page_config(page_title="AI Intro Generator", layout="centered")

st.title("🎯 Executive Intro Generator")
st.markdown("Upload a CSV with executive data and generate short, personalized intros for outreach emails.")

# --- OpenAI API Key ---
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

# --- Event Topics Input ---
st.markdown("### 🧠 Event Topics")
topics = st.text_area("Enter 3–5 event topics (comma-separated)", "IT Management, Endpoint Management, Security, Automation, Cloud Strategy")
is_aws_event = st.toggle("Is this an AWS-hosted event?")

# --- Prompt Generator ---
def generate_prompt(first_name, last_name, job_title, company_name, company_description, topics, is_aws):
    return f"""You are a helpful assistant writing short, factual, personalized intros for cold email invitations to executives.

Here is the information available:

First Name: {first_name}
Last Name: {last_name}
Job Title: {job_title}
Company: {company_name}
Company Description: {company_description}

The intro should be 1–2 professional sentences, broken into 2 short paragraphs for readability.

Do not mention the person’s name. Do not include any invented information. Use the company description only to help understand their role and context — don’t reference the company in the message.

Reference only 1 or 2 of the following event topics if relevant: {topics}

{'AWS would like to invite you to join...' if is_aws else 'We are inviting you to join...'}

Use a warm, professional tone. Here's an example of the format and tone:

\"I hope this message finds you well. As a leader in cybersecurity and IT operations at Grupo AG, your expertise in overseeing complex and innovative IT environments aligns perfectly with the themes of our upcoming executive event, focusing on IT and Endpoint Management.\"

Now write the intro:"""

# --- Intro Generator ---
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
            temperature=0.7,
            max_tokens=100
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# --- Generate Intros ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    required_columns = ["First Name", "Last Name", "Job Title", "Company Name", "Company Description"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
    else:
        if st.button("🚀 Generate Intros"):
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
