import 'dart:io';
import 'dart:typed_data';
import 'package:record/record.dart';

class AudioStreamer {
  final AudioRecorder _recorder = AudioRecorder();
  RawDatagramSocket? _socket;
  InternetAddress? _targetAddress;
  bool _isStreaming = false;

  Future<bool> startStreaming(String ipAddress) async {
    if (_isStreaming) return true;

    try {
      _targetAddress = InternetAddress(ipAddress);
      
      // UDP socket for sending
      _socket = await RawDatagramSocket.bind(InternetAddress.anyIPv4, 0);
      
      if (await _recorder.hasPermission()) {
        final stream = await _recorder.startStream(const RecordConfig(
          encoder: AudioEncoder.pcm16bits,
          bitRate: 128000,
          sampleRate: 44100,
          numChannels: 1,
        ));

        stream.listen(
          (Uint8List data) {
            if (_socket != null && _targetAddress != null) {
              _socket!.send(data, _targetAddress!, 50000);
            }
          },
          onError: (e) => print('Ses kayıt hatası: $e'),
          onDone: () => stopStreaming(),
        );

        _isStreaming = true;
        return true;
      }
      return false;
    } catch (e) {
      print('Streaming error: $e');
      stopStreaming();
      return false;
    }
  }

  Future<void> stopStreaming() async {
    _isStreaming = false;
    await _recorder.stop();
    _socket?.close();
    _socket = null;
  }

  bool get isStreaming => _isStreaming;
}
