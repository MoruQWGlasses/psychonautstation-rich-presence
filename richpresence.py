import time
import sys
import os
import subprocess
import psutil
import requests
import ctypes
from pypresence import Presence

CLIENT_ID = '1453834311454167165' 
LARGE_IMAGE_KEY = "spacelaw"
DEFAULT_SMALL_IMAGE = "piskonat" 
BYOND_BIN_FOLDER = r"C:\Program Files (x86)\BYOND\bin"
BYOND_PAGER_PATH = os.path.join(BYOND_BIN_FOLDER, "byond.exe")
DREAMSEEKER_PATH = os.path.join(BYOND_BIN_FOLDER, "dreamseeker.exe")
SERVER_ADDRESS = "byond://play.ss13.tr:3131"
API_URL = "https://ss13.tr/api/server"
BUTTONS = [
    {"label": "Web Sitesi", "url": "https://ss13.tr"},
    {"label": "Discord Sunucusu", "url": "https://discord.gg/HpVjG6NMnU"}
]

def get_dreamseeker_pid():
    for proc in psutil.process_iter(['name', 'pid']):
        try:
            if "dreamseeker" in proc.info['name'].lower():
                return proc.info['pid']
        except:
            pass
    return None

def get_window_title_by_pid(pid):
    if not pid: return None
    try:
        user32 = ctypes.windll.user32
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        found_title = []

        def enum_windows_proc(hwnd, lParam):
            if not user32.IsWindowVisible(hwnd): return True
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                tid = ctypes.c_ulong()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(tid))
                
                if tid.value == pid:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    text = buff.value.lower()
                    
                    if "psychonaut station" not in text:
                        return True
                        
                    found_title.append(buff.value)
                    return False 
            return True

        user32.EnumWindows(WNDENUMPROC(enum_windows_proc), 0)
        return found_title[0] if found_title else None
    except:
        return None

def ensure_pager_running():
    pager_running = False
    for proc in psutil.process_iter(['name']):
        try:
            if "byond.exe" in proc.info['name'].lower():
                pager_running = True
                break
        except:
            pass

    if not pager_running:
        print("      > BYOND Pager kapalı. Otomatik giriş için açılıyor...")
        if os.path.exists(BYOND_PAGER_PATH):
            subprocess.Popen([BYOND_PAGER_PATH])
            print("      > Giriş yapılması bekleniyor (5 sn)...")
            time.sleep(5) 
        else:
            return False
    return True

def get_api_data():
    if not API_URL: return None
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(API_URL, headers=headers, timeout=3)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data[0] if len(data) > 0 else None
            return data
    except Exception:
        return None
    return None

def main():
    print("[1/4] Discord'a bağlanılıyor...")
    rpc = None
    try:
        rpc = Presence(CLIENT_ID)
        rpc.connect()
    except Exception as e:
        print(f"      > UYARI: Discord bağlantısı başarısız ({e}).")
        rpc = None

    print("[2/4] Hesap kontrolü yapılıyor...")
    if not ensure_pager_running():
        input("Devam edilemiyor. Enter'a bas...")
        return

    print(f"[3/4] Sunucuya bağlanılıyor: {SERVER_ADDRESS}")
    if os.path.exists(DREAMSEEKER_PATH):
        try:
            subprocess.Popen([DREAMSEEKER_PATH, SERVER_ADDRESS])
            print("      > Oyun başlatıldı.")
        except Exception as e:
            print(f"      > HATA: Oyun açılamadı! {e}")
            return
    else:
        print(f"      > HATA: dreamseeker.exe bulunamadı!")
        return

    print("[4/4] Durum izleme aktif...")
    
    last_round_id = None
    cached_start_timestamp = time.time()
    next_update_time = 0
    UPDATE_INTERVAL = 15

    while True:
        pid = get_dreamseeker_pid()
        if not pid:
            print("\nKapatılıyor.")
            if rpc:
                try: rpc.close()
                except: pass
            break

        if time.time() > next_update_time:
            if rpc is not None:
                try:
                    api_data = get_api_data()
                    
                    if api_data and api_data.get("err_str") == "Rebooting":
                        rpc.update(
                            details="Yeni round başlıyor.",
                            state="Sunucu Hazırlanıyor...",
                            large_image=LARGE_IMAGE_KEY,
                            large_text="Space Station 13",
                            small_image=DEFAULT_SMALL_IMAGE,
                            buttons=BUTTONS
                        )
                        next_update_time = time.time() + UPDATE_INTERVAL
                        continue

                    window_title = get_window_title_by_pid(pid)
                    station_name_from_window = None
                    
                    if window_title:
                        if ":" in window_title:
                            station_name_from_window = window_title.split(":", 1)[-1].strip()
                        elif " - " in window_title:
                            station_name_from_window = window_title.split(" - ")[-1].strip()
                        else:
                            station_name_from_window = window_title.replace("Psychonaut Station", "").strip()

                    if api_data:
                        oyuncu = api_data.get("players", 0)
                        api_map_name = api_data.get("map", "Map")
                        round_id = api_data.get("round_id", "?")
                        sec_level = api_data.get("security_level", "unknown")
                        
                        if station_name_from_window:
                            if station_name_from_window.lower().endswith("istasyonu"):
                                details_text = station_name_from_window
                            else:
                                details_text = f"{station_name_from_window} İstasyonu"
                        else:
                            details_text = "Bağlantı Bekleniyor..."

                        state_text = f"{oyuncu} Oyuncu | #{round_id} | {api_map_name}"
                        large_text_hover = f"Harita: {api_map_name}"

                        if sec_level in ['green', 'blue', 'red', 'delta']:
                            current_small_image = f"aalert_{sec_level}"
                            current_small_text = f"Alarm: {sec_level.upper()}"
                        else:
                            current_small_image = DEFAULT_SMALL_IMAGE
                            current_small_text = "Yeni round bekleniyor."
                        round_duration = int(api_data.get("round_duration", 0))
                        calculated_start = time.time() - round_duration
                        
                        if str(round_id) != str(last_round_id):
                            last_round_id = str(round_id)
                            cached_start_timestamp = calculated_start
                        else:
                            if round_duration > 0:
                                cached_start_timestamp = min(cached_start_timestamp, calculated_start)
                            
                            drift = calculated_start - cached_start_timestamp
                            if drift > 90:
                                cached_start_timestamp = calculated_start

                        rpc.update(
                            details=details_text[:128],
                            state=state_text[:128],
                            large_image=LARGE_IMAGE_KEY,
                            large_text=large_text_hover[:128],
                            small_image=current_small_image,
                            small_text=current_small_text[:128],
                            start=cached_start_timestamp,
                            buttons=BUTTONS
                        )
                    else:
                        fallback = station_name_from_window if station_name_from_window else "Bağlantı Bekleniyor..."
                        rpc.update(
                            details=fallback[:128],
                            state="Space Station 13",
                            large_image=LARGE_IMAGE_KEY,
                            small_image=DEFAULT_SMALL_IMAGE,
                            start=time.time(),
                            buttons=BUTTONS
                        )
                except Exception:
                    try: rpc.close() 
                    except: pass
                    rpc = None
            
            next_update_time = time.time() + UPDATE_INTERVAL

        time.sleep(1)

if __name__ == "__main__":
    main()