import streamlit as st
import os
import subprocess
import time

st.set_page_config(page_title="Tailscale Exit Node", page_icon="🛡️")
st.title("🛡️ Tailscale Exit Node (Manual Login)")

def run_bg(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if st.button("🚀 ЗАПУСТИТЬ УСТАНОВКУ"):
    with st.status("Настройка сервера...", expanded=True) as status:
        # 1. Скачиваем бинарники
        if not os.path.exists("tailscale_bin"):
            st.write("📥 Скачиваю Tailscale...")
            os.system("wget https://pkgs.tailscale.com/stable/tailscale_1.58.2_amd64.tgz")
            os.system("tar xzf tailscale_1.58.2_amd64.tgz")
            os.system("mv tailscale_1.58.2_amd64 tailscale_bin")
        
        # 2. Запускаем демон
        st.write("⚙️ Запуск демона (Userspace)...")
        # Важно: запускаем в userspace режиме, так как в Streamlit нет прав root
        run_bg("./tailscale_bin/tailscaled --tun=userspace-networking --socks5-server=localhost:1055 &")
        time.sleep(5)
        
        # 3. Запускаем авторизацию
        st.write("🔗 Генерирую ссылку для входа...")
        st.warning("СМОТРИ ССЫЛКУ В ЛОГАХ STREAMLIT (кнопка 'Manage app' -> 'Logs' внизу справа)")
        
        # Запускаем команду регистрации без ключа
        # Она напечатает ссылку в стандартный вывод ошибок (stderr)
        os.system("./tailscale_bin/tailscale up --advertise-exit-node --hostname=sok-vpn-node &")
        
        status.update(label="✅ Команда отправлена! Проверь логи.", state="complete")

st.info("💡 Как это работает:\n1. Нажми кнопку выше.\n2. Открой Logs (внизу справа).\n3. Найди ссылку https://login.tailscale.com/a/...\n4. Перейди по ней и нажми Connect.")
