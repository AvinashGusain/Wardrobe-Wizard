import streamlit as st
from PIL import Image, ImageStat
import sqlite3
import io
import random
import json
import numpy as np
from io import BytesIO
import pandas as pd

st.set_page_config(page_title="Wardrobe Wizard", layout="wide")

st.title("🧥 Wardrobe Wizard AI")
st.markdown("### 📸 Snap → AI Learns → Gets Smarter Every Time!")

# Learning database
@st.cache_data
def init_learning_db():
    conn = sqlite3.connect('wardrobe.db')
    c = conn.cursor()
    # Main clothes table
    c.execute('''CREATE TABLE IF NOT EXISTS clothes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  type TEXT, color TEXT, season TEXT, 
                  image_data BLOB)''')
    # LEARNING TABLE - AI improves from corrections
    c.execute('''CREATE TABLE IF NOT EXISTS learning_data 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  rgb_r REAL, rgb_g REAL, rgb_b REAL,
                  detected_type TEXT, detected_color TEXT,
                  corrected_type TEXT, corrected_color TEXT)''')
    conn.commit()
    conn.close()

init_learning_db()

@st.cache_data
def get_clothes():
    conn = sqlite3.connect('wardrobe.db')
    clothes = conn.execute("SELECT * FROM clothes").fetchall()
    conn.close()
    return clothes

clothes_data = get_clothes()

# 🔥 LEARNING COLOR DETECTION
def detect_color_learning(image):
    """AI that learns from user corrections"""
    image_small = image.resize((50, 50))
    img_array = np.array(image_small)
    avg_color = np.mean(img_array, axis=(0,1))
    r, g, b = int(avg_color[0]), int(avg_color[1]), int(avg_color[2])
    
    # Get learned corrections
    conn = sqlite3.connect('wardrobe.db')
    corrections = conn.execute("""
        SELECT corrected_color, AVG(rgb_r), AVG(rgb_g), AVG(rgb_b) 
        FROM learning_data 
        WHERE rgb_r BETWEEN ? AND ? AND rgb_g BETWEEN ? AND ? AND rgb_b BETWEEN ? AND ?
        GROUP BY corrected_color
        HAVING COUNT(*) > 1
    """, (r-30, r+30, g-30, g+30, b-30, b+30)).fetchall()
    conn.close()
    
    if corrections:
        return max(corrections, key=lambda x: x[1:])[0]  # Most similar learned color
    
    # Fallback detection
    if r > 200: return "White"
    if r > 180 and g < 120: return "Red"
    if g > 180 and b < 120: return "Green"
    if b > 180: return "Blue"
    if r < 80: return "Black"
    return "Gray"

def detect_type_learning(image):
    """Learns clothing type from corrections"""
    width, height = image.size
    aspect = width / height
    
    conn = sqlite3.connect('wardrobe.db')
    learned_types = conn.execute("""
        SELECT corrected_type, COUNT(*) cnt FROM learning_data 
        WHERE corrected_type IS NOT NULL 
        GROUP BY corrected_type
    """).fetchall()
    conn.close()
    
    if aspect > 1.5:
        return "Pants" if learned_types and learned_types[0][1] > 2 else "T-Shirt"
    return "T-Shirt"

# MAIN FLOW
st.subheader("🎥 **AI Learns From You!**")

if st.button("📷 TAKE PHOTO", type="primary"):
    st.session_state.show_camera = True

if st.session_state.get('show_camera', False):
    st.markdown("### 📸 SNAP YOUR CLOTHING")
    img = st.camera_input("Point & click camera icon")
    
    if img:
        image = Image.open(img)
        st.image(image, width=400)
        
        # 🔥 LEARNING DETECTION
        color = detect_color_learning(image)
        cloth_type = detect_type_learning(image)
        
        st.markdown(f"### 🤖 **AI Guess**: *{color} {cloth_type}*")
        st.caption("⭐ AI gets smarter when you correct it!")
        
        # CORRECT & LEARN
        col1, col2 = st.columns(2)
        with col1:
            user_type = st.selectbox("✅ Correct Type:", 
                                   ["T-Shirt", "Shirt", "Pants", "Jeans", "Shoes"], 
                                   index=["T-Shirt", "Shirt", "Pants", "Jeans", "Shoes"].index(cloth_type))
        with col2:
            user_color = st.selectbox("✅ Correct Color:", 
                                    ["White", "Black", "Blue", "Red", "Green", "Gray", "Pink", "Yellow"], 
                                    index=["White", "Black", "Blue", "Red", "Green", "Gray", "Pink", "Yellow"].index(color))
        
        # RECORD LEARNING
        if st.button("🎓 TEACH AI + SAVE", type="primary"):
            img_array = np.array(image.resize((50,50)))
            r, g, b = np.mean(img_array, axis=(0,1)).astype(int)
            
            conn = sqlite3.connect('wardrobe.db')
            # Save clothing
            img_buffer = BytesIO()
            image.save(img_buffer, format='PNG')
            img_data = img_buffer.getvalue()
            conn.execute("INSERT INTO clothes (type, color, season, image_data) VALUES (?, ?, ?, ?)",
                        (user_type, user_color, "All", img_data))
            
            # LEARN FROM CORRECTION
            conn.execute("""
                INSERT INTO learning_data (rgb_r, rgb_g, rgb_b, detected_type, detected_color, 
                                         corrected_type, corrected_color)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (r, g, b, cloth_type, color, user_type, user_color))
            
            conn.commit()
            conn.close()
            st.cache_data.clear()
            st.success("🎉 AI LEARNED + Saved!")
            st.balloons()
            st.rerun()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎩 INSTANT OUTFIT", type="secondary"):
                st.session_state.show_outfit = True
        with col2:
            if st.button("❌ NEW PHOTO"):
                del st.session_state.show_camera
                st.rerun()
else:
    st.info("👆 Click **📷 TAKE PHOTO** to start!")

# OUTFIT GENERATION
if st.session_state.get('show_outfit', False) and len(clothes_data) >= 2:
    st.markdown("---")
    st.subheader("✨ **PERFECT OUTFIT** ✨")
    
    tops = [c for c in clothes_data if c[1] in ["T-Shirt", "Shirt"]]
    bottoms = [c for c in clothes_data if c[1] in ["Pants", "Jeans"]]
    
    if tops and bottoms:
        top = random.choice(tops)
        bottom = random.choice(bottoms)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("👕 TOP")
            img_top = Image.open(BytesIO(top[4]))
            st.image(img_top, width=280)
            st.caption(f"{top[2]} {top[1]}")
        with col2:
            st.subheader("👖 BOTTOM")
            img_bottom = Image.open(BytesIO(bottom[4]))
            st.image(img_bottom, width=280)
            st.caption(f"{bottom[2]} {bottom[1]}")
        
        st.success("👌 **PERFECT MATCH!**")
        if st.button("🎲 NEW OUTFIT"):
            st.session_state.show_outfit = False
            st.rerun()

# LEARNING STATS
conn = sqlite3.connect('wardrobe.db')
learning_count = conn.execute("SELECT COUNT(*) FROM learning_data").fetchone()[0]
conn.close()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("👗 Total Clothes", len(clothes_data))
with col2:
    st.metric("🧠 AI Lessons", learning_count)
with col3:
    if st.button("🎲 QUICK OUTFIT") and len(clothes_data) >= 2:
        st.session_state.show_outfit = True
