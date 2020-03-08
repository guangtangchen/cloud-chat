import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000


def record_audio_main(file_in):
    """
    录制音频
    :param file_in: str, 暂存音频的文件名
    :return: None
    """
    def record_audio():
        rec_time = 4   # 录制时间为4S
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
        print('start recording....')
        frames = []
        for i in range(int(RATE / CHUNK * rec_time)):
            data = stream.read(CHUNK)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        print('recording done...')
        wf = wave.open(output_file, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
    output_file = file_in
    print(output_file)
    record_audio()


def run_audio_main(file_in):
    """
    播放语音的主函数
    :param file_in: str, target wave file
    :return: None
    """
    if not file_in:
        return
    f = wave.open(file_in, 'rb')
    params = f.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    p = pyaudio.PyAudio()   # audio对象
    chunk = 1024
    stream = p.open(format=p.get_format_from_width(sampwidth),
                    channels=nchannels,
                    rate=framerate,
                    output=True)   # 音频流
    while True:
        data = f.readframes(chunk)
        if data == b'':
            break
        stream.write(data)   # 输出音频
    f.close()
    stream.stop_stream()
    stream.close()
    p.terminate()


