import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:permission_handler/permission_handler.dart';
import 'audio_streamer.dart';

void main() {
  runApp(const EMicApp());
}

class EMicApp extends StatelessWidget {
  const EMicApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'E-MIC',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1F538D),
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      home: const EMicHome(),
    );
  }
}

class EMicHome extends StatefulWidget {
  const EMicHome({super.key});

  @override
  State<EMicHome> createState() => _EMicHomeState();
}

class _EMicHomeState extends State<EMicHome> {
  final TextEditingController _ipController = TextEditingController();
  final AudioStreamer _audioStreamer = AudioStreamer();
  bool _isStreaming = false;

  @override
  void initState() {
    super.initState();
    _loadSavedIp();
    _requestPermissions();
  }

  Future<void> _requestPermissions() async {
    await Permission.microphone.request();
  }

  Future<void> _loadSavedIp() async {
    final prefs = await SharedPreferences.getInstance();
    final savedIp = prefs.getString('last_ip');
    if (savedIp != null) {
      _ipController.text = savedIp;
    }
  }

  Future<void> _saveIp(String ip) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('last_ip', ip);
  }

  void _toggleStreaming() async {
    if (_isStreaming) {
      await _audioStreamer.stopStreaming();
      setState(() {
        _isStreaming = false;
      });
    } else {
      final ip = _ipController.text.trim();
      if (ip.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Lütfen bilgisayarınızın IP adresini girin')),
        );
        return;
      }

      await _saveIp(ip);
      final success = await _audioStreamer.startStreaming(ip);
      
      if (success) {
        setState(() {
          _isStreaming = true;
        });
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Bağlantı veya mikrofon izni hatası')),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('E-MIC', style: TextStyle(fontWeight: FontWeight.bold)),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.mic, size: 80, color: Colors.blueAccent),
            const SizedBox(height: 40),
            TextField(
              controller: _ipController,
              decoration: const InputDecoration(
                labelText: 'Bilgisayar IP Adresi',
                hintText: 'Örn: 192.168.1.100',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.computer),
              ),
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              enabled: !_isStreaming,
            ),
            const SizedBox(height: 40),
            ElevatedButton(
              onPressed: _toggleStreaming,
              style: ElevatedButton.styleFrom(
                backgroundColor: _isStreaming ? Colors.red.shade700 : const Color(0xFF1F538D),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 50, vertical: 20),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(30),
                ),
              ),
              child: Text(
                _isStreaming ? 'Bağlantıyı Kes' : 'Bağlan ve Konuş',
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            const SizedBox(height: 20),
            Text(
              _isStreaming ? 'Ses aktarılıyor...' : 'Bekleniyor',
              style: TextStyle(
                color: _isStreaming ? Colors.green : Colors.grey,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _ipController.dispose();
    _audioStreamer.stopStreaming();
    super.dispose();
  }
}
