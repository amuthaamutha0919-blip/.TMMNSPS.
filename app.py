import streamlit as st
import pandas as pd
from datetime import datetime, date, time

# --- 1. பக்க அமைப்புகள் மற்றும் பிரீமியம் CSS ---
st.set_page_config(page_title="சங்க மேலாண்மை", layout="centered")

st.markdown("""
    <style>
    .main { background: #f4f7f6; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #e1e4e8; border-radius: 10px; padding: 10px 20px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #2E86C1; color: white; }
    .premium-card {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 5px solid #2E86C1;
        margin-bottom: 15px;
    }
    .id-card-wrap {
        background: linear-gradient(135deg, #1b263b 0%, #0d1b2a 100%);
        padding: 30px; border-radius: 20px; color: white; width: 320px;
        text-align: center; margin: auto; border: 3px solid #F1C40F;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# உங்கள் சங்கத்தின் லோகோ
LOGO_URL = "https://i.ibb.co/XwhBx8S/image.png" 

# --- 2. டேட்டாபேஸ் மேலாண்மை (Session State) ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = pd.DataFrame(columns=["பெயர்", "மொபைல்", "பிறந்தநாள்_நிதி", "விழா_நிதி", "கட்டிய_தேதி"])
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["தேதி", "விவரம்", "தொகை"])
if 'locks' not in st.session_state:
    st.session_state.locks = {"bday": True, "fest": True, "id_card": True, "contacts": True}
if 'targets' not in st.session_state:
    st.session_state.targets = {
        "bday_amt": 30, "fest_amt": 500, 
        "fest_name": "பொங்கல் விழா", "fest_dt": date.today()
    }

# --- 3. லாகின் வசதி ---
st.sidebar.image(LOGO_URL, width=150)
st.sidebar.title("🔐 சங்க லாகின்")
user_type = st.sidebar.selectbox("யார் நீங்கள்?", ["உறுப்பினர்", "தலைவர் (Admin)"])
password = st.sidebar.text_input("கடவுச்சொல்", type="password")

is_admin = (user_type == "தலைவர் (Admin)" and password == "admin123")
is_member = (user_type == "உறுப்பினர்" and password == "member123")

# --- 4. தலைவர் நிர்வாக அறை (Admin Panel) ---
if is_admin:
    st.markdown("<h1 style='text-align: center; color: #1B4F72;'>👨‍✈️ சங்க நிர்வாக அறை</h1>", unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["🔒 கட்டுப்பாடுகள்", "👥 உறுப்பினர் & வரவு", "📊 கணக்கு வழக்கு"])

    with t1:
        st.subheader("மாஸ்டர் லாக் (Master Locks)")
        col_a, col_b = st.columns(2)
        st.session_state.locks['id_card'] = col_a.toggle("ஐடி கார்டு பக்கம் திற", value=st.session_state.locks['id_card'])
        st.session_state.locks['fest'] = col_b.toggle("விழா நிதி பக்கம் திற", value=st.session_state.locks['fest'])
        st.session_state.locks['contacts'] = col_a.toggle("தொடர்புகள் பக்கம் திற", value=st.session_state.locks['contacts'])
        
        st.divider()
        st.subheader("இலக்கு & காலக்கெடு")
        st.session_state.targets['fest_name'] = st.text_input("விழா பெயர்", value=st.session_state.targets['fest_name'])
        st.session_state.targets['fest_dt'] = st.date_input("விழா தேதி", value=st.session_state.targets['fest_dt'])
        st.session_state.targets['fest_amt'] = st.number_input("விழா நிதி (₹)", value=st.session_state.targets['fest_amt'])

    with t2:
        st.subheader("உறுப்பினர் மேலாண்மை (Auto-Save)")
        search = st.text_input("🔍 பெயர் அல்லது மொபைல் மூலம் தேடுக...")
        
        if st.button("➕ புதிய உறுப்பினரைச் சேர்"):
            new_member = pd.DataFrame([{"பெயர்": "புதியவர்", "மொபைல்": "0000", "பிறந்தநாள்_நிதி": 0, "விழா_நிதி": 0, "கட்டிய_தேதி": "-"}])
            st.session_state.user_db = pd.concat([st.session_state.user_db, new_member], ignore_index=True)
            st.rerun()

        res = st.session_state.user_db[st.session_state.user_db['பெயர்'].str.contains(search, case=False)]
        for i, row in res.iterrows():
            with st.expander(f"👤 {row['பெயர்']} (ID: {abs(hash(row['மொபைல்'])) % 10000})"):
                st.session_state.user_db.at[i, 'பெயர்'] = st.text_input("பெயர்", value=row['பெயர்'], key=f"n_{i}")
                st.session_state.user_db.at[i, 'மொபைல்'] = st.text_input("மொபைல்", value=row['மொபைல்'], key=f"m_{i}")
                st.session_state.user_db.at[i, 'விழா_நிதி'] = st.number_input("செலுத்திய தொகை", value=int(row['விழா_நிதி']), key=f"f_{i}")
                st.session_state.user_db.at[i, 'கட்டிய_தேதி'] = datetime.now().strftime("%d-%m-%Y %H:%M")

    with t3:
        st.subheader("செலவுப் பதிவு")
        e_desc = st.text_input("செலவு விவரம்")
        e_amt = st.number_input("தொகை", min_value=0)
        if st.button("செலவைச் சேமி"):
            new_e = pd.DataFrame([{"தேதி": date.today(), "விவரம்": e_desc, "தொகை": e_amt}])
            st.session_state.expenses = pd.concat([st.session_state.expenses, new_e], ignore_index=True)
        st.table(st.session_state.expenses)

# --- 5. உறுப்பினர் பக்கம் (Member Page) ---
elif is_member:
    st.markdown(f"<div style='text-align: center;'><img src='{LOGO_URL}' width='100'></div>", unsafe_allow_html=True)
    choice = st.sidebar.radio("செல்", ["🏠 முகப்பு", "💰 நிதி நிலை", "🪪 ஐடி கார்டு", "📞 தொடர்புகள்"])

    if choice == "🏠 முகப்பு":
        days = (st.session_state.targets['fest_dt'] - date.today()).days
        st.markdown(f"<div style='background: white; padding: 30px; border-radius: 20px; text-align: center; border: 2px solid #2E86C1;'>"
                    f"<h3>{st.session_state.targets['fest_name']} வர இன்னும்</h3>"
                    f"<h1 style='color: #E67E22;'>{max(0, days)} நாட்கள்</h1></div>", unsafe_allow_html=True)

    elif choice == "🪪 ஐடி கார்டு":
        if st.session_state.locks['id_card'] and not st.session_state.user_db.empty:
            row = st.session_state.user_db.iloc[0] # உதாரணத்திற்கு முதல் உறுப்பினர்
            st.markdown(f"""
                <div class="id-card-wrap">
                    <img src="{LOGO_URL}" width="80" style="border-radius: 50%; background: white; padding: 5px;">
                    <h2 style="margin: 15px 0 5px 0;">{row['பெயர்']}</h2>
                    <p style="opacity: 0.8;">சங்க உறுப்பினர்</p>
                    <hr style="border: 0.5px solid rgba(255,255,255,0.2);">
                    <p style="font-size: 18px;">📱 {row['மொபைல்']}</p>
                    <div style="background: #F1C40F; color: #0d1b2a; padding: 10px; border-radius: 10px; font-weight: bold; font-size: 20px; margin-top: 15px;">
                        ID NO: {abs(hash(row['மொபைல்'])) % 10000}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else: st.error("🔒 ஐடி கார்டு பக்கம் பூட்டப்பட்டுள்ளது.")

    elif choice == "தொடர்புகள்":
        if st.session_state.locks['contacts']:
            for i, row in st.session_state.user_db.iterrows():
                st.markdown(f"**{row['பெயர்']}** - 📱 {row['மொபைல்']} [📞 Call](tel:{row['மொபைல்']})")
                st.divider()

# --- 6. லாகின் இல்லாத முகப்பு ---
else:
    st.markdown(f"<div style='text-align: center; margin-top: 50px;'><img src='{LOGO_URL}' width='200'><h1>சங்க டிஜிட்டல் ஆப்</h1><p>லாகின் செய்து தொடரவும்</p></div>", unsafe_allow_html=True)

# சைடு பாரில் இருப்பு நிலை (Balance)
if is_admin or is_member:
    st.sidebar.divider()
    t_in = st.session_state.user_db['விழா_நிதி'].sum()
    t_out = st.session_state.expenses['தொகை'].sum()
    st.sidebar.metric("சங்க இருப்பு", f"₹{t_in - t_out}")
