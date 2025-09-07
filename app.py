import streamlit as st
import pandas as pd
import openai
import requests
import time

# --- Streamlit App Config ---
st.set_page_config(page_title="LinkedIn Intro Generator", layout="centered")
st.title("🧠 LinkedIn Intro Generator")
st.markdown("Upload a CSV with a column named **'Personal Linkedin URL'**. This tool will generate a short personalized intro for each person.")

# --- Set OpenAI API Key ---
openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- Upload CSV ---
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if 'Personal Linkedin URL' not in df.columns:
        st.error("❌ Your file must contain a column named 'Personal Linkedin URL'.")
    else:
        intros = []
        with st.spinner("Generating intros..."):
            for url in df['Personal Linkedin URL']:
                if pd.isna(url) or not str(url).startswith("http"):
                    intros.append("No valid LinkedIn URL provided.")
                    continue

                prompt = f"Write a short 1–2 sentence personalized intro to this person based on their LinkedIn profile: {url}"

                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are an expert at summarizing professional profiles in a concise and friendly way."},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.7,
                        max_tokens=100,
                    )
                    intro = response.choices[0].message.content.strip()
                except Exception as e:
                    intro = f"Error: {str(e)}"

                intros.append(intro)
                time.sleep(1.2)  # Optional delay to avoid hitting rate limits

        df['Personalised Intro'] = intros

        st.success("✅ Intros generated!")
        st.dataframe(df.head())

        st.download_button(
            label="📥 Download with Intros",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name="linkedin_intros.csv",
            mime="text/csv"
        )
