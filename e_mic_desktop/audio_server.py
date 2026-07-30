import socket
import threading
import pyaudio
import struct

class AudioServer:
    def __init__(self, port=50000, output_device_index=None):
        self.port = port
        self.output_device_index = output_device_index
        
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.sock = None
        
        self.is_running = False
        self.thread = None

    def start(self):
        if self.is_running:
            return
            
        try:
            self.stream = self.p.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      output=True,
                                      output_device_index=self.output_device_index,
                                      frames_per_buffer=self.chunk)
                                      
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(("0.0.0.0", self.port))
            
            self.is_running = True
            self.thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.thread.start()
            return True, "Sunucu başlatıldı. Bağlantı bekleniyor..."
        except Exception as e:
            self.stop()
            return False, f"Hata: {str(e)}"

    def _receive_loop(self):
        while self.is_running:
            try:
                data, addr = self.sock.recvfrom(65536)
                if data and self.stream:
                    self.stream.write(data)
            except OSError:
                break
            except Exception as e:
                print(f"Alım hatası: {e}")

    def stop(self):
        self.is_running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
            
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            self.stream = None

    @staticmethod
    def get_output_devices():
        p = pyaudio.PyAudio()
        devices = []
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
                name = p.get_device_info_by_host_api_device_index(0, i).get('name')
                devices.append((i, name))
        p.terminate()
        return devices
