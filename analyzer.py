import re
from datetime import datetime
from collections import Counter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import google.generativeai as genai

def parse_time(time_str):
    time_str = time_str.replace(" ", " ") # Handle non-breaking spaces Whatsapp sometimes uses
    formats = [
        "%d/%m/%y, %I:%M %p",
        "%m/%d/%y, %I:%M %p",
        "%d/%m/%y, %H:%M",
        "%m/%d/%y, %H:%M",
        "%d/%m/%Y, %I:%M %p",
        "%m/%d/%Y, %I:%M %p",
        "%d/%m/%Y, %H:%M",
        "%m/%d/%Y, %H:%M",
    ]
    time_str = time_str.strip().lower() # normalize string
    if time_str.endswith(' am'):
        time_str = time_str[:-3] + ' am'
    elif time_str.endswith(' pm'):
        time_str = time_str[:-3] + ' pm'
    
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt.lower())
        except ValueError:
            pass
    return None

def analyze_chat(file_content):
    lines = file_content.split('\n')
    pattern = r"(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}.*?) - (.*?): (.*)"
    
    messages = []
    analyzer = SentimentIntensityAnalyzer()
    
    for line in lines:
        match = re.match(pattern, line)
        if match:
            time_str, sender, msg = match.groups()
            
            # Filter system messages
            if "Messages and calls are end-to-end encrypted" in msg or "omitted" in msg:
                continue
                
            score = analyzer.polarity_scores(msg)
            messages.append({
                "time_str": time_str,
                "sender": sender,
                "message": msg,
                "sentiment": score["compound"]
            })

    if not messages:
        return {"error": "Could not parse any messages. Did you export the chat correctly?"}

    # 1. Message Count
    count = Counter([msg["sender"] for msg in messages])
    
    # 2. Avg Length
    avg_len = {}
    for sender in count:
        texts = [m["message"] for m in messages if m["sender"] == sender]
        avg_len[sender] = sum(len(t) for t in texts) / len(texts) if texts else 0

    # 3. Response Times & Dry Replies
    response_times = []
    dry_replies = Counter()
    initiations = Counter()
    
    parsed_messages = []
    for msg in messages:
        t = parse_time(msg["time_str"])
        if t:
            parsed_messages.append({**msg, "time": t})
            
    for i in range(1, len(parsed_messages)):
        prev = parsed_messages[i-1]
        curr = parsed_messages[i]
        
        # Dry replies logic
        if len(curr["message"]) < 5 and curr["sentiment"] <= 0:
            dry_replies[curr["sender"]] += 1
            
        if curr["sender"] != prev["sender"]:
            diff = (curr["time"] - prev["time"]).total_seconds()
            if diff >= 0 and diff < 3600 * 24: # max 1 day to be considered a response
                response_times.append({
                    "responder": curr["sender"],
                    "time": diff
                })
        
        # Initiator detection (gap > 1 hour)
        diff = (curr["time"] - prev["time"]).total_seconds()
        if diff > 3600:
            initiations[curr["sender"]] += 1

    
    avg_response_times = {}
    for sender in count:
        times = [rt["time"] for rt in response_times if rt["responder"] == sender]
        avg_response_times[sender] = sum(times) / len(times) if times else 0

    # 4. Health Score
    health_score = 0
    if len(count) >= 2:
        top_2 = count.most_common(2)
        ratio = min(top_2[0][1], top_2[1][1]) / max(top_2[0][1], top_2[1][1])
        health_score += ratio * 30

    sentiments = [m["sentiment"] for m in messages]
    if sentiments:
        avg_sent = sum(sentiments) / len(sentiments)
        health_score += (avg_sent + 1) * 20
        
    all_times = [rt["time"] for rt in response_times]
    if all_times:
        avg_resp = sum(all_times) / len(all_times)
        health_score += max(0, 30 - (avg_resp / 60) / 10) # Using minutes

    timeline = [{"time": m["time"], "sentiment": m["sentiment"]} for m in parsed_messages if "time" in m]

    return {
        "count": dict(count),
        "avg_len": avg_len,
        "avg_response_times": avg_response_times,
        "dry_replies": dict(dry_replies),
        "initiations": dict(initiations),
        "health_score": min(round(health_score, 2), 100),
        "total_messages": len(messages),
        "timeline": timeline
    }

def get_ai_summary(api_key, stats):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Strip timeline for the prompt so it's not too large
        stats_copy = {k:v for k,v in stats.items() if k != "timeline"}
        
        prompt = f"""
        You are an AI Conversation Analyzer with a humorous, savage, social-scientist persona.
        Analyze these chat statistics and give a verdict in 2-3 short, punchy paragraphs.
        
        Stats:
        {stats_copy}
        
        Tell me who is carrying the conversation, who gives dry replies, who takes forever to respond, and the overall vibe. Be mildly roasting but fun (not mean). Use emojis.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error connecting to Gemini API: {e}"
