import streamlit as st
import pandas as pd
import openai
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="LinkedIn Intro Generator")

st.title("🔗 LinkedIn Intro Generator")
st.write("Upload a CSV with `First Name`, `Last Name`, and `LinkedIn URL` to generate short personalized intros.")

# Upload CSV
uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if not all(col in df.columns for col in ['First Name', 'Last Name', 'LinkedIn URL']):
        st.error("CSV must contain 'First Name', 'Last Name', and 'LinkedIn URL' columns.")
    else:
        with st.spinner("Generating personalized intros..."):
            intros = []
            for _, row in df.iterrows():
                prompt = f"Write a short and friendly 1-2 sentence intro to {row['First Name']} {row['Last Name']}, based on their LinkedIn profile at {row['LinkedIn URL']}. Don't mention LinkedIn or that you're generating text."
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7
                    )
                    intro = response.choices[0].message.content.strip()
                except Exception as e:
                    intro = f"Error: {e}"
                intros.append(intro)

            df["Personalized Intro"] = intros
            st.success("✅ Done generating intros!")

            st.write(df.head())

            st.download_button(
                label="📥 Download CSV with Intros",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="with_personalized_intros.csv",
                mime="text/csv"
            )
