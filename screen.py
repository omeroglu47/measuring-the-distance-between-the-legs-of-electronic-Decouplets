import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QTimer, QTime
import numpy as np
import kapasitor


class MyWindow(QWidget):
    def __init__(self):
        self.veri_yolu = ""
        self.time = 0.0
        self.distance = 0.0
        self.img = np.empty((0, 0))

        super().__init__()
        self.setWindowTitle("Kapasitör ayakları arasındaki mesafe ölçümü (mamur teknoloji)")
        self.setGeometry(100, 100, 1500, 900)
        self.setWindowIcon(QIcon("ikon.png"))

        # Logo eklemek için QLabel oluştur
        self.logo_label = QLabel(self)
        self.logo_label.setGeometry(20, 20, 350, 100)
        self.logo_label.setScaledContents(True)
        pixmap = QPixmap("mamurtech_logo.png")
        self.logo_label.setPixmap(pixmap)

        # Başlat butonu oluştur
        self.start_button = QPushButton("Başlat (Bacaklar Arasındaki Mesafeyi Ölç)", self)
        self.start_button.setGeometry(400, 40, 380, 60)
        self.start_button.setStyleSheet(
            "background-color: yellow; font-weight: bold; font-size: 16px; border-radius: 30px;")
        self.start_button.clicked.connect(self.start_measurement)

        # Görsel seç butonu oluştur
        self.select_image_button = QPushButton("Görsel Seç", self)
        self.select_image_button.setGeometry(800, 40, 180, 60)
        self.select_image_button.setStyleSheet(
            "background-color: yellow; font-weight: bold; font-size: 16px; border-radius: 30px;")
        self.select_image_button.clicked.connect(self.open_image)

        # Kapat butonu oluştur
        self.close_button = QPushButton("Kapat", self)
        self.close_button.setGeometry(1375, 100, 80, 50)
        self.close_button.setStyleSheet(
            "background-color: red; font-weight: bold; font-size: 16px; border-radius: 30px;")
        self.close_button.clicked.connect(self.close_window)

        # Açıklama etiketi oluştur
        self.description_label = QLabel(
            "Gripper tarafından tutulan kapasitör analiz edilmektedir. Bu kapasitörün bacakları arasındaki mesafeyi piksel cinsinden vermektedir.",
            self)
        self.description_label.setGeometry(1000, 20, 350, 100)
        self.description_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; border: 2px solid black; padding: 10px;")
        self.description_label.setWordWrap(True)

        # Resim alanı oluştur
        self.image_label = QLabel(self)
        self.image_label.setGeometry(50, 140, 1000, 700)

        # IP1_Cap.jpg görselini yükle
        self.load_default_image()

        # Mesafe labelı oluştur
        self.distance_label = QLabel("", self)
        self.distance_label.setGeometry(1050, 250, 420, 100)
        self.distance_label.setStyleSheet(
            "background-color: #ADD8E6; color: black; font-weight: bold; font-size: 18px; border: 4px solid black;")

        # Zaman labelı oluştur
        self.time_label = QLabel("", self)
        self.time_label.setGeometry(1050, 450, 420, 100)
        self.time_label.setStyleSheet(
            "background-color: #ADD8E6; color: black; font-weight: bold; font-size: 17px; border: 4px solid black;")

        # Durum labelı oluştur
        self.status_label = QLabel("Durum: ", self)
        self.status_label.setGeometry(100, 840, 1175, 60)
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        # Saat labelı oluştur
        self.clock_label = QLabel("", self)
        self.clock_label.setGeometry(1370, 50, 100, 40)
        self.clock_label.setStyleSheet(
            "background-color: green; color: black; font-weight: bold; font-size: 16px; border: 2px solid black;")

        # Timer oluştur
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # 1 saniyede bir güncelle

        # İlk kez saat etiketini güncelle
        self.update_time()

    def open_image(self):
        # Resim seçme iletişim kutusunu aç
        file_name, _ = QFileDialog.getOpenFileName(self, "Resim Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            # Seçilen resmi yükle
            pixmap = QPixmap(file_name)
            # Resmi resim alanına sığdır
            self.image_label.setPixmap(pixmap.scaled(1000, 700, aspectRatioMode=True))
            self.veri_yolu = file_name
            self.status_label.setText("Resim başarıyla yüklendi.")

    def load_default_image(self):
        # IP1_Cap.jpg görselini yükle
        pixmap = QPixmap("IP1_Cap.jpg")
        # Resmi resim alanına sığdır
        self.image_label.setPixmap(pixmap.scaled(1000, 700, aspectRatioMode=True))
        self.veri_yolu = "IP1_Cap.jpg"

    def load_kapasitor(self, img):
        pixmap = QPixmap(img)
        # Resmi resim alanına sığdır
        self.image_label.setPixmap(pixmap.scaled(1000, 700, aspectRatioMode=True))

    def start_measurement(self):
        if self.veri_yolu:

            try:
                sonuc = kapasitor.baslatma(self.veri_yolu)
                self.time = float(sonuc[0])
                self.distance = float(sonuc[1])
                self.img = sonuc[2]

                pixmap = QPixmap("output_image.jpg")
                # Resmi resim alanına sığdır
                self.image_label.setPixmap(pixmap.scaled(1000, 700, aspectRatioMode=True))

                # Mesafe ve zamanı güncelle
                self.distance_label.setText(f"Mesafe: {self.distance} px")
                self.time_label.setText(f"Çalışma Zamanı: {self.time} s")

                self.status_label.setText("İşlem başarıyla tamamlandı.")

            except Exception as e:

                self.status_label.setText(f"Hata: {str(e)} lütfen geçerli bir görsel girin")
        else:

            self.status_label.setText("Lütfen önce bir görsel seçin.")

    def update_time(self):
        # Anlık saat bilgisini al
        current_time = QTime.currentTime()
        # Saat formatını ayarla
        display_text = current_time.toString('hh:mm:ss')
        # Saat etiketini güncelle
        self.clock_label.setText(display_text)

    def close_window(self):
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
