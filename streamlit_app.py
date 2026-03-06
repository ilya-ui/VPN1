import streamlit as st
import os
import subprocess
import time

st.set_page_config(page_title="Tailscale Exit Node", page_icon="🛡️")
st.title("🛡️ Tailscale Exit Node (Manual)")

# Папки для бинарников
BIN_DIR = "./tailscale_bin"

def run_bg(cmd):
    # Запуск процесса в фоне
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if st.button("🚀 УСТАНОВИТЬ И ЗАПУСТИТЬ"):
    with st.status("Выполняю магию...", expanded=True) as status:
        # 1. Скачиваем, если папки нет
        if not os.path.exists(BIN_DIR):
            st.write("📥 Скачиваю архивы...")
            os.system("wget https://pkgs.tailscale.com/stable/tailscale_1.58.2_amd64.tgz -O ts.tgz")
            os.system("tar xzf ts.tgz")
            os.system(f"mv tailscale_1.58.2_amd64 {BIN_DIR}")
            os.system("rm ts.tgz")
        
        # 2. Запускаем демона (tailscaled)
        st.write("⚙️ Запускаю демон (Userspace)...")
        # Используем --socket, чтобы точно знать, куда стучаться
        run_bg(f"{BIN_DIR}/tailscaled --tun=userspace-networking --socks5-server=localhost:1055 &")
        
        # Даем демону 10 секунд, чтобы он создал сокет и проснулся
        time.sleep(10)
        
        # 3. Попытка авторизации
        st.write("🔗 Генерирую ссылку для входа...")
        # Команда 'up' без ключа выдаст ссылку в консоль (stderr)
        # Мы запускаем её в фоне, чтобы она не вешала сайт
        auth_process = subprocess.Popen(
            [f"{BIN_DIR}/tailscale", "up", "--advertise-exit-node", "--hostname=sok-vpn-node"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        status.update(label="✅ Команда отправлена! Ищи ссылку в логах.", state="complete")

st.markdown("""
### Что делать дальше:
1. Нажми кнопку выше.
2. Подожди 15 секунд.
3. Открой **Logs** (внизу справа: Manage app -> Logs).
4. Ищи там ссылку, начинающуюся на `https://login.tailscale.com/a/...`
5. Перейди по ней и нажми **Connect**.
6. Как только привяжешь — иди в [панель Tailscale](https://login.tailscale.com/admin/machines) и включи **Exit Node**.
""")

# Кнопка для проверки статуса (поможет понять, залогинился или нет)
if st.button("Проверить статус"):
    try:
        res = subprocess.check_output(f"{BIN_DIR}/tailscale status", shell=True, stderr=subprocess.STDOUT).decode()
        st.code(res)
    except:
        st.error("Демон еще не запущен или не авторизован.")
