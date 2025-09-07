import streamlit as st
import pandas as pd
import openai
import os
from io import BytesIO

# --- Streamlit Page Setup ---
st.set_page_config(page_title="AI Intro Generator", layout="centered")

st.title("🎯 Executive Intro Generator")
st.markdown("Upload a CSV file with a column called **Personal Linkedin URL** and get a personalized intro for each person based on their LinkedIn profile.")

# --- Set your OpenAI API Key (replace or use env variable) ---
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

# --- Prompt Template ---
def generate_prompt(linkedin_url):
    return f"""You are a helpful assistant helping write cold email intros to executives based on their LinkedIn profile.

Go to this LinkedIn profile: {linkedin_url}

Write a short 1–2 sentence personalized introduction for why we’re reaching out to them. Mention something specific from their background or role. We are inviting them to a private executive event with peers to share insights and challenges they’re facing.

Use a warm, professional tone. Do not include greetings like 'Hi' or 'Dear'—just the intro paragraph."""

# --- Generate Intros ---
def generate_intro(linkedin_url):
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who writes short intros for cold outreach emails."},
                {"role": "user", "content": generate_prompt(linkedin_url)}
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

    if "Personal Linkedin URL" not in df.columns:
        st.error("❌ The column 'Personal Linkedin URL' was not found in the uploaded CSV.")
    else:
        st.info("Generating intros... This may take a moment ⏳")

        df["Personalised Intro"] = df["Personal Linkedin URL"].apply(generate_intro)

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
