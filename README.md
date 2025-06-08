# kelime-tahmin-oyunu
Python'da arayüz kullanarak kelime tahmin etme oyunu yapımı. (harf, süre, ipucu, kontrolü, kazanma ve kaybetme durumu)


**OYUN**
![Desktop 2025 06 04 - 17 31 46 04](https://github.com/user-attachments/assets/18fbc4ad-7e94-4114-8694-91a6c723bc41)




**Uzaylıdan Kaçış Şifreli Mesaj**

*- Grafiksel kullanıcı arayüz (GUI),*

*- Gerçek zamanlı etkileşim (süreli tahmin),*

*- Ses efekti yönetimi,*

*- Skor kaydı tutma*

*gibi ileri konuları içeren bir oyun geliştirmeleri hedeflenmektedir.*

*Programlama Dili: Python*

*Arayüz: Tkinter, Pygame* 

**ANA EKRAN**


![Ekran görüntüsü 2025-06-03 165828](https://github.com/user-attachments/assets/06ee0967-790f-47f8-beec-db812478ec42)


**1. Oyun Mantığı**

*Bu projede, kullanıcı rastgele seçilen bir şifreli cümleyi harf harf tahmin ederek uzaylıdan*
*kaçmaya çalışır. Şifreler, önceden belirlenmiş bilim kurgu temalı cümlelerin yer aldığı bir listeden*
*Python fonksiyonu ile otomatik olarak seçilir. Her tahmin için 20 saniyelik süresi vardır; yanlış*
*tahminlerde uzaylı yaklaşır, tuzak harflerde iki adım ilerler. Oyun, ses efektleriyle desteklenir ve*
*oyun sonucu (kazanma/kaybetme, süre) scores.txt dosyasına kaydedilir. Grafik arayüzü*
*oluşturulur ve kullanıcıya etkileşimli bir deneyim sunar.*

*GUI üzerinde:*

*a. Şifreli kelime _ _ _ şeklinde gösterilir*

*b. Harf tahmin girişi yapılır*

*c. Süre sayacı çalışır (20 saniye)*

*d. Her yanlışta uzaylı yaklaşır*

*e. Tuzak harf girilirse 2 adım ilerler*

*Maksimum 6 hata hakkı vardır.*

**2. Proje Bileşenleri**

*- Oyun başladığında rastgele seçilen kelime ya da kısa cümle,*

 *_ _ _ _ _ _ _ _ _ _ şeklinde gösterilir.*

**2. Süreli Tahmin**

*- Oyuncunun her tahmin için 10 saniye süresi vardır.*

*- Bu süre dinamik olarak kontrol edilmesi sağlanacaktır. Süre istenildiği durumlarda uzatılıp kısaltılabilir.*

*- Süre dolarsa yanlış sayılır ve uzaylı yaklaşır.*

**3. Uzaylı Yaklaşma Mekanizması**

*- Her yanlışta ASCII grafik ilerler:*

*��------��*

*��-----��*

*��----��*

*...*

**4. Tuzak Harf**

*-x, z, j, q gibi harfler tuzaktır.*

*- Girilirse uzaylı 2 adım yaklaşır.*

**5. İpucu**

*- Kullanıcı 1 kez ipucu alabilir.*

*- Şifrenin ilk harfi gösterilir.*

*- Ekstra 1 yanlış sayılır.*

**6. Ses Efektleri**

*- Doğru tahmin: correct.mp3*

*- Yanlış tahmin: wrong.mp3*

*- Oyunu kazanma: win.mp3*

*- Kaybetme: lose.mp3*

**7. Skor Kaydı**

*- Oyun sonunda başarı durumu ve süre bilgisi scores.txt dosyasına yazılır.*

*- 2025-05-20 10:33 | KAZANDI | roket fırlatma | 43 saniye*

*- 2025-05-20 10:41 | KAYBETTİ | uzay görevi | 62 saniye*

**KAZANMA**




https://github.com/user-attachments/assets/6b87cdac-52cc-45a9-8391-2a920e529223




**KAYBETME.**



https://github.com/user-attachments/assets/53bf83cd-53f3-4636-95b1-183bc0ddfc72


**OYUNDAN EKRAN GÖRÜNTÜLERİ**



![Ekran görüntüsü 2025-06-03 170000](https://github.com/user-attachments/assets/dfb9da20-3872-46d0-81aa-a53edf76ab2f)



![Ekran görüntüsü 2025-06-03 170037](https://github.com/user-attachments/assets/9f8e1165-8065-4b4e-b12a-55193e37c1de)



![Ekran görüntüsü 2025-06-03 170059](https://github.com/user-attachments/assets/9fc1ed5d-41da-4b34-abfc-130a4dbbb0d2)



![Ekran görüntüsü 2025-06-03 170118](https://github.com/user-attachments/assets/114c8f15-5fbe-4ffd-af0f-f1fbc7ff2054)

