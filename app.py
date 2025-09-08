import streamlit as st
import pandas as pd
import openai
import os
from io import BytesIO

# --- Streamlit Page Setup ---
st.set_page_config(page_title="AI Intro Generator", layout="centered")

st.title("🎯 Executive Intro Generator")
st.markdown("Upload a CSV file with these columns: **First Name**, **Last Name**, **Company**, **Email**, **Title**, and **Professional Background**.\n\nWe'll generate a short personalized intro for each person to help you run high-impact outreach.")

# --- Set your OpenAI API Key (via Secrets or Env Variable) ---
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

# --- Prompt Generator ---
def generate_prompt(row):
    return f"""
You are writing a short cold outreach intro for an email.

Here is the recipient's info:
- Name: {row.get('First Name', '')} {row.get('Last Name', '')}
- Job Title: {row.get('Title', '')}
- Company: {row.get('Company', '')}
- Email: {row.get('Email', '')}
- Background: {row.get('Professional Background', '')}

Write a 1–2 sentence personalized intro to invite them to a private executive event with other {row.get('Title', '').split()[0] if row.get('Title') else 'executives'}. 
Mention something from their background that would make them a good fit. Be friendly and insightful.
Don't include greetings like 'Hi' or 'Dear'.
"""

# --- Generate Intros ---
def generate_intro(row):
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who writes short intros for cold outreach emails."},
                {"role": "user", "content": generate_prompt(row)}
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

    required_cols = ["First Name", "Last Name", "Company", "Email", "Title", "Professional Background"]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"❌ Missing columns: {', '.join(missing_cols)}")
    else:
        st.info("Generating intros... This may take a moment ⏳")

        df["Personalised Intro"] = df.apply(generate_intro, axis=1)

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
