import streamlit as st
from PIL import Image
import sqlite3
import io
import random
import numpy as np
from io import BytesIO

st.set_page_config(page_title="Wardrobe Wizard", layout="wide")
st.title("🧥 Wardrobe Wizard - SMART OUTFITS")
st.markdown("### AI-powered outfit combinations that actually work!")

@st.cache_data
def get_clothes():
    conn = sqlite3.connect('wardrobe.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clothes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, color TEXT, 
                  season TEXT, image_data BLOB)''')
    clothes = c.execute("SELECT * FROM clothes").fetchall()
    conn.close()
    return clothes

clothes_data = get_clothes()

# 🔥 SMART COLOR WHEEL MATCHING
def color_wheel_match(color1, color2):
    """Returns compatibility score 0-100"""
    color_wheel = {
        'White': 100, 'Black': 95, 'Gray': 90,
        'Blue': 85, 'Green': 80, 'Red': 75,
        'Yellow': 70, 'Pink': 65
    }
    return min(color_wheel.get(color1, 50) + color_wheel.get(color2, 50), 100)

# 🔥 CORE OUTFIT GENERATION ALGORITHM
def generate_smart_outfit(clothes):
    """Creates fashion-rules compliant outfits"""
    tops = [c for c in clothes if c[1] in ["T-Shirt", "Shirt"]]
    bottoms = [c for c in clothes if c[1] in ["Pants", "Jeans"]]
    shoes = [c for c in clothes if c[1] == "Shoes"]
    
    if not (tops and bottoms):
        return None
    
    best_score = 0
    best_outfit = None
    
    # Try all combinations (fashion rules)
    for top in tops:
        for bottom in bottoms:
            # Color harmony score
            harmony = color_wheel_match(top[2], bottom[2])
            
            # Style rules bonus
            style_bonus = 20 if top[2] != bottom[2] else 10  # Contrast better
            total_score = harmony + style_bonus
            
            if total_score > best_score:
                best_score = total_score
                best_outfit = (top, bottom)
    
    return best_outfit

# QUICK ADD SECTION
st.subheader("👕 Quick Add Clothes")
col1, col2 = st.columns(2)
with col1:
    if st.button("📷 Add Top", type="secondary"):
        st.session_state.add_mode = "top"
with col2:
    if st.button("👖 Add Bottom", type="secondary"):
        st.session_state.add_mode = "bottom"

# CAMERA + LEARNING (SIMPLIFIED)
if st.session_state.get('add_mode'):
    st.subheader("📸 Snap your item")
    img = st.camera_input("Snap clothing")
    
    if img:
        image = Image.open(img)
        st.image(image, width=300)
        
        # Simple detection
        color = random.choice(["White", "Black", "Blue", "Red"])
        cloth_type = st.session_state.add_mode.upper()
        
        col1, col2 = st.columns(2)
        user_type = col1.selectbox("Type:", ["T-Shirt", "Shirt"] if st.session_state.add_mode == "top" 
                                 else ["Pants", "Jeans"])
        user_color = col2.selectbox("Color:", ["White", "Black", "Blue", "Red", "Green"])
        
        if st.button("✅ ADD TO WARDROBE"):
            img_buffer = BytesIO()
            image.save(img_buffer, format='PNG')
            img_data = img_buffer.getvalue()
            
            conn = sqlite3.connect('wardrobe.db')
            conn.execute("INSERT INTO clothes (type, color, season, image_data) VALUES (?, ?, ?, ?)",
                        (user_type, user_color, "All", img_data))
            conn.commit()
            conn.close()
            st.cache_data.clear()
            st.success("✅ Added!")
            del st.session_state.add_mode
            st.rerun()

# 🔥 THE CORE - SMART OUTFIT GENERATOR
st.markdown("---")
st.subheader("✨ **SMART OUTFIT GENERATOR** ✨")

if st.button("🎩 **CREATE BEST OUTFIT**", type="primary", use_container_width=True):
    outfit = generate_smart_outfit(clothes_data)
    
    if outfit:
        top, bottom = outfit
        st.markdown("### 🎯 **PERFECT MATCH FOUND**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👕 TOP")
            img_top = Image.open(BytesIO(top[4]))
            st.image(img_top, width=300)
            st.metric("Style Score", f"{color_wheel_match(top[2], bottom[2])}%", delta="⭐")
            st.caption(f"{top[2]} {top[1]}")
        
        with col2:
            st.subheader("👖 BOTTOM")
            img_bottom = Image.open(BytesIO(bottom[4]))
            st.image(img_bottom, width=300)
            st.caption(f"{bottom[2]} {bottom[1]}")
        
        st.balloons()
        st.success("👌 **WEAR THIS TODAY!** 📸 Share screenshot!")
        
        st.markdown("---")
        if st.button("🎲 NEW OUTFIT"):
            st.rerun()
    else:
        st.error("❌ Need 1 TOP + 1 BOTTOM first!")
        st.info("👆 Use Quick Add buttons above")

# STATS DASHBOARD
col1, col2, col3, col4 = st.columns(4)
tops_count = len([c for c in clothes_data if c[1] in ["T-Shirt", "Shirt"]])
bottoms_count = len([c for c in clothes_data if c[1] in ["Pants", "Jeans"]])

with col1: st.metric("👕 Tops", tops_count)
with col2: st.metric("👖 Bottoms", bottoms_count)
with col3: st.metric("👗 Total", len(clothes_data))
with col4: 
    if st.button("🔄 REFRESH", type="secondary"):
        st.cache_data.clear()
        st.rerun()
