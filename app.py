import streamlit as st
import sqlite3
from datetime import datetime
import re
from collections import Counter

DB = 'agent_memory.db'

def connect():
    con = sqlite3.connect(DB)
    con.execute('''CREATE TABLE IF NOT EXISTS memory(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_input TEXT,
        response TEXT,
        feedback INTEGER DEFAULT 0,
        created_at TEXT
    )''')
    return con

def save_interaction(q, a):
    con = connect()
    cur = con.execute('INSERT INTO memory(user_input,response,created_at) VALUES(?,?,?)',
                      (q, a, datetime.now().isoformat(timespec='seconds')))
    con.commit(); row_id = cur.lastrowid; con.close()
    return row_id

def feedback(row_id, value):
    con = connect(); con.execute('UPDATE memory SET feedback=? WHERE id=?',(value,row_id)); con.commit(); con.close()

def history(limit=100):
    con = connect(); rows = con.execute('SELECT id,user_input,response,feedback,created_at FROM memory ORDER BY id DESC LIMIT ?', (limit,)).fetchall(); con.close()
    return rows

def tokens(text):
    return set(re.findall(r'[a-zA-Z0-9]+', text.lower()))

def best_memory(query):
    q = tokens(query); best = None; score = 0
    for row in history(200):
        if row[3] < 0: continue
        t = tokens(row[1]); union = q | t
        s = len(q & t) / len(union) if union else 0
        s += 0.12 if row[3] > 0 else 0
        if s > score: score, best = s, row
    return best if score >= 0.25 else None

def agent_reply(query):
    old = best_memory(query)
    if old:
        return ("I found a useful pattern in my learned memory.\n\n"
                f"Previous related task: {old[1]}\n\n"
                f"Learned answer: {old[2]}\n\n"
                "I reused this because it is similar to your current request. Your feedback will help me improve this choice.")
    q = query.lower()
    if any(x in q for x in ['hello','hi','hey']):
        return "Hello! Give me a task or question. I will store the interaction and use your feedback to improve future responses."
    if 'python' in q:
        return "For a Python task, I would break the problem into input, processing, output, and validation. Add more details and I can learn the preferred solution from your feedback."
    if 'study' in q or 'learn' in q:
        return "A useful learning plan is: define the goal, split it into small topics, practice each topic, test yourself, then revise weak areas. I can remember which approach you prefer."
    return ("I analyzed your request but do not have a strong learned match yet. "
            "This local demo improves by storing successful previous responses. "
            "Give feedback after each answer; positively rated patterns are prioritized for similar future questions.")

st.set_page_config(page_title='Self-Learning AI Agent', page_icon='🧠', layout='wide')
st.title('🧠 Self-Learning AI Agent')
st.caption('Local Python AI agent • Persistent memory • Feedback learning • No paid API required')

with st.sidebar:
    st.header('Agent Controls')
    page = st.radio('Navigate', ['Chat Agent','Learning Dashboard','Memory'])
    if st.button('Reset all memory', type='secondary'):
        con=connect(); con.execute('DELETE FROM memory'); con.commit(); con.close(); st.success('Memory reset.')

if page == 'Chat Agent':
    st.subheader('Talk to the agent')
    prompt = st.text_area('Enter a task or question', placeholder='Example: Give me a Python study plan...', height=120)
    if st.button('Run Agent', type='primary', use_container_width=True) and prompt.strip():
        answer = agent_reply(prompt.strip())
        rid = save_interaction(prompt.strip(), answer)
        st.session_state['last_id'] = rid
        st.session_state['last_answer'] = answer
    if st.session_state.get('last_answer'):
        st.markdown('### Agent response')
        st.info(st.session_state['last_answer'])
        c1,c2 = st.columns(2)
        if c1.button('👍 Helpful', use_container_width=True):
            feedback(st.session_state['last_id'], 1); st.success('Learned: this response was useful.')
        if c2.button('👎 Not helpful', use_container_width=True):
            feedback(st.session_state['last_id'], -1); st.warning('Learned: this response should be avoided.')

elif page == 'Learning Dashboard':
    rows=history(500); total=len(rows); pos=sum(r[3]>0 for r in rows); neg=sum(r[3]<0 for r in rows)
    a,b,c=st.columns(3); a.metric('Interactions',total); b.metric('Positive Feedback',pos); c.metric('Negative Feedback',neg)
    st.subheader('What the agent has learned')
    words=[]
    for r in rows:
        if r[3]>0: words += list(tokens(r[1]))
    common=Counter(words).most_common(12)
    if common:
        st.bar_chart({w:n for w,n in common})
    else: st.info('Give positive feedback to build learned patterns.')

else:
    st.subheader('Persistent Agent Memory')
    rows=history(100)
    if not rows: st.info('No memories yet.')
    for r in rows:
        mark='👍' if r[3]>0 else ('👎' if r[3]<0 else '—')
        with st.expander(f'{mark} {r[1][:80]} • {r[4]}'):
            st.write(r[2])
