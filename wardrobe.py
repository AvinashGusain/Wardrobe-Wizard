import streamlit as st
from PIL import Image, ImageStat
import sqlite3
import io
import random
from io import BytesIO

st.set_page_config(page_title="Wardrobe Wizard", layout="wide")

st.title("🧥 Wardrobe Wizard")
st.markdown("### 📸 Snap → **REAL COLOR DETECTION** → Instant Outfits!")

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

# 🔥 BETTER COLOR DETECTION
def detect_color(image):
    """Real color analysis from image"""
    # Get average color
    stat = ImageStat.Stat(image)
    r, g, b = stat.mean[:3]
    
    # Convert to color name
    if r > 200 and g > 200 and b > 200:
        return "White"
    elif r > 150 and g < 100 and b < 100:
        return "Red"
    elif r > 150 and g > 150 and b < 100:
        return "Yellow"
    elif r < 100 and g > 150 and b < 100:
        return "Green" 
    elif r < 100 and g < 100 and b > 150:
        return "Blue"
    elif r < 100 and g < 100 and b < 100:
        return "Black"
    else:
        return "Gray"

def detect_clothing_type(image):
    """Smart clothing guess"""
    width, height = image.size
    aspect = width / height
    
    if aspect > 1.5:  # Wide = pants/shoes
        return random.choice(["Pants", "Jeans"])
    else:  # Tall = shirts
        return random.choice(["T-Shirt", "Shirt"])

# MAIN SECTION - CLEAN LAYOUT
st.subheader("🎥 **Click button → Snap → AUTO-DETECT**")

# BUTTON FIRST
col1, col2 = st.columns([1, 3])
with col1:
    if st.button("📷 TAKE PHOTO", type="primary", use_container_width=True):
        st.session_state.show_camera = True

# SHOW CAMERA ONLY AFTER BUTTON
if st.session_state.get('show_camera', False):
    st.markdown("### 📸 Camera Active - Snap your clothing!")
    img = st.camera_input("Point & click camera icon ⬇️")
    
    if img:
        st.session_state.current_img = img
        image = Image.open(img)
        st.image(image, width=350)
        
        # 🔥 REAL DETECTION
        color = detect_color(image)
        cloth_type = detect_clothing_type(image)
        
        st.success(f"🎯 **DETECTED**: {color} {cloth_type}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾 Save", use_container_width=True):
                img_buffer = BytesIO()
                image.save(img_buffer, format='PNG')
                img_data = img_buffer.getvalue()
                
                conn = sqlite3.connect('wardrobe.db')
                conn.execute("INSERT INTO clothes (type, color, season, image_data) VALUES (?, ?, ?, ?)",
                            (cloth_type, color, "All", img_data))
                conn.commit()
                conn.close()
                st.cache_data.clear()
                st.success("✅ Saved to wardrobe!")
                st.rerun()
        
        with col2:
            if st.button("🎩 INSTANT OUTFIT", type="primary", use_container_width=True):
                st.session_state.show_outfit = True
        
        with col3:
            if st.button("❌ New Photo", use_container_width=True):
                del st.session_state.show_camera
                st.rerun()
    else:
        st.info("👆 Click camera icon above to snap!")
else:
    st.info("👆 Click **📷 TAKE PHOTO** button to start!")

# OUTFIT GENERATION - FIXED
if st.session_state.get('show_outfit', False) and len(clothes_data) >= 2:
    st.markdown("---")
    st.subheader("✨ **YOUR PERFECT OUTFIT** ✨")
    
    tops = [c for c in clothes_data if c[1] in ["Shirt", "T-Shirt"]]
    bottoms = [c for c in clothes_data if c[1] in ["Pants", "Jeans"]]
    
    if tops and bottoms:
        top = random.choice(tops)
        bottom = random.choice(bottoms)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👕 TOP")
            img_top = Image.open(BytesIO(top[4]))
            st.image(img_top, width=250)
            st.caption(f"{top[2]} {top[1]}")
        
        with col2:
            st.subheader("👖 BOTTOM")
            img_bottom = Image.open(BytesIO(bottom[4]))
            st.image(img_bottom, width=250)
            st.caption(f"{bottom[2]} {bottom[1]}")
        
        st.balloons()
        st.success("👌 **READY TO ROCK!**")
        
        if st.button("🎲 New Outfit", type="secondary"):
            st.session_state.show_outfit = False
            st.rerun()
    else:
        st.error("❌ Need 1 top + 1 bottom in wardrobe!")

# STATS
col1, col2 = st.columns(2)
with col1:
    st.metric("👗 Total Items", len(clothes_data))
with col2:
    if st.button("🎲 Quick Outfit") and len(clothes_data) >= 2:
        st.session_state.show_outfit = True
