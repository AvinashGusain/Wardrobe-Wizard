import streamlit as st
from PIL import Image
import sqlite3
import io
import random

st.set_page_config(page_title="Wardrobe Wizard", layout="wide")
from io import BytesIO

st.title("🧥 Wardrobe Wizard")
st.markdown("### Snap your clothes → Get perfect outfits instantly!")

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
tab1, tab2 = st.tabs(["📷 Add Clothes", "🎩 Get Outfit"])

with tab1:
    st.subheader("🎥 Capture or Upload Clothes")
    
    # BUTTON-CONTROLLED SECTIONS
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📷 Open Camera", type="secondary"):
            st.session_state.camera_mode = True
        if st.button("📁 Upload File", type="secondary"):
            st.session_state.camera_mode = False
    
    # CAMERA SECTION (Button activated)
    if st.session_state.get('camera_mode', False):
        st.subheader("🎥 Camera Active")
        camera_img = st.camera_input("Point at clothing & click camera icon ⬇️")
        
        if camera_img:
            image = Image.open(camera_img)
            st.image(image, caption="✅ Photo captured!", width=300)
            
            col_type, col_color = st.columns(2)
            with col_type:
                cloth_type = st.selectbox("Type:", ["Shirt", "T-Shirt", "Pants", "Jeans", "Shoes", "Jacket"])
            with col_color:
                color = st.text_input("Color:")
            
            # 🔥 NEW SUGGESTIONS BUTTON
            if st.button("✨ Get Suggestions for This Item", type="primary"):
                st.subheader("🤖 AI Suggestions:")
                st.success(f"✅ Perfect for: **{random.choice(['Work', 'Casual', 'Gym'])}** outfits")
                st.info(f"💡 Pairs well with: **{random.choice(['Jeans', 'Chinos', 'Sneakers'])}**")
            
            if color and st.button("✅ Save to Wardrobe"):
                img_buffer = BytesIO()
                image.save(img_buffer, format='PNG')
                img_data = img_buffer.getvalue()
                
                conn = sqlite3.connect('wardrobe.db')
                conn.execute("INSERT INTO clothes (type, color, season, image_data) VALUES (?, ?, ?, ?)",
                            (cloth_type, color, weather, img_data))
                conn.commit()
                conn.close()
                
                st.success("🎉 Saved!")
                st.cache_data.clear()
                st.rerun()
    
    # UPLOAD SECTION (Button activated)
    else:
        st.subheader("📁 File Upload")
        uploaded_file = st.file_uploader("Choose image", type=['png','jpg','jpeg'])
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="✅ Photo loaded!", width=300)
            
            col_type, col_color = st.columns(2)
            with col_type:
                cloth_type = st.selectbox("Type:", ["Shirt", "T-Shirt", "Pants", "Jeans", "Shoes", "Jacket"])
            with col_color:
                color = st.text_input("Color:")
            
            # 🔥 SUGGESTIONS BUTTON
            if st.button("✨ Get Suggestions for This Item", type="primary"):
                st.subheader("🤖 AI Suggestions:")
                st.success(f"✅ Perfect for: **{random.choice(['Work', 'Casual', 'Gym'])}** outfits")
                st.info(f"💡 Pairs well with: **{random.choice(['Jeans', 'Chinos', 'Sneakers'])}**")
            
            if color and st.button("✅ Save to Wardrobe"):
                img_buffer = BytesIO()
                image.save(img_buffer, format='PNG')
                img_data = img_buffer.getvalue()
                
                conn = sqlite3.connect('wardrobe.db')
                conn.execute("INSERT INTO clothes (type, color, season, image_data) VALUES (?, ?, ?, ?)",
                            (cloth_type, color, weather, img_data))
                conn.commit()
                conn.close()
                
                st.success("🎉 Saved!")
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
        else:
            st.warning("👕 Add shirts AND pants first!")

# Stats
total = len(clothes_data)
st.metric("Total Items", total)
if st.button("🔄 Refresh"):
    st.cache_data.clear()
    st.rerun()
