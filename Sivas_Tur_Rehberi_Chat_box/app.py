import streamlit as st
import requests
import uuid
import concurrent.futures

BASE_URL = "http://localhost:8000"
CHAT_URL = f"{BASE_URL}/chat"
SEARCH_URL = f"{BASE_URL}/web_search"

st.set_page_config(
    page_title="SİVAS ŞEHİR TANITIM REHBERİ",
    layout="wide"
)

st.title("🏛️ SİVAS ŞEHİR TANITIM REHBERİ")
st.caption("Selçuklu'nun kalbinden Cumhuriyet'in merkezine; Sivas'ı keşfedin. 🕌📜")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

def fetch_data(url, payload):
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()["answer"]
        else:
            return f"⚠️ Hata: {response.status_code}"
    except Exception as e:
        return f"⚠️ Bağlantı hatası: {str(e)}"

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

st.write("---")
col_opt1, col_opt2 = st.columns([2, 3])

with col_opt1:
    search_mode = st.selectbox(
        "Yanıt Modunu Seçiniz:",
        options=["✨ Her İkisi (Hibrit)", "🧠 Akıllı Asistan", "🌐 Web Search"],
        index=0
    )

user_input = st.chat_input("Sivas hakkında bir soru sorun...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    payload = {"session_id": st.session_state.session_id, "message": user_input}

    if search_mode == "✨ Her İkisi (Hibrit)":
        
        with st.chat_message("assistant"):
            st.write("Cevaplar hazırlanıyor...")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("🧠 **Akıllı Asistan**")
                ai_container = st.empty()
                with ai_container:
                    with st.spinner("Düşünüyor..."):
                        pass
            
            with col2:
                st.success("🌐 **Web Arama (Google)**")
                web_container = st.empty()
                with web_container:
                    with st.spinner("Aranıyor..."):
                        pass

            ai_result = ""
            web_result = ""
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_ai = executor.submit(fetch_data, CHAT_URL, payload)
                future_web = executor.submit(fetch_data, SEARCH_URL, payload)
                
                future_map = {future_ai: "ai", future_web: "web"}
                
                for future in concurrent.futures.as_completed(future_map):
                    task_type = future_map[future]
                    result = future.result()
                    
                    if task_type == "ai":
                        ai_result = result
                        ai_container.markdown(result)
                    elif task_type == "web":
                        web_result = result
                        web_container.markdown(result)
            
            combined_msg = f"""
            **🧠 Asistan:** {ai_result}
            
            ---
            **🌐 Web:** {web_result}
            """
            st.session_state.messages.append({"role": "assistant", "content": combined_msg})

    else:
        if search_mode == "🌐 Web Search":
            target_url = SEARCH_URL
            spinner_text = "🌐 Web üzerinde araştırma yapılıyor..."
        else:
            target_url = CHAT_URL
            spinner_text = "🧠 Asistan düşünüyor..."

        with st.chat_message("assistant"):
            with st.spinner(spinner_text):
                answer = fetch_data(target_url, payload)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})