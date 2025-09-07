import streamlit as st
import pandas as pd
import openai
import io

# --- Set up your OpenAI API key ---
openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- UI Layout ---
st.set_page_config(page_title="Intro Generator", layout="centered")
st.title("🧠 LinkedIn Personalised Intro Generator")
st.write("Upload a CSV with a 'Personal Linkedin URL' column. The tool will generate short, personalized intros to use in outreach.")

# --- Upload CSV ---
uploaded_file = st.file_uploader("Upload your contact list", type=["csv"])

# --- Generate intro for a single row ---
def generate_intro(linkedin_url):
    prompt = f"""
You are helping a B2B event organiser write short, personalized email intros to executives. 
You're provided with the LinkedIn URL: {linkedin_url}

Write a short, professional and personalized intro (1–2 sentences max) that mentions something about their background, experience, or company. This intro will be used as the opening line in an email inviting them to a private executive event relevant to their field.
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# --- Generate intros and allow download ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if "Personal Linkedin URL" not in df.columns:
        st.error("❌ The uploaded file must contain a column called 'Personal Linkedin URL'")
    else:
        if st.button("🔍 Generate Intros"):
            with st.spinner("Generating intros..."):
                df["Personalised Intro"] = df["Personal Linkedin URL"].apply(generate_intro)

            st.success("✅ Intros generated!")
            st.dataframe(df.head(10))

            # Download
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 Download CSV with Intros",
                data=csv,
                file_name="contacts_with_intros.csv",
                mime="text/csv",
            )

