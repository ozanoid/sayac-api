import streamlit as st
from flask import Flask, jsonify
import time
from threading import Thread
import requests
from streamlit_server_state import server_state, server_state_lock

app = Flask(__name__)

def count_to_65():
    with server_state_lock["count_result"]:
        server_state["count_result"] = None
    time.sleep(65)
    with server_state_lock["count_result"]:
        server_state["count_result"] = {"status": "success", "message": "65 saniye sayma işlemi başarıyla tamamlandı."}

@app.route('/count', methods=['GET'])
def start_count():
    thread = Thread(target=count_to_65)
    thread.start()
    return jsonify({"status": "started", "message": "Sayaç başlatıldı. 65 saniye sonra tamamlanacak."})

@app.route('/result', methods=['GET'])
def get_result():
    with server_state_lock["count_result"]:
        result = server_state.get("count_result")
    if result is None:
        return jsonify({"status": "in_progress", "message": "Sayma işlemi henüz tamamlanmadı."})
    return jsonify(result)

def run_flask():
    app.run(port=5000)

if __name__ == '__main__':
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    st.title("65 Saniye Sayaç API")

    if st.button("Sayacı Başlat"):
        response = requests.get("http://localhost:5000/count")
        st.json(response.json())

    if st.button("Sonucu Kontrol Et"):
        response = requests.get("http://localhost:5000/result")
        st.json(response.json())

    st.write("API Endpoint'leri:")
    st.code("Sayacı başlatmak için: http://localhost:5000/count")
    st.code("Sonucu kontrol etmek için: http://localhost:5000/result")