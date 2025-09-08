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
def generate_prompt(row, event_topics, is_aws):
    name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
    company = row.get('Company', '')
    title = row.get('Title', '')
    background = row.get('Professional Background', '')

    intro_context = (
        f"AWS would like to invite you to join a select group of executives."
        if is_aws else
        f"We'd love to invite you to connect with a group of senior peers."
    )

    return f"""You are a helpful assistant helping write short intros for cold emails to executives.

Here is the contact's background:
- Name: {name}
- Title: {title}
- Company: {company}
- Background: {background}

They are being invited to an exclusive executive event. The themes of the event include: {event_topics}.

Write a short, personalized cold email intro in 2 short paragraphs (2 lines max total). Start with something relevant to their role or background, then use the second line to invite them. Pick one or two event themes that are most relevant to their work — don't list them all.

Use a warm, professional tone. Avoid greetings like 'Hi' or 'Dear'. Do not mention the format of the event (e.g. dinner, roundtable). Here's the context to include in the second sentence: {intro_context}.
"""

def generate_intro(row, event_topics, is_aws):
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who writes short intros for cold outreach emails."},
                {"role": "user", "content": generate_prompt(row, event_topics, is_aws)}
            ],
            temperature=0.7,
            max_tokens=120,
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

        is_aws_event = st.toggle("This is an AWS-led event")

        if event_topics:
            if st.button("🚀 Generate Intros"):
                st.info("Generating intros... This may take a moment ⏳")

                df["Personalised Intro"] = df.apply(lambda row: generate_intro(row, event_topics, is_aws_event), axis=1)

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

