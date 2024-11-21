from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
import wave
import os
import json
from tkinter import Tk, filedialog, messagebox, Button, Label, Frame
from tkinter.ttk import Progressbar

def convert_audio_to_wav(audio_file):
    """
    Convierte un archivo de audio MP3 o M4A a formato WAV mono PCM.
    """
    try:
        # Cargar el archivo de audio (MP3 o M4A)
        audio = AudioSegment.from_file(audio_file)

        # Convertir a mono
        audio = audio.set_channels(1)

        # Asegurar la tasa de muestreo adecuada (16kHz es común para reconocimiento de voz)
        audio = audio.set_frame_rate(16000)

        # Exportar como archivo WAV
        wav_file = audio_file.rsplit(".", 1)[0] + ".wav"
        audio.export(wav_file, format="wav")

        return wav_file
    except Exception as e:
        messagebox.showerror("Error", f"Error al convertir el archivo de audio: {e}")
        return None

def transcribe_audio(file_path, progress_bar, root):
    """
    Transcribe el audio usando el modelo Vosk y actualiza la barra de progreso.
    """
    # Ruta del modelo (cambiar si está en otra ubicación)
    model_path = "modelo/vosk-model-small-es-0.42"

    # Verificar si el modelo existe
    if not os.path.exists(model_path):
        messagebox.showerror("Error", "Modelo de Vosk no encontrado en la ruta especificada.")
        return

    # Cargar el modelo
    model = Model(model_path)

    # Leer el archivo de audio
    wf = wave.open(file_path, "rb")

    # Verificar que sea un archivo mono y con el framerate correcto
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        messagebox.showerror("Error", "El archivo debe estar en formato WAV mono PCM.")
        return

    recognizer = KaldiRecognizer(model, wf.getframerate())
    transcription = ""
    total_frames = wf.getnframes()
    frames_processed = 0

    while True:
        data = wf.readframes(4000)
        frames_processed += len(data)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            transcription += result.get("text", "") + "\n"

        # Actualizar la barra de progreso
        progress = int((frames_processed / total_frames) * 100)
        progress_bar["value"] = progress
        root.update_idletasks()  # Actualizar la interfaz en tiempo real

    wf.close()
    return transcription

def select_audio_file(progress_bar, root):
    """
    Abre un cuadro de diálogo para seleccionar un archivo MP3 o M4A y comienza la transcripción.
    """
    file_path = filedialog.askopenfilename(
        title="Seleccionar archivo de audio",
        filetypes=[("Archivos MP3", "*.mp3"), ("Archivos M4A", "*.m4a")]
    )
    if file_path:
        wav_file = convert_audio_to_wav(file_path)  # Convertir MP3 o M4A a WAV
        if wav_file:
            transcription = transcribe_audio(wav_file, progress_bar, root)
            if transcription:
                save_transcription(transcription)
            os.remove(wav_file)  # Eliminar el archivo WAV temporal

def save_transcription(transcription):
    """
    Guarda la transcripción en un archivo de texto.
    """
    save_path = filedialog.asksaveasfilename(
        title="Guardar transcripción",
        defaultextension=".txt",
        filetypes=[("Archivos de texto", "*.txt")]
    )
    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(transcription)
        messagebox.showinfo("Éxito", "Transcripción guardada correctamente.")

def create_gui():
    """
    Crea la interfaz gráfica con Tkinter.
    """
    root = Tk()
    root.title("Transcriptor de Audio")
    root.geometry("500x300")
    
    # Frame para los widgets
    frame = Frame(root)
    frame.pack(pady=20)

    # Título de la interfaz
    label = Label(frame, text="Transcriptor de Audio", font=("Helvetica", 16))
    label.pack(pady=10)

    # Botón para seleccionar y transcribir archivo
    transcribe_button = Button(frame, text="Seleccionar archivo de audio", font=("Helvetica", 12), command=lambda: select_audio_file(progress_bar, root))
    transcribe_button.pack(pady=10)

    # Barra de progreso
    progress_bar = Progressbar(frame, length=300, mode="determinate", maximum=100)
    progress_bar.pack(pady=10)

    # Iniciar la interfaz
    root.mainloop()

if __name__ == "__main__":
    create_gui()
