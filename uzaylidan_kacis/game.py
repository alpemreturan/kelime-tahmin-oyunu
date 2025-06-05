import tkinter as tk
from tkinter import font
import random
import datetime
import pygame
import os 
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SCORE_FILE = os.path.join(BASE_DIR, "scores.txt")
SOUND_FILES = {
    "correct": os.path.join(BASE_DIR, "correct.mp3"),
    "wrong": os.path.join(BASE_DIR, "wrong.mp3"),
    "win": os.path.join(BASE_DIR, "win.mp3"),
    "lose": os.path.join(BASE_DIR, "lose.mp3")
}
icon_path = os.path.join(BASE_DIR, "icon.ico")

pygame.mixer.init()  # Pygame ses modülünü başlat

# --- Oyun Ayarları ---
SCI_FI_PHRASES = [
    "uzay gemisi", "lazer tabancasi", "zaman makinesi", "galaksi kesfi", 
    "robot ordusu", "kara delik", "yildizlararasi yolculuk", 
    "teleportasyon cihazi", "enerji kalkani", "plazma tüfegi", 
    "solucan deligi", "android isyani", "uzay istasyonu", 
    "terraforming", "hiperuzay sicramasi", "bilinc aktarimi", 
    "kuantum bilgisayar", "genetik modifikasyon", "siberpunk gelecek", 
    "distopik toplum", "ay kolonisi", "mars yolculugu", "yapay zeka"
]
TRAP_LETTERS = ['x', 'z', 'j', 'q']
MAX_PENALTY_POINTS = 6  # Maksimum 6 hata hakkı (0'dan 6'ya kadar, 6'da kaybeder)
GUESS_TIME_SECONDS = 20 # Her tahmin için süre

ALIEN_STAGES = [
    "👽----------🛸",  # 0 ceza puanı
    "👽---------🛸",   # 1 ceza puanı
    "👽--------🛸",    # 2 ceza puanı
    "👽-------🛸",     # 3 ceza puanı
    "👽------🛸",      # 4 ceza puanı
    "👽-----🛸",       # 5 ceza puanı
    "👽----🛸",        # 6 ceza puanı (Yakalandın!)
    # Daha fazla ilerleme için ek aşamalar eklenebilir, ancak 6 puanda oyun biter.
    # Bu yüzden 6. indeksteki (7. aşama) yeterli.
]
# MAX_PENALTY_POINTS'a göre ALIEN_STAGES'ı dinamik olarak ayarlayalım
# Eğer MAX_PENALTY_POINTS 6 ise, 7 aşama olmalı (0'dan 6'ya)
ALIEN_STAGES_DYNAMIC = ["👽" + "-" * (MAX_PENALTY_POINTS - i) + "🛸" for i in range(MAX_PENALTY_POINTS)]
ALIEN_STAGES_DYNAMIC.append("👽" + "🛸") # Yakalanma durumu
if len(ALIEN_STAGES_DYNAMIC) != MAX_PENALTY_POINTS + 1: # Kontrol
    print("ALIEN_STAGES_DYNAMIC boyutu MAX_PENALTY_POINTS ile uyumlu değil. Varsayılan kullanılıyor.")
else:
    ALIEN_STAGES = ALIEN_STAGES_DYNAMIC

# --- Global Oyun Değişkenleri ---
current_phrase = ""
hidden_phrase_display = ""
guessed_letters = set()
penalty_points = 0
game_timer_id = None
game_active = False
hint_used_this_game = False
game_start_time = None

def play_sound_async(sound_key):
    """Belirtilen ses dosyasını pygame ile çalar (threading yok)."""
    if sound_key in SOUND_FILES:
        sound_file = SOUND_FILES[sound_key]
        try:
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Ses çalınamadı: {e}")

# --- GUI Güncelleme Fonksiyonları ---
def update_phrase_label():
    """Şifreli kelime etiketini günceller."""
    global hidden_phrase_display
    displayed_text = []
    for char_original in current_phrase:
        char = char_original.lower()
        if char == ' ':
            displayed_text.append(' ') # Boşlukları doğrudan göster
        elif char in guessed_letters:
            displayed_text.append(char_original) # Tahmin edilen harfi orijinal haliyle göster
        else:
            displayed_text.append('_')
    hidden_phrase_display = " ".join(displayed_text)
    phrase_label.config(text=hidden_phrase_display)

def update_alien_label():
    """Uzaylı ilerleme etiketini günceller."""
    stage_index = min(penalty_points, MAX_PENALTY_POINTS) # En fazla son aşamayı göster
    alien_label.config(text=ALIEN_STAGES[stage_index])

def update_penalty_label():
    """Kalan hata hakkı (ceza puanı) etiketini günceller."""
    # Kalan hak = Maksimum hak - Mevcut ceza puanı
    # Ancak oyun "Maksimum 6 hata hakkı vardır" diyor, bu da 6. hatada oyun biter demek.
    # Bu yüzden doğrudan ceza puanını veya ilerlemeyi göstermek daha mantıklı olabilir.
    # Şimdilik ceza puanını gösterelim:
    penalty_display_label.config(text=f"Ceza Puanı: {penalty_points}/{MAX_PENALTY_POINTS}")

def update_timer_label(seconds_left):
    """Süre sayacı etiketini günceller."""
    timer_label.config(text=f"Süre: {seconds_left}sn")

def update_status_label(message, color="black"):
    """Durum mesajı etiketini günceller."""
    status_label.config(text=message, fg=color)

# --- Zamanlayıcı Fonksiyonları ---
def countdown():
    """Geri sayım yapar ve süresi dolduğunda işlemi tetikler."""
    global game_timer_id, penalty_points, game_active
    
    current_time = int(timer_label.cget("text").split(" ")[1][:-2]) # "Süre: 20sn" -> 20
    current_time -= 1
    update_timer_label(current_time)

    if current_time > 0:
        game_timer_id = root.after(1000, countdown)
    else: # Süre doldu
        if game_active: # Oyun hala aktifse (kazanma/kaybetme durumu oluşmadıysa)
            update_status_label("Süre Doldu! Yanlış tahmin.", "red")
            play_sound_async("wrong")
            penalty_points += 1
            update_penalty_label()
            update_alien_label()
            check_game_over_conditions()
            if game_active: # Hala bitmediyse yeni tahmin için sayacı başlat
                 start_guess_timer()


def start_guess_timer():
    """Tahmin için zamanlayıcıyı başlatır veya sıfırlar."""
    global game_timer_id
    if game_timer_id:
        root.after_cancel(game_timer_id)
    update_timer_label(GUESS_TIME_SECONDS)
    game_timer_id = root.after(1000, countdown)

# --- Oyun Mantığı Fonksiyonları ---
def select_new_phrase():
    """Listeden rastgele yeni bir şifreli kelime seçer."""
    global current_phrase
    current_phrase = random.choice(SCI_FI_PHRASES)
    # print(f"Seçilen Şifre (Test için): {current_phrase}") # Test için

def start_new_game():
    """Yeni bir oyunu başlatır veya mevcut oyunu sıfırlar."""
    global penalty_points, guessed_letters, game_active, hint_used_this_game, game_start_time
    
    game_active = True
    penalty_points = 0
    guessed_letters = set()
    hint_used_this_game = False
    game_start_time = datetime.datetime.now()

    select_new_phrase()
    update_phrase_label()
    update_alien_label()
    update_penalty_label()
    update_status_label("Yeni oyun başladı. Bir harf tahmin edin!", "blue")
    
    guess_entry.config(state=tk.NORMAL)
    guess_entry.delete(0, tk.END)
    guess_entry.focus()
    
    guess_button.config(text="Tahmin Et", command=process_guess, state=tk.NORMAL)
    hint_button.config(state=tk.NORMAL)
    
    start_guess_timer()

def process_guess(event=None): # event=None Enter tuşu için
    """Kullanıcının harf tahminini işler."""
    global penalty_points, game_active

    if not game_active:
        return

    guess = guess_entry.get().lower()
    guess_entry.delete(0, tk.END)

    if not guess.isalpha() or len(guess) != 1:
        update_status_label("Lütfen geçerli tek bir harf girin.", "orange")
        return

    if guess in guessed_letters:
        update_status_label(f"'{guess}' harfini zaten tahmin ettiniz.", "orange")
        # Tekrar eden tahmin için süre sıfırlanabilir veya devam edebilir. Şimdilik devam etsin.
        # start_guess_timer() # İsteğe bağlı: tekrar eden tahmin için süreyi yeniden başlat
        return

    guessed_letters.add(guess)
    
    # Tahmin yapıldığı için mevcut sayacı durdur
    if game_timer_id:
        root.after_cancel(game_timer_id)

    if guess in TRAP_LETTERS:
        update_status_label(f"'{guess}' bir tuzak harf! Uzaylı 2 adım ilerledi.", "red")
        play_sound_async("wrong")
        penalty_points += 2
    elif guess in current_phrase.lower():
        update_status_label(f"'{guess}' harfi doğru!", "green")
        play_sound_async("correct")
        # Ceza puanı artmaz
    else:
        update_status_label(f"'{guess}' harfi yanlış.", "red")
        play_sound_async("wrong")
        penalty_points += 1

    update_phrase_label()
    update_penalty_label()
    update_alien_label()
    
    check_game_over_conditions()
    
    if game_active: # Oyun hala devam ediyorsa yeni tahmin için sayacı başlat
        start_guess_timer()


def give_hint():
    """Kullanıcıya ipucu verir."""
    global penalty_points, hint_used_this_game, game_active

    if not game_active or hint_used_this_game:
        if hint_used_this_game:
            update_status_label("Bu oyunda ipucunu zaten kullandınız.", "orange")
        return

    hint_used_this_game = True
    penalty_points += 1 # İpucu kullanmanın cezası 1 hata
    
    first_letter_of_phrase = ""
    for char_original in current_phrase: # Orijinal büyük/küçük harfi koru
        char_lower = char_original.lower()
        if char_lower.isalpha() and char_lower not in guessed_letters:
            first_letter_of_phrase = char_original # İlk *tahmin edilmemiş* harfi al
            guessed_letters.add(char_lower) # İpucu verilen harfi tahmin edilmişlere ekle
            break
    
    if not first_letter_of_phrase: # Tüm harfler zaten tahmin edilmişse (çok olası değil ama kontrol)
        # Veya tüm harfler zaten biliniyorsa (örneğin tek harfli kelime ve ipucu)
        # Bu durumda ipucu etkisiz kalır ama cezası uygulanır.
        # Alternatif olarak, ipucu verilemiyorsa ceza uygulanmayabilir.
        # Şimdilik, ipucu istendiği için ceza her zaman uygulansın.
        update_status_label("İpucu kullanıldı ancak tüm harfler zaten açık!", "orange")
    else:
         update_status_label(f"İpucu: Bir harf '{first_letter_of_phrase}'. Uzaylı 1 adım ilerledi.", "blue")


    play_sound_async("wrong") # İpucu bir tür "yanlış" olarak değerlendirilebilir (ceza puanı açısından)
    
    update_phrase_label()
    update_penalty_label()
    update_alien_label()
    hint_button.config(state=tk.DISABLED) # İpucu butonunu devre dışı bırak
    
    check_game_over_conditions()
    
    if game_active: # Oyun hala devam ediyorsa (ipucu sonrası bitmediyse)
        # İpucu sonrası süre sıfırlanmalı mı? Genellikle evet.
        start_guess_timer()


def check_game_over_conditions():
    """Oyunun kazanma veya kaybetme durumunu kontrol eder."""
    global game_active
    if not game_active: return

    # Kazanma durumu: Şifredeki tüm harfler tahmin edildi mi?
    # (Boşluklar hariç)
    all_letters_guessed = True
    for char_original in current_phrase:
        char = char_original.lower()
        if char.isalpha() and char not in guessed_letters:
            all_letters_guessed = False
            break
    
    if all_letters_guessed:
        game_active = False
        play_sound_async("win")
        duration = (datetime.datetime.now() - game_start_time).total_seconds()
        update_status_label(f"TEBRİKLER! Kazandınız! Süre: {duration:.0f}sn", "green")
        record_score("KAZANDI", duration)
        end_game_ui_setup()
        return True # Oyun bitti

    # Kaybetme durumu: Ceza puanı maksimuma ulaştı mı?
    if penalty_points >= MAX_PENALTY_POINTS:
        game_active = False
        play_sound_async("lose")
        duration = (datetime.datetime.now() - game_start_time).total_seconds()
        update_status_label(f"OYUN BİTTİ! Uzaylıya yakalandın. Şifre: {current_phrase}", "red")
        record_score("KAYBETTİ", duration)
        end_game_ui_setup()
        return True # Oyun bitti
    
    return False # Oyun devam ediyor

def end_game_ui_setup():
    """Oyun bittiğinde GUI elemanlarını ayarlar."""
    if game_timer_id:
        root.after_cancel(game_timer_id)
    guess_entry.config(state=tk.DISABLED)
    hint_button.config(state=tk.DISABLED)
    guess_button.config(text="Yeni Oyun", command=start_new_game, state=tk.NORMAL)


def record_score(status, duration_seconds):
    try:
        with open(SCORE_FILE, "a", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            f.write(f"{timestamp} | {status} | {current_phrase} | {duration_seconds:.0f} saniye\n")
    except Exception as e:
        print("Skor dosyasına yazılamadı!", e)
        update_status_label("Skor dosyasına yazılamadı!", "red")


# --- GUI Kurulumu ---
root = tk.Tk()
root.title("Uzaylıdan Kaçış Oyunu")
root.geometry("900x600") # Pencere boyutunu biraz büyüttük
root.resizable(False, False)
root.iconbitmap(icon_path)  # İkon dosyasını ayarla

# Fontlar
title_font = font.Font(family="Helvetica", size=20, weight="bold")
label_font = font.Font(family="Arial", size=14)
status_font = font.Font(family="Arial", size=12)
alien_font = font.Font(family="Courier New", size=18, weight="bold") # Uzaylı için farklı font

# Ana Çerçeve
main_frame = tk.Frame(root, padx=20, pady=20)
main_frame.pack(expand=True, fill=tk.BOTH)

# Başlık
game_title_label = tk.Label(main_frame, text="Uzaylıdan Kaçış!", font=title_font, fg="navy")
game_title_label.pack(pady=(0, 20))

# Şifreli Kelime Etiketi
phrase_label = tk.Label(main_frame, text="_ _ _", font=font.Font(family="Consolas", size=24, weight="bold"), pady=10)
phrase_label.pack()

# Zamanlayıcı Etiketi
timer_label = tk.Label(main_frame, text=f"Süre: {GUESS_TIME_SECONDS}sn", font=label_font, fg="purple")
timer_label.pack(pady=5)

# Giriş Alanı ve Buton Çerçevesi
input_frame = tk.Frame(main_frame)
input_frame.pack(pady=10)

guess_entry_label = tk.Label(input_frame, text="Harf Girin:", font=label_font)
guess_entry_label.pack(side=tk.LEFT, padx=(0,5))

guess_entry = tk.Entry(input_frame, width=5, font=label_font, justify=tk.CENTER)
guess_entry.pack(side=tk.LEFT, padx=5)
guess_entry.bind("<Return>", process_guess) # Enter tuşuna basıldığında tahmin et

guess_button = tk.Button(input_frame, text="Tahmin Et", font=label_font, command=process_guess, bg="lightblue", relief=tk.RAISED)
guess_button.pack(side=tk.LEFT, padx=5)

hint_button = tk.Button(input_frame, text="İpucu", font=label_font, command=give_hint, bg="lightyellow", relief=tk.RAISED)
hint_button.pack(side=tk.LEFT, padx=5)

# Uzaylı İlerleme Etiketi
alien_label = tk.Label(main_frame, text=ALIEN_STAGES[0], font=alien_font, fg="red", pady=10)
alien_label.pack()

# Ceza Puanı Etiketi
penalty_display_label = tk.Label(main_frame, text=f"Ceza Puanı: 0/{MAX_PENALTY_POINTS}", font=label_font, fg="darkorange")
penalty_display_label.pack(pady=5)

# Durum Mesajı Etiketi
status_label = tk.Label(main_frame, text="Oyuna başlamak için 'Yeni Oyun'a tıklayın.", font=status_font, pady=10, wraplength=550)
status_label.pack()

# Başlangıçta "Yeni Oyun" butonu aktif olsun
guess_button.config(text="Yeni Oyun", command=start_new_game, state=tk.NORMAL)
guess_entry.config(state=tk.DISABLED)
hint_button.config(state=tk.DISABLED)


# --- Oyunu Başlat ---
# start_new_game() # İlk oyun otomatik başlasın istenirse bu satır açılır, yoksa kullanıcı butona basar.

root.mainloop()