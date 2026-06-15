import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import datetime
import os

# =========================
# ⚙️ SETUP
# =========================
st.set_page_config(page_title="日常點滴紀錄簿", layout="wide")

HISTORY_DIR = "history_polaroids"
os.makedirs(HISTORY_DIR, exist_ok=True)

if "page" not in st.session_state:
    st.session_state.page = "home"


# =========================
# 🎨 CSS（萬用字元暴力覆寫宋體 + 筆記本全背景 + 置底置中）
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;700&display=swap');

/* 全局背景：橫線筆記本紙 */
.stApp {
    background-color: #FFFFFF !important;
    background-image: 
        linear-gradient(rgba(173, 216, 230, 0.45) 2px, transparent 2px), 
        url('https://www.transparenttextures.com/patterns/cardboard-flat.pattern') !important;
    background-size: 100% 24px, auto !important;
    position: relative !important;
    min-height: 100vh !important;
}

/* 隱藏 header & footer */
[data-testid="stHeader"], footer {
    visibility: hidden;
    height: 0px;
}

/* 消除 Streamlit 預設留白 */
[data-testid="stMainBlockContainer"] {
    padding-top: 25px !important;
    padding-left: 25px !important;
    padding-right: 25px !important;
    padding-bottom: 90px !important; 
}

/* 萬用字元覆寫法：強制網頁上所有中文元件一律吃宋體 */
.stApp * {
    font-family: "Songti TC", "Songti SC", "STSong", "BiauKai", "PMingLiU", serif !important;
}

/* 頂部外框 */
.nav-wrapper {
    text-align: left;
    margin-bottom: 20px;
}

/* 🔥 修正：將頂部標題貼紙的字型也同步為宋體 */
.canvas-title, .canvas-title * {
    color: #A67B5B !important;
    font-size: 34px !important; /* 中文宋體改為 34px 比例最精緻 */
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    font-family: "Songti TC", "Songti SC", "STSong", "BiauKai", serif !important; /* 換成宋體 */
    display: inline-block;
    background-color: #FFFFFF !important;
    padding: 4px 16px !important;
    border-radius: 8px !important;
    box-shadow: 2px 2px 0px rgba(166, 123, 91, 0.1) !important;
}

.canvas-subtitle {
    color: #8C7365 !important;
    font-size: 16px !important;
    margin-bottom: 25px !important;
    letter-spacing: 0.5px !important;
}

/* 手繪感白色卡片 */
.polaroid-card {
    background: #FFFFFF !important;
    padding: 35px !important;
    border-radius: 16px !important;
    color: #4A4A4A !important;
    margin-bottom: 20px !important;
    box-shadow: 4px 4px 0px #A67B5B !important;
    border: 3px solid #8C7365 !important;
    position: relative !important;
}

.polaroid-card::after {
    content: '' !important;
    position: absolute !important;
    top: -12px !important;
    left: 50% !important;
    transform: translateX(-50%) rotate(-4deg) !important;
    width: 85px !important;
    height: 24px !important;
    background-color: rgba(149, 205, 122, 0.6) !important;
    border-radius: 2px !important;
}

/* 固定在螢幕正中間最底部的頁尾 */
.page-footer {
    position: absolute !important;
    bottom: 20px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    text-align: center !important;
    width: auto !important;
    white-space: nowrap !important;
    z-index: 9999 !important;
}

/* 暴力覆寫 st.segmented_control 立體方塊 */
div[data-testid="stSegmentedControl"] > div {
    background-color: transparent !important;
    border: none !important;
    gap: 14px !important;
}

div[data-testid="stSegmentedControl"] button {
    border-radius: 10px !important;
    border: 3px solid #8C7365 !important;
    background-color: #FFFFFF !important;
    color: #8C7365 !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    padding: 8px 22px !important;
    box-shadow: 4px 4px 0px #A67B5B !important;
    transition: all 0.1s ease-in-out !important;
}

div[data-testid="stSegmentedControl"] button:hover {
    background-color: #FDF7F2 !important;
}

div[data-testid="stSegmentedControl"] button[aria-checked="true"] {
    background-color: #95CD7A !important;
    color: white !important;
    border-color: #81B966 !important;
    transform: translate(3px, 3px) !important;
    box-shadow: 0px 0px 0px #A67B5B !important;
}

/* 底部的普通按鈕風格同步 */
div.stButton > button {
    border-radius: 10px !important;
    border: 3px solid #8C7365 !important;
    background-color: #FFFFFF !important;
    color: #8C7365 !important;
    padding: 10px 24px !important;
    font-weight: 700 !important;
    box-shadow: 4px 4px 0px #A67B5B !important;
    transition: all 0.1s ease !important;
}

div.stButton > button:hover {
    background-color: #FDF7F2 !important;
}

div.stButton > button:active {
    transform: translate(3px, 3px) !important;
    box-shadow: 0px 0px 0px #A67B5B !important;
}
</style>
""", unsafe_allow_html=True)


# =========================
# 📸 拍立得生成引擎（🔥 修正：照片指定 Mac 內建宋體 & 字級放大）
# =========================
def generate_polaroid(image_file, text, date_str):
    img = Image.open(image_file).convert("RGB")
    canvas = Image.new("RGB", (800, 1000), "#FEFDF5")

    w, h = img.size
    s = min(w, h)
    img = img.crop(((w-s)//2, (h-s)//2, (w+s)//2, (h+s)//2))
    img = img.resize((720, 720))

    canvas.paste(img, (40, 40))
    draw = ImageDraw.Draw(canvas)

    font_loaded = False
    
    # 🔥 核心修正：只鎖定 Mac 與 Windows 的「宋體 / 明體」系列字型路徑，移除黑體干擾
    serif_fonts = [
        "/System/Library/Fonts/STSongti-Light.ttc", # Mac 內建標準宋體
        "/System/Library/Fonts/Songti.ttc",         # Mac 備用宋體
        "/Library/Fonts/Songti.ttc",                # Mac 用戶安裝路徑
        "C:/Windows/Fonts/simsun.ttc",              # Windows 新宋體
        "C:/Windows/Fonts/mingliu.ttc"              # Windows 細明體
    ]
    
    for font_path in serif_fonts:
        if os.path.exists(font_path):
            try:
                # 順利載入後，心情文字設為 42，日期與時間放大到 28
                font1 = ImageFont.truetype(font_path, 42)
                font2 = ImageFont.truetype(font_path, 28)
                font_loaded = True
                break
            except:
                pass
                
    if not font_loaded:
        font1 = ImageFont.load_default()
        font2 = ImageFont.load_default()

    draw.text((50, 795), text or "", fill="#4A4A4A", font=font1)
    draw.text((50, 885), date_str, fill="#8C7365", font=font2)

    return canvas


# =========================
# 📦 檔案動態載入
# =========================
files = sorted(
    [f for f in os.listdir(HISTORY_DIR) if f.endswith(".jpg")],
    reverse=True
)


# =========================
# 🧭 頂部純淨標題
# =========================
st.markdown('<div class="nav-wrapper"><div class="canvas-title">日常點滴紀錄簿</div></div>', unsafe_allow_html=True)


# =========================
# 🏠 HOME 頁面
# =========================
if st.session_state.page == "home":
    st.markdown('<div class="canvas-subtitle">快門喀嚓，拼湊生活圖鑑。.</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="polaroid-card" style="text-align: center;">
        <h2 style="color: #A67B5B; font-size: 32px; margin-bottom: 5px;">The Diary</h2>
        <p style="color: #8C7365; font-size: 14px; margin-bottom: 25px;">把散落的日常碎片，裁切成一張一張的回憶。</p>
    </div>
    """, unsafe_allow_html=True)

    home_col1, home_col2 = st.columns(2)
    with home_col1:
        if st.button("上傳回億 ", key="home_to_create", use_container_width=True):
            st.session_state.page = "create"
            st.rerun()
    with home_col2:
        if st.button("開啟回憶牆 ", key="home_to_wall", use_container_width=True):
            st.session_state.page = "wall"
            st.rerun()


# =========================
# 📸 CREATE 頁面
# =========================
elif st.session_state.page == "create":
    st.markdown('<div class="polaroid-card"><h3> 上傳回億 </h3>', unsafe_allow_html=True)

    option = st.segmented_control(
        "照片來源", 
        options=["相簿上傳", "相機拍攝"], 
        default="相簿上傳",
        label_visibility="collapsed"
    )
    
    file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"]) if option == "相簿上傳" else st.camera_input("Camera")

    st.markdown('</div>', unsafe_allow_html=True)

    if file:
        st.markdown('<div class="polaroid-card">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)

        with c1:
            text = st.text_input("心情文字", placeholder="留下一句話吧...")
            date = st.date_input("日期", datetime.date.today())
            time = st.time_input("時間", datetime.datetime.now().time())

            dt = f"{date.strftime('%Y.%m.%d')} {time.strftime('%H:%M')}"
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("📌 釘上回憶", key="submit_polaroid"):
                with st.spinner("拍立得顯影中..."):
                    img = generate_polaroid(file, text, dt)
                    name = datetime.datetime.now().strftime("%Y%m%d%H%M%S.jpg")
                    path = os.path.join(HISTORY_DIR, name)
                    img.save(path)

                st.success("成功釘上回憶牆！")
                st.session_state.page = "wall"
                st.rerun()

        with c2:
            st.markdown("<p style='font-weight: 600; color: #A67B5B; margin-bottom: 8px;'>素材預覽</p>", unsafe_allow_html=True)
            st.image(file, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)


# =========================
# 🖼 WALL 頁面
# =========================
elif st.session_state.page == "wall":
    st.markdown('<div class="polaroid-card"><h3> 回憶牆 </h3>', unsafe_allow_html=True)

    if files:
        cols = st.columns(3)
        for i, f in enumerate(files):
            with cols[i % 3]:
                st.image(os.path.join(HISTORY_DIR, f), use_container_width=True)
    else:
        st.markdown('<p style="color: #8C7365;">目前牆上空空如也，快去 create 留下一點足跡！</p>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)


# =======================================================
# 📝 固定在螢幕正中間最底部的頁尾
# =======================================================
st.markdown('<div class="page-footer">', unsafe_allow_html=True)

if st.session_state.page != "home":
    if st.button("⬅ 返回首頁", key="global_back_home"):
        st.session_state.page = "home"
        st.rerun()
else:
    st.markdown('<span style="color:#A67B5B; font-size:14px; opacity:0.8; font-family:\'Fredoka\'; font-weight:700;">日常點滴紀錄簿 © 2026</span>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)