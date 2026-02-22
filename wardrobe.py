import streamlit as st
from PIL import Image, ImageStat
import sqlite3
import io
import random
import numpy as np
from io import BytesIO

st.set_page_config(page_title="Wardrobe Wizard", layout="wide")

st.title("🧥 Wardrobe Wizard")
st.markdown("### 📸 Snap → **SMART DETECTION** → Perfect Outfits!")

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

# 🔥 IMPROVED COLOR DETECTION
def detect_dominant_color(image):
    """Get REAL dominant color from image"""
    # Resize for faster processing
    image_small = image.resize((100, 100))
    image_array = np.array(image_small)
    
    # Get average RGB
    avg_color = np.mean(image_array, axis=(0,1))
    r, g, b = int(avg_color[0]), int(avg_color[1]), int(avg_color[2])
    
    # Better color classification
    if r > 200 and g > 200 and b > 200:
        return "White"
    elif r > 180 and g < 120 and b < 120:
        return "Red"
    elif r > 180 and g > 180 and b < 120:
        return "Yellow"
    elif g > 180 and r < 120 and b < 120:
        return "Green"
    elif b > 180 and r < 120 and g < 120:
        return "Blue"
    elif r < 80 and g < 80 and b < 80:
        return "Black"
    elif r > 150 and g > 100 and b > 100:
        return "Pink"
    elif b > 150 and g > 150:
        return "Cyan"
    else:
        return "Gray"

def detect_clothing_type(image):
    """Better clothing type guess"""
    width, height = image.size
    aspect = width / height
    
    if aspect > 1.8:
        return "Pants"
    elif aspect > 1.2:
        return "Jeans"
    elif height > width * 1.2:
        return "T-Shirt"
    else:
        return "Shirt"

# CLEAN ONE-BUTTON FLOW
st.subheader("🎥 **Click → Snap → AUTO-DETECT**")

if st.button("📷 TAKE PHOTO", type="primary", help="Click to open camera"):
    st.session_state.show_camera = True

if st.session_state.get('show_camera', False):
    st.markdown("### 📸 Camera Ready!")
    img = st.camera_input("Point at clothing & SNAP ⬇️")
    
    if img:
        image = Image.open(img)
        st.image(image, width=400, caption="Analyzing...")
        
        # 🔥 SMARTER DETECTION
        color = detect_dominant_color(image)
        cloth_type = detect_clothing_type(image)
        
        st.markdown(f"### 🎯 **AI Detection**: *{color} {cloth_type}*")
        
        # MANUAL OVERRIDE
        col1, col2 = st.columns([1,1])
        with col1:
            override_type = st.selectbox("Type:", ["Shirt", "T-Shirt", "Pants", "Jeans", "Shoes"], 
                                       index=["Shirt", "T-Shirt", "Pants", "Jeans", "Shoes"].index(cloth_type))
        with col2:
            override_color = st.selectbox("Color:", ["White", "Black", "Blue", "Red", "Green", "Gray", "Pink"], 
                                        index=["White", "Black", "Blue", "Red", "Green", "Gray", "Pink"].index(color))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾 SAVE", use_container_width=True):
                img_buffer = BytesIO()
                image.save(img_buffer, format='PNG')
                img_data = img_buffer.getvalue()
                
                conn = sqlite3.connect('wardrobe.db')
                conn.execute("INSERT INTO clothes (type, color, season, image_data) VALUES (?, ?, ?, ?)",
                            (override_type, override_color, "All", img_data))
                conn.commit()
                conn.close()
                st.cache_data.clear()
                st.success("✅ Saved!")
                st.rerun()
        
        with col2:
            if st.button("🎩 INSTANT OUTFIT", type="primary", use_container_width=True) and len(clothes_data) >= 2:
                st.session_state.show_outfit = True
        
        with col3:
            if st.button("❌ NEW PHOTO", use_container_width=True):
                if 'show_camera' in st.session_state:
                    del st.session_state.show_camera
                st.rerun()
    else:
        st.info("📱 Click the **camera icon** (⬇️) to snap photo!")
else:
    st.info("👆 Click **📷 TAKE PHOTO** to start!")

# FIXED OUTFIT GENERATION
if st.session_state.get('show_outfit', False) and len(clothes_data) >= 2:
    st.markdown("---")
    st.subheader("✨ **PERFECT OUTFIT READY** ✨")
    
    tops = [c for c in clothes_data if c[1] in ["Shirt", "T-Shirt"]]
    bottoms = [c for c in clothes_data if c[1] in ["Pants", "Jeans"]]
    
    if tops and bottoms:
        top = random.choice(tops)
        bottom = random.choice(bottoms)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👕 TOP")
            img_top = Image.open(BytesIO(top[4]))
            st.image(img_top, width=280)
            st.caption(f"*{top[2]} {top[1]}*")
        
        with col2:
            st.subheader("👖 BOTTOM")
            img_bottom = Image.open(BytesIO(bottom[4]))
            st.image(img_bottom, width=280)
            st.caption(f"*{bottom[2]} {bottom[1]}*")
        
        st.balloons()
        st.success("👌 **ROCK THIS LOOK!** 📸 Share screenshot!")
        
        if st.button("🎲 NEW OUTFIT"):
            st.session_state.show_outfit = False
            st.rerun()
    else:
        st.error("❌ Add 1 shirt/t-shirt + 1 pants/jeans first!")

# STATS
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("👗 Total Items", len(clothes_data))
with col2:
    tops_count = len([c for c in clothes_data if c[1] in ["Shirt", "T-Shirt"]])
    st.metric("👕 Tops", tops_count)
with col3:
    bottoms_count = len([c for c in clothes_data if c[1] in ["Pants", "Jeans"]])
    st.metric("👖 Bottoms", bottoms_count)

if st.button("🎲 QUICK OUTFIT") and len(clothes_data) >= 2:
    st.session_state.show_outfit = True
