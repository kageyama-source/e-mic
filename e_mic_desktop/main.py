import customtkinter as ctk
import socket
import threading
from audio_server import AudioServer

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("E-MIC Sunucu")
        self.geometry("400x500")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.server = None
        self.devices = AudioServer.get_output_devices()
        
        self._build_ui()

    def _build_ui(self):
        # Header
        self.title_label = ctk.CTkLabel(self, text="E-MIC Sunucu", font=("Roboto", 24, "bold"))
        self.title_label.pack(pady=20)

        # IP Info
        ip_addr = self._get_local_ip()
        self.ip_frame = ctk.CTkFrame(self)
        self.ip_frame.pack(pady=10, padx=20, fill="x")
        
        self.ip_title = ctk.CTkLabel(self.ip_frame, text="Telefonunuzdan bu IP adresine bağlanın:", font=("Roboto", 12))
        self.ip_title.pack(pady=(10, 0))
        
        self.ip_label = ctk.CTkLabel(self.ip_frame, text=ip_addr, font=("Roboto", 20, "bold"), text_color="#1f538d")
        self.ip_label.pack(pady=(5, 10))

        # Device Selection
        self.device_label = ctk.CTkLabel(self, text="Çıkış Aygıtı (Sanal Mikrofonunuz):", font=("Roboto", 14))
        self.device_label.pack(pady=(20, 5))

        device_names = [name for _, name in self.devices] if self.devices else ["Cihaz bulunamadı"]
        self.device_combo = ctk.CTkOptionMenu(self, values=device_names, width=300)
        self.device_combo.pack(pady=5)
        
        if not self.devices:
            self.device_combo.configure(state="disabled")

        # Port Info
        self.port_label = ctk.CTkLabel(self, text="Port: 50000", font=("Roboto", 12))
        self.port_label.pack(pady=5)

        # Status Label
        self.status_label = ctk.CTkLabel(self, text="Durum: Durduruldu", text_color="red", font=("Roboto", 14))
        self.status_label.pack(pady=20)

        # Start/Stop Button
        self.toggle_btn = ctk.CTkButton(self, text="Sunucuyu Başlat", command=self.toggle_server,
                                        width=200, height=40, font=("Roboto", 16, "bold"))
        self.toggle_btn.pack(pady=20)

    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def toggle_server(self):
        if self.server and self.server.is_running:
            self.server.stop()
            self.status_label.configure(text="Durum: Durduruldu", text_color="red")
            self.toggle_btn.configure(text="Sunucuyu Başlat", fg_color=["#3a7ebf", "#1f538d"])
            self.device_combo.configure(state="normal")
        else:
            selected_name = self.device_combo.get()
            device_idx = None
            for idx, name in self.devices:
                if name == selected_name:
                    device_idx = idx
                    break
                    
            self.server = AudioServer(port=50000, output_device_index=device_idx)
            success, msg = self.server.start()
            
            if success:
                self.status_label.configure(text="Durum: Çalışıyor", text_color="green")
                self.toggle_btn.configure(text="Sunucuyu Durdur", fg_color="#a83232", hover_color="#8c2a2a")
                self.device_combo.configure(state="disabled")
            else:
                self.status_label.configure(text=f"Durum: {msg}", text_color="orange")

    def on_closing(self):
        if self.server:
            self.server.stop()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
