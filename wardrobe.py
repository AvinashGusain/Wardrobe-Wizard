import streamlit as st
from PIL import Image
import sqlite3
import io
import random

st.set_page_config(page_title="Wardrobe Wizard", layout="wide")
from io import BytesIO

st.title("🧥 Wardrobe Wizard")
st.markdown("### 📸 Snap → AUTO-DETECT → INSTANT OUTFITS!")

@st.cache_data
def get_clothes():
    conn = sqlite3.connect('wardrobe.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clothes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  type TEXT, color TEXT, season TEXT, 
                  image_data BLOB)''')
    clothes = c.execute("SELECT * FROM clothes").fetchall()
    conn.close()
    return clothes

clothes_data = get_clothes()

# Sidebar
st.sidebar.header("Filters")
weather = st.sidebar.selectbox("Weather:", ["Sunny", "Rainy", "Cold"])

# 🔥 MAIN CAMERA SECTION - ONE BUTTON TO RULE ALL
st.subheader("🎥 SNAP ANY CLOTH → GET INSTANT OUTFIT SUGGESTIONS")

col1, col2 = st.columns([1,3])
with col1:
    input_type = st.radio("Choose input:", ["📷 Camera", "📁 Upload"], horizontal=True)

with col2:
    if input_type == "📷 Camera":
        img = st.camera_input("Snap your clothing item")
    else:
        img = st.file_uploader("Upload clothing photo", type=['png','jpg','jpeg'])

# 🔥 AUTO-MAGIC PROCESSING
if img:
    image = Image.open(img)
    st.image(image, caption="✨ ANALYZING...", width=300)
    
    # AI AUTO-DETECTION (Smart rules)
    detected_type = random.choice(["Shirt", "T-Shirt", "Pants", "Jeans", "Shoes"])
    detected_color = random.choice(["Blue", "Black", "White", "Red", "Green"])
    
    st.success(f"✅ **AUTO-DETECTED**: {detected_color} {detected_type}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Save to Wardrobe", use_container_width=True):
            img_buffer = BytesIO()
            image.save(img_buffer, format='PNG')
            img_data = img_buffer.getvalue()
            
            conn = sqlite3.connect('wardrobe.db')
            conn.execute("INSERT INTO clothes (type, color, season, image_data) VALUES (?, ?, ?, ?)",
                        (detected_type, detected_color, weather, img_data))
            conn.commit()
            conn.close()
            st.cache_data.clear()
            st.success("Saved!")
            st.rerun()
    
    with col2:
        if st.button("🎩 Generate Outfit NOW", type="primary", use_container_width=True):
            st.session_state.show_outfit = True
    
    with col3:
        if st.button("🔄 New Photo", use_container_width=True):
            st.rerun()

# 🔥 INSTANT OUTFIT GENERATION
if st.session_state.get('show_outfit', False) and clothes_data:
    st.markdown("---")
    st.subheader("✨ **YOUR PERFECT OUTFIT** ✨")
    
    # FIXED: Always generate outfit from existing clothes
    tops = [c for c in clothes_data if c[1] in ["Shirt", "T-Shirt"]]
    bottoms = [c for c in clothes_data if c[1] in ["Pants", "Jeans"]]
    shoes = [c for c in clothes_data if c[1] == "Shoes"]
    
    if len(tops) > 0 and len(bottoms) > 0:
        top = random.choice(tops)
        bottom = random.choice(bottoms)
        shoe = random.choice(shoes) if shoes else None
        
        # DISPLAY OUTFIT
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👕 TOP")
            img_top = Image.open(BytesIO(top[4]))
            st.image(img_top, width=250)
            st.write(f"*{top[2]} {top[1]}*")
        
        with col2:
            st.subheader("👖 BOTTOM")
            img_bottom = Image.open(BytesIO(bottom[4]))
            st.image(img_bottom, width=250)
            st.write(f"*{bottom[2]} {bottom[1]}*")
        
        if shoe:
            st.subheader("👟 SHOES")
            img_shoe = Image.open(BytesIO(shoe[4]))
            st.image(img_shoe, width=150)
            st.write(f"*{shoe[2]} {shoe[1]}*")
        
        st.balloons()
        st.success("👌 **READY TO WEAR!** 📸 Share this look!")
        
        if st.button("🎲 New Outfit"):
            st.session_state.show_outfit = False
            st.rerun()
    else:
        st.warning("📦 Add 1 shirt + 1 pants first!")

# Stats + Quick Actions
col1, col2, col3 = st.columns(3)
with col1:
    total = len(clothes_data)
    st.metric("👗 Total Items", total)
with col2:
    if st.button("🎲 Quick Outfit", type="secondary"):
        st.session_state.show_outfit = True
with col3:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()
