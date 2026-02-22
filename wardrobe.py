import streamlit as st
from PIL import Image
import sqlite3
import os
import base64
from io import BytesIO

# Database setup
@st.cache_resource
def init_db():
    conn = sqlite3.connect('wardrobe.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clothes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  type TEXT, color TEXT, season TEXT, 
                  image_data BLOB)''')
    conn.commit()
    return conn

conn = init_db()

st.set_page_config(page_title="Wardrobe Wizard", layout="wide")
st.title("🧥 Wardrobe Wizard")
st.markdown("### Snap your clothes → Get perfect outfits instantly!")

# Sidebar filters
st.sidebar.header("Filters")
outfit_type = st.sidebar.selectbox("Outfit type:", ["Work", "Casual", "Party", "Gym"])
weather = st.sidebar.selectbox("Weather:", ["Sunny", "Rainy", "Cold"])

# Tab 1: Add clothes
tab1, tab2 = st.tabs(["➕ Add Clothes", "🎩 Get Outfit"])

with tab1:
    st.subheader("📸 Add new clothing item")
    uploaded_file = st.file_uploader("Choose image", type=['png','jpg','jpeg'])
    
    col1, col2 = st.columns([3,1])
    with col1:
        cloth_type = st.selectbox("Type:", ["Shirt", "T-Shirt", "Pants", "Jeans", "Shoes", "Jacket"])
        color = st.text_input("Color (e.g., Blue, Black):")
        season = st.selectbox("Season:", ["Summer", "Winter", "All"])
    
    if uploaded_file is not None and color:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded", width=200)
        
        # Convert to binary for DB
        img_buffer = BytesIO()
        image.save(img_buffer, format='PNG')
        img_data = img_buffer.getvalue()
        
        if st.button("✅ Save to Wardrobe", key="save"):
            conn.execute("INSERT INTO clothes (type, color, season, image_data) VALUES (?, ?, ?, ?)",
                        (cloth_type, color, season, img_data))
            conn.commit()
            st.success("🎉 Added to wardrobe!")
            st.rerun()

with tab2:
    st.subheader("✨ Generate Perfect Outfit")
    
    if st.button("🎲 Get Random Outfit", type="primary"):
        # Filter clothes based on selections
        query = "SELECT * FROM clothes WHERE season=? OR season='All'"
        clothes = conn.execute(query, (weather,)).fetchall()
        
        # Separate by type
        tops = [c for c in clothes if c[1] in ["Shirt", "T-Shirt"]]
        bottoms = [c for c in clothes if c[1] in ["Pants", "Jeans"]]
        shoes = [c for c in clothes if c[1] == "Shoes"]
        
        if tops and bottoms:
            top = random.choice(tops)
            bottom = random.choice(bottoms)
            shoe = shoes[0] if shoes else None
            
            # Display outfit
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("👕 Top")
                img_top = Image.open(BytesIO(top[4]))
                st.image(img_top, width=150)
                st.write(f"*{top[2]} {top[1]}*")
            
            with col2:
                st.subheader("👖 Bottom")
                img_bottom = Image.open(BytesIO(bottom[4]))
                st.image(img_bottom, width=150)
                st.write(f"*{bottom[2]} {bottom[1]}*")
            
            with col3:
                if shoe:
                    st.subheader("👟 Shoes")
                    img_shoe = Image.open(BytesIO(shoe[4]))
                    st.image(img_shoe, width=100)
                    st.write(f"*{shoe[2]} {shoe[1]}*")
            
            st.success("👌 Perfect for your vibe!")
            
            # Share button
            st.markdown("---")
            st.subheader("📱 Share your look!")
            st.info("Screenshot this → Post on Instagram Stories!")
        else:
            st.warning("👕 Add some shirts/pants first!")

# Show wardrobe stats
stats_col1, stats_col2 = st.columns(2)
with stats_col1:
    total = conn.execute("SELECT COUNT(*) FROM clothes").fetchone()[0]
    st.metric("Total Items", total)
with stats_col2:
    unique_colors = len(conn.execute("SELECT DISTINCT color FROM clothes").fetchall())
    st.metric("Colors", unique_colors)
