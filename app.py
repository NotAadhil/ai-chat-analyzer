import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from analyzer import analyze_chat, get_ai_summary

st.set_page_config(page_title="AI Chat Analyzer", page_icon="🕵️", layout="wide")

# Custom UI
st.title("🕵️ The AI Conversation Analyzer")
st.markdown("Upload a WhatsApp chat export and let the AI break down your conversation dynamics.")

with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Gemini API Key (Optional but recommended)", type="password", help="Needed to generate the savage AI summary.")
    if not api_key:
        st.warning("Without an API key, you won't get the AI-generated Roast/Summary.")
        
    st.divider()
    st.markdown("### How to Export:")
    st.markdown("1. Open a WhatsApp chat\n2. Click the 3 dots\n3. **Export chat** (without media)\n4. Upload the `.txt` here")
    uploaded_file = st.file_uploader("Upload Chat file", type="txt")

if uploaded_file is not None:
    # Read text
    content = uploaded_file.getvalue().decode("utf-8")
    
    with st.spinner("Analyzing chats... (might take a sec for long chats)"):
        stats = analyze_chat(content)
        
    if "error" in stats:
        st.error(stats["error"])
    else:
        st.success("Analysis Complete!")
        
        # Determine Top Talker
        if stats["count"]:
            top_talker = max(stats["count"], key=stats["count"].get)
        else:
            top_talker = "Unknown"
            
        # Display KPIs
        st.markdown("### 📊 The Dashboard")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Messages", stats["total_messages"])
        col2.metric("Health Score", f"{stats['health_score']}/100")
        col3.metric("Top Talker", top_talker)
        col4.metric("Longest Avg Text", max(stats["avg_len"], key=stats["avg_len"].get) if stats["avg_len"] else "Unknown")
        
        st.divider()
        
        # AI SUMMARY
        if api_key:
            st.markdown("### 🧠 The AI Verdict")
            with st.spinner("Consulting Gemini..."):
                summary = get_ai_summary(api_key, stats)
            st.info(summary)
        else:
            st.info("Provide a Gemini API key in the sidebar to get a custom roast and relationship verdict here.")

        # DEEP DIVE STATS
        st.markdown("### 🔍 Deep Dive")
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Message Shares")
            df_count = pd.DataFrame(list(stats["count"].items()), columns=['Sender', 'Count'])
            if not df_count.empty:
                st.bar_chart(df_count.set_index('Sender'))
        
        with c2:
            st.subheader("Average Response Time (Minutes)")
            resp = {k: round(v/60, 1) for k,v in stats["avg_response_times"].items()}
            df_resp = pd.DataFrame(list(resp.items()), columns=['Sender', 'Minutes'])
            if not df_resp.empty:
                st.bar_chart(df_resp.set_index('Sender'))
                
        # Dry Replies and Initiations
        c3, c4 = st.columns(2)
        with c3:
            st.subheader("💀 Dry Replies (Count)")
            if stats["dry_replies"]:
                for sender, count in stats["dry_replies"].items():
                    st.write(f"**{sender}**: {count}")
            else:
                st.write("No dry replies detected! Good vibes.")
                
        with c4:
            st.subheader("🔁 Initiations (Starting convo after a gap)")
            if stats["initiations"]:
                for sender, count in stats["initiations"].items():
                    st.write(f"**{sender}**: {count}")
            else:
                st.write("No clear initiations detected.")

        # Timeline
        st.markdown("### 😊 Emotional Tone Over Time")
        timeline = stats["timeline"]
        if len(timeline) > 5:
            df_timeline = pd.DataFrame(timeline)
            df_timeline.set_index("time", inplace=True)
            # Smooth it out
            df_timeline["Smoothed Sentiment"] = df_timeline["sentiment"].rolling(window=max(5, len(timeline)//20)).mean()
            st.line_chart(df_timeline["Smoothed Sentiment"])
        else:
            st.write("Not enough data over time to plot mood.")
            
