import streamlit as st
from PIL import Image
import sqlite3
import io
import random
import numpy as np
from io import BytesIO
from collections import defaultdict

st.set_page_config(page_title="Wardrobe Wizard", layout="wide")
st.title("🧥 Wardrobe Wizard AI")
st.markdown("### Smart outfits for ANY scenario!")

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

# 🔥 FASHION AI KNOWLEDGE BASE (Internet rules)
OUTFIT_RULES = {
    # Weather-based rules
    "Sunny": {"tops": ["T-Shirt", "Shirt"], "bottoms": ["Jeans", "Pants"], "score_bonus": 20},
    "Rainy": {"tops": ["Shirt"], "bottoms": ["Jeans"], "score_bonus": 15},
    "Cold": {"tops": ["Shirt"], "bottoms": ["Pants"], "score_bonus": 25},
    
    # Color harmony rules
    "White": ["Blue", "Black", "Red", "Green"],
    "Black": ["White", "Red", "Yellow", "Blue"], 
    "Blue": ["White", "Gray", "Black"],
    "Red": ["Black", "White", "Gray"],
}

def generate_outfits(specific_item_id=None, weather="Sunny", mode="smart", count=3):
    """Generate MULTIPLE smart outfits"""
    tops = [c for c in clothes_data if c[1] in ["T-Shirt", "Shirt"]]
    bottoms = [c for c in clothes_data if c[1] in ["Pants", "Jeans"]]
    
    outfits = []
    
    if mode == "random" or not tops or not bottoms:
        # Pure random fallback
        for _ in range(count):
            if tops and bottoms:
                outfits.append((random.choice(tops), random.choice(bottoms)))
    
    else:
        # SMART matching
        best_combos = []
        
        for top in tops:
            for bottom in bottoms:
                score = 0
                
                # Weather bonus
                weather_bonus = OUTFIT_RULES.get(weather, {}).get("score_bonus", 0)
                
                # Color harmony
                if bottom[2] in OUTFIT_RULES.get(top[2], []):
                    score += 40
                
                # Contrast bonus
                if top[2] != bottom[2]:
                    score += 20
                
                # Specific item priority
                if specific_item_id and (top[0] == specific_item_id or bottom[0] == specific_item_id):
                    score += 50
                
                best_combos.append((score, top, bottom))
        
        # Top N outfits
        best_combos.sort(reverse=True)
        outfits = [(top, bottom) for score, top, bottom in best_combos[:count]]
    
    return outfits

# 🔥 MAIN OUTFIT GENERATOR
st.subheader("✨ **GENERATE OUTFITS**")

col1, col2, col3 = st.columns(3)
with col1:
    weather = st.selectbox("Weather:", ["Sunny", "Rainy", "Cold"])
with col2:
    mode = st.selectbox("Mode:", ["smart", "random"])
with col3:
    outfit_count = st.slider("Outfits to show:", 1, 5, 3)

# Specific item selector
specific_items = {c[0]: f"{c[2]} {c[1]}" for c in clothes_data}
if specific_items:
    col1, col2 = st.columns(2)
    with col1:
        use_specific = st.checkbox("⭐ Feature this item:")
    with col2:
        specific_item = st.selectbox("Choose:", ["None"] + list(specific_items.values()), 
                                   key="specific") if use_specific else "None"

if st.button("🎩 **GENERATE OUTFITS**", type="primary", use_container_width=True):
    specific_id = None
    if use_specific and specific_item != "None":
        # Find item ID
        for item in clothes_data:
            if f"{item[2]} {item[1]}" == specific_item:
                specific_id = item[0]
                break
    
    outfits = generate_outfits(specific_id, weather, mode, outfit_count)
    
    if outfits:
        for i, (top, bottom) in enumerate(outfits, 1):
            with st.expander(f"👗 Outfit #{i} - {top[2]} {top[1]} + {bottom[2]} {bottom[1]}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("👕 TOP")
                    img_top = Image.open(BytesIO(top[4]))
                    st.image(img_top, width=280)
                    st.caption(top[2], top[1])
                
                with col2:
                    st.subheader("👖 BOTTOM")
                    img_bottom = Image.open(BytesIO(bottom[4]))
                    st.image(img_bottom, width=280)
                    st.caption(bottom[2], bottom[1])
                
                st.success(f"⭐ Perfect for {weather}!")
    else:
        st.error("❌ Add 1 top + 1 bottom first!")

# 🔥 QUICK ADD SYSTEM
st.markdown("---")
st.subheader("👗 **Quick Add Clothes**")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📷 ADD TOP", type="secondary"):
        st.session_state.add_mode = "top"
with col2:
    if st.button("👖 ADD BOTTOM", type="secondary"):
        st.session_state.add_mode = "bottom"
with col3:
    if st.button("🎲 RANDOM GENERATOR", type="secondary"):
        st.session_state.mode_override = "random"

if st.session_state.get('add_mode'):
    st.subheader(f"📸 Add {st.session_state.add_mode.upper()}")
    img = st.camera_input("Snap your item")
    
    if img:
        image = Image.open(img)
        st.image(image, width=350)
        
        col1, col2 = st.columns(2)
        with col1:
            types = ["T-Shirt", "Shirt"] if st.session_state.add_mode == "top" else ["Pants", "Jeans"]
            user_type = st.selectbox("Type:", types)
        with col2:
            user_color = st.selectbox("Color:", ["White", "Black", "Blue", "Red", "Green", "Gray"])
        
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

# STATS
col1, col2, col3, col4 = st.columns(4)
tops = len([c for c in clothes_data if c[1] in ["T-Shirt", "Shirt"]])
bottoms = len([c for c in clothes_data if c[1] in ["Pants", "Jeans"]])

with col1: st.metric("👕 Tops", tops)
with col2: st.metric("👖 Bottoms", bottoms)
with col3: st.metric("👗 Total", len(clothes_data))
with col4: st.button("🔄 REFRESH", on_click=lambda: st.cache_data.clear() or st.rerun())
