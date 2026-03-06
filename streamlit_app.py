import streamlit as st
import os
import subprocess
import time

st.set_page_config(page_title="Tailscale Exit Node", page_icon="🛡️")
st.title("🛡️ Tailscale Exit Node")

# Забираем ключ из .streamlit/secrets.toml
TS_KEY = st.secrets["TS_KEY"]

def run_cmd(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if st.button("🚀 ЗАПУСТИТЬ VPN"):
    with st.status("Развертывание Tailscale...", expanded=True) as status:
        # 1. Скачиваем бинарники (если нет)
        if not os.path.exists("tailscale_bin"):
            st.write("📥 Скачиваю файлы...")
            os.system("wget https://pkgs.tailscale.com/stable/tailscale_1.58.2_amd64.tgz")
            os.system("tar xzf tailscale_1.58.2_amd64.tgz")
            os.system("mv tailscale_1.58.2_amd64 tailscale_bin")
        
        # 2. Запускаем демон в Userspace режиме
        st.write("⚙️ Запуск tailscaled...")
        # Userspace-networking позволяет работать без прав root и модуля tun
        run_cmd("./tailscale_bin/tailscaled --tun=userspace-networking --socks5-server=localhost:1055 &")
        time.sleep(5)
        
        # 3. Подключаемся
        st.write("🔗 Авторизация в Tailnet...")
        up_cmd = f"./tailscale_bin/tailscale up --authkey={TS_KEY} --advertise-exit-node --hostname=streamlit-exit-node"
        result = os.system(up_cmd)
        
        if result == 0:
            status.update(label="✅ VPN Активен!", state="complete", expanded=False)
            st.success("Узел появился в твоей панели Tailscale!")
            st.balloons()
        else:
            status.update(label="❌ Ошибка запуска", state="error")
            st.error("Проверь логи Streamlit Cloud.")

st.info("⚠️ Теперь зайди в панель Tailscale и включи 'Edit route settings' -> 'Use as exit node' для этого устройства.")

# Чтобы процесс не убили сразу, выводим логи
if st.checkbox("Показать состояние"):
    status_output = subprocess.check_output("./tailscale_bin/tailscale status", shell=True).decode()
    st.code(status_output)
