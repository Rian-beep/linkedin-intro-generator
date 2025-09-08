import streamlit as st
import pandas as pd
import openai
import os
from io import BytesIO

# --- Streamlit Page Setup ---
st.set_page_config(page_title="AI Intro Generator", layout="centered")
st.title("🎯 Executive Intro Generator")
st.markdown("Upload a CSV with executive contact details and generate personalized cold email intros tailored to your event.")

# --- Set your OpenAI API Key ---
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# --- Prompt Template ---
def generate_prompt(row, event_topics):
    return f"""You are a helpful assistant helping write short intros for cold emails to executives.

Here is the contact's background:
- First Name: {row.get('First Name', '')}
- Last Name: {row.get('Last Name', '')}
- Title: {row.get('Title', '')}
- Company: {row.get('Company', '')}
- Email: {row.get('Email', '')}
- Background: {row.get('Professional Background', '')}

They are being invited to a private executive roundtable event. The topics of the event include: {event_topics}.

Write a short 1–2 sentence personalized introduction for why we're reaching out. Mention something relevant from their background or role and tie it into the event themes.

Use a warm, professional tone. Do not include greetings like 'Hi' or 'Dear'—just the intro paragraph.
"""

def generate_intro(row, event_topics):
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who writes short intros for cold outreach emails."},
                {"role": "user", "content": generate_prompt(row, event_topics)}
            ],
            temperature=0.7,
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# --- Upload CSV ---
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    required_columns = ['First Name', 'Last Name', 'Company', 'Email', 'Title', 'Professional Background']
    if not all(col in df.columns for col in required_columns):
        st.error(f"❌ Your CSV must contain these columns: {', '.join(required_columns)}")
    else:
        st.markdown("### ✍️ Event Topics")
        event_topics = st.text_area("List the topics of your event", placeholder="e.g. AI in sales, revenue operations, driving pipeline efficiency...")

        if event_topics:
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

