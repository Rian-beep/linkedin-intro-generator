import streamlit as st
import pandas as pd
import openai
import os
from io import BytesIO

# --- Streamlit Page Setup ---
st.set_page_config(page_title="AI Intro Generator", layout="centered")

st.title("🎯 Executive Intro Generator")
st.markdown("Upload a Cognism CSV file and generate a personalized intro for each contact based on job title, company name, and company description.")

# --- OpenAI API Key ---
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# --- Topic Entry and AWS Toggle ---
st.markdown("### ✍️ Event Topics")
topics_input = st.text_area("Enter 5 topics for the event (separate by commas)", placeholder="AI, Automation, CX, Revenue Growth, Cloud")
is_aws_event = st.toggle("Is this an AWS Event?", value=False)

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload Cognism CSV", type=["csv"])

# --- Prompt Template ---
def generate_prompt(first, last, company, title, company_desc, topics):
    topics_list = [t.strip() for t in topics.split(',') if t.strip()]
    selected_topics = ", ".join(topics_list[:2]) if topics_list else "key challenges"

    if is_aws_event:
        intro_line = f"AWS would like you to join a select group of peers."
    else:
        intro_line = f"We're reaching out to invite you to a private executive event."

    prompt = f"""
You are a helpful assistant who writes short, personalized intros for cold outreach emails.

Write a short two-line (two-paragraph) intro to invite {first} {last}, {title} at {company}, to an exclusive event.
Use this company description for context: "{company_desc}".
The event will cover topics such as {selected_topics}.
{intro_line}
Avoid greetings like 'Hi' or 'Dear'. Keep it warm and professional.
"""
    return prompt

# --- Generate Intros ---
def generate_intro(row):
    try:
        prompt = generate_prompt(
            row.get("First Name", ""),
            row.get("Last Name", ""),
            row.get("Company Name", ""),
            row.get("Job Title", ""),
            row.get("Company Description", ""),
            topics_input
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

    required_cols = ["First Name", "Last Name", "Company Name", "Job Title", "Company Description"]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"❌ Missing columns in CSV: {', '.join(missing_cols)}")
    else:
        if st.button("🚀 Generate Intros"):
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
