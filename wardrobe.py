import streamlit as st
from PIL import Image
import sqlite3
import io
import random

# MUST BE FIRST
st.set_page_config(page_title="Wardrobe Wizard", layout="wide")

from io import BytesIO

st.title("🧥 Wardrobe Wizard")
st.markdown("### 📸 SNAP your clothes → Get perfect outfits instantly!")

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
outfit_type = st.sidebar.selectbox("Outfit type:", ["Work", "Casual", "Party", "Gym"])
weather = st.sidebar.selectbox("Weather:", ["Sunny", "Rainy", "Cold"])

# Tabs
tab1, tab2 = st.tabs(["📷 CAMERA (NEW!)", "🎩 Get Outfit"])

with tab1:
    st.subheader("🎥 Live Camera - Snap Your Clothes!")
    
    # 🔥 CAMERA INPUT
    camera_img = st.camera_input("Point at your clothing item")
    
    col1, col2 = st.columns([3,1])
    with col1:
        cloth_type = st.selectbox("Type:", ["Shirt", "T-Shirt", "Pants", "Jeans", "Shoes", "Jacket"])
        color = st.text_input("Color (e.g., Blue, Black):")
        season = st.selectbox("Season:", ["Summer", "Winter", "All"])
    
    # Show captured image
    if camera_img:
        image = Image.open(camera_img)
        st.image(image, caption="✅ Captured!", width=300)
        
        if color and st.button("✅ Save to Wardrobe", type="primary"):
            # Save camera image to DB
            img_buffer = BytesIO()
            image.save(img_buffer, format='PNG')
            img_data = img_buffer.getvalue()
            
            conn = sqlite3.connect('wardrobe.db')
            conn.execute("INSERT INTO clothes (type, color, season, image_data) VALUES (?, ?, ?, ?)",
                        (cloth_type, color, season, img_data))
            conn.commit()
            conn.close()
            
            st.success("🎉 Added to wardrobe!")
            st.balloons()
            st.cache_data.clear()
            st.rerun()
    
    # Fallback: file upload
    else:
        st.info("👆 Click camera above OR drag image file below")
        uploaded_file = st.file_uploader("📁 Or upload photo", type=['png','jpg','jpeg'])
        if uploaded_file and color and st.button("✅ Save from Upload"):
            image = Image.open(uploaded_file)
            img_buffer = BytesIO()
            image.save(img_buffer, format='PNG')
            img_data = img_buffer.getvalue()
            
            conn = sqlite3.connect('wardrobe.db')
            conn.execute("INSERT INTO clothes (type, color, season, image_data) VALUES (?, ?, ?, ?)",
                        (cloth_type, color, season, img_data))
            conn.commit()
            conn.close()
            
            st.success("🎉 Added to wardrobe!")
            st.cache_data.clear()
            st.rerun()

with tab2:
    st.subheader("✨ Generate Perfect Outfit")
    
    if st.button("🎲 Get Random Outfit", type="primary") and clothes_data:
        tops = [c for c in clothes_data if c[1] in ["Shirt", "T-Shirt"]]
        bottoms = [c for c in clothes_data if c[1] in ["Pants", "Jeans"]]
        
        if tops and bottoms:
            top = random.choice(tops)
            bottom = random.choice(bottoms)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("👕 Top")
                img_top = Image.open(BytesIO(top[4]))
                st.image(img_top, width=200, caption=f"{top[2]} {top[1]}")
            
            with col2:
                st.subheader("👖 Bottom")
                img_bottom = Image.open(BytesIO(bottom[4]))
                st.image(img_bottom, width=200, caption=f"{bottom[2]} {bottom[1]}")
            
            st.success("👌 Perfect outfit ready!")
            st.balloons()
        else:
            st.warning("👕 Add shirts AND pants first!")

# Stats
total = len(clothes_data)
st.metric("Total Items", total)

if st.button("🔄 Refresh"):
    st.cache_data.clear()
    st.rerun()
