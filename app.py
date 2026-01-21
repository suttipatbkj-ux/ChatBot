import os
import google.generativeai as genai
from pypdf import PdfReader
import streamlit as st
from prompt import PROMPT_WORKAW
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import dotenv

# โหลด Environment Variables
dotenv.load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# ตั้งค่า API Key
if not GOOGLE_API_KEY:
    st.error("ไม่พบ GOOGLE_API_KEY ในไฟล์ .env")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# ตั้งค่าการตอบ
generation_config = {
    "temperature": 0.0, 
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 2048,
    "response_mime_type": "text/plain",
}

SAFETY_SETTINGS = {
     HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
     HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
     HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
     HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
}

# --- ส่วนอ่านไฟล์ PDF ---
pdf_filename = "Graphic.pdf" 
pdf_content = ""

try:
    if os.path.exists(pdf_filename):
        reader = PdfReader(pdf_filename)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pdf_content += text + "\n"
        print(f"✅ อ่านไฟล์สำเร็จ! ความยาวตัวอักษร: {len(pdf_content)} ตัว")
    else:
        st.error(f"❌ ไม่พบไฟล์ {pdf_filename}")
except Exception as e:
    st.error(f"❌ เกิดข้อผิดพลาดในการอ่านไฟล์ PDF: {e}")

# --- รวม Prompt ---
FULL_SYSTEM_INSTRUCTION = f"""
{PROMPT_WORKAW}

----------------------------------------
CONTEXT / KNOWLEDGE BASE:
{pdf_content}
----------------------------------------
"""

# สร้าง Model (ใช้ gemini-1.5-flash เป็นรุ่นหลักที่รองรับ System Instruction ได้ดี)
try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", 
        safety_settings=SAFETY_SETTINGS,
        generation_config=generation_config,
        system_instruction=FULL_SYSTEM_INSTRUCTION 
    )
except:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        safety_settings=SAFETY_SETTINGS,
        generation_config=generation_config,
    )

# --- 🔥 ส่วนตกแต่งแนว "ยอดนักสืบจิ๋วโคนัน" (Detective Conan Theme CSS) 🔥 ---
conan_style = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;700&display=swap');

/* พื้นหลังสีน้ำเงินเข้มแบบ Detective Blue */
[data-testid="stAppViewContainer"] {
    font-family: 'Kanit', sans-serif;
    background: linear-gradient(180deg, #002147 0%, #003366 50%, #004080 100%);
    color: white;
}

/* ปรับแต่งหัวข้อ */
h1 {
    color: #FFD700 !important; /* สีทองเหมือนตราตำรวจ */
    text-shadow: 2px 2px 4px #000;
    font-weight: 800 !important;
    text-align: center;
}

/* กล่องข้อความ User (สีขาวขอบน้ำเงิน) */
[data-testid="stChatMessage"]:nth-child(even) {
    background-color: #ffffff !important;
    color: #000 !important;
    border: 2px solid #002147 !important;
    border-radius: 15px !important;
}

/* กล่องข้อความ Bot (สีแดงหูกระต่าย) */
[data-testid="stChatMessage"]:nth-child(odd) {
    background-color: #C41E3A !important; /* Red Bow Tie */
    color: white !important;
    border: 2px solid #ffffff !important;
    border-radius: 15px !important;
}

/* แถบ Sidebar */
[data-testid="stSidebar"] {
    background-color: #001529 !important;
}

/* ปุ่มกดสีเหลือง/ทอง */
.stButton>button {
    background-color: #FFD700 !important;
    color: #000 !important;
    font-weight: bold !important;
    border-radius: 10px !important;
    border: 2px solid #000 !important;
}

/* ช่องพิมพ์แชท */
.stChatInput textarea {
    border: 2px solid #FFD700 !important;
}
</style>
"""
st.markdown(conan_style, unsafe_allow_html=True)

# --- User Interface ---
def clear_history():
    st.session_state["messages"] = [
        {"role": "model", "content": "ความจริงมีเพียงหนึ่งเดียวเท่านั้น! น้อง Graphic Bot (โหมดนักสืบ) พร้อมช่วยไขปริศนากราฟิกแล้วครับ 🔍⚽"}
    ]
    st.rerun()

with st.sidebar:
    st.markdown("### 🔍 Detective Menu")
    if st.button("🗑️ ล้างประวัติการไขคดี"):
        clear_history()

st.title("🕵️‍♂️ Detective Graphic Bot 🔍")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "model", "content": "ความจริงมีเพียงหนึ่งเดียวเท่านั้น! น้อง Graphic Bot (โหมดนักสืบ) พร้อมช่วยไขปริศนากราฟิกแล้วครับ 🔍⚽"}
    ]

# แสดงประวัติ (ปรับ Icon เป็นแว่นขยายและรอยเท้า)
for msg in st.session_state["messages"]:
    avatar_icon = "🕵️" if msg["role"] == "user" else "🔍"
    st.chat_message(msg["role"], avatar=avatar_icon).write(msg["content"])

# รับ Input
if prompt := st.chat_input("ใส่เบาะแสคำถามที่นี่..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="🕵️").write(prompt)

    def generate_response():
        history_api = [
            {"role": msg["role"], "parts": [{"text": msg["content"]}]}
            for msg in st.session_state["messages"]
        ]

        try:
            chat_session = model.start_chat(history=history_api)
            
            # บังคับคำสั่งแนบท้าย (Suffix Prompting)
            strict_prompt = f"""
            {prompt}
            
            (IMPORTANT COMMAND FOR AI: 
            1. Answer purely based on the provided CONTEXT above.
            2. If the answer is NOT in the CONTEXT, you MUST say "ขออภัยค่ะ ผมไม่พบเบาะแสเรื่องนี้ในเอกสารครับ 🕵️‍♂️"
            3. DO NOT use outside knowledge to answer.)
            """
            
            response = chat_session.send_message(strict_prompt)
            
            st.session_state["messages"].append({"role": "model", "content": response.text})
            st.chat_message("model", avatar="🔍").write(response.text)

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการไขคดี: {e}")

    generate_response()