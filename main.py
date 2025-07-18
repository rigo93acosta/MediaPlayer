import tkinter as tk
from tkinter import ttk, messagebox
import vlc
import threading
import os
import yt_dlp
import time
import urllib.request
import re

class YouTubePlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reproductor de YouTube")
        self.root.geometry("900x700")
        # Cambiar el icono (ajusta la ruta según tu archivo)
        try:
            self.root.iconbitmap("icono.ico")  # Para archivos .ico
            # O usa: self.root.iconphoto(False, tk.PhotoImage(file="icono.png"))  # Para PNG
        except:
            pass  # Si no encuentra el icono, continúa sin él
        # --- Variables de estado ---
        self.vlc_instance = None
        self.player = None
        self.current_url = ""
        self.available_formats = {}  # {'1080p': 'format_id', ...}
        self.available_subtitles = {} # {'Español': 'es', ...}
        self.subtitle_file = "subtitle.vtt" # Nombre del archivo de subtitulos
        self.current_subtitle_lang = None

        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def initialize_vlc(self):
        if self.vlc_instance is None:
            try:
                # Opciones VLC mejoradas para subtítulos
                vlc_args = [
                    "--no-xlib", 
                    "--avcodec-hw=none",
                    "--sub-autodetect-file",
                    "--sub-track=0"
                ]
                self.vlc_instance = vlc.Instance(vlc_args)
                self.player = self.vlc_instance.media_player_new()
                return True
            except Exception as e:
                messagebox.showerror("Error de VLC", f"No se pudo inicializar VLC. Asegúrate de que VLC Media Player (misma arquitectura que Python) esté instalado.\n\nError: {e}")
                return False
        return True

    def create_widgets(self):
        # --- Frame Superior ---
        top_frame = tk.Frame(self.root, bg="lightgrey", pady=5)
        top_frame.pack(side=tk.TOP, fill=tk.X)
        tk.Label(top_frame, text="URL de YouTube:", bg="lightgrey").pack(side=tk.LEFT, padx=(10, 5))
        self.url_entry = tk.Entry(top_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.load_button = tk.Button(top_frame, text="Cargar", command=self.load_video)
        self.load_button.pack(side=tk.LEFT, padx=(0, 10))

        # --- Frame para el Video ---
        self.video_frame = tk.Frame(self.root, bg="black")
        self.video_frame.pack(expand=True, fill=tk.BOTH)

        # --- Frame de Controles ---
        bottom_frame = tk.Frame(self.root, bg="lightgrey", pady=5)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.play_pause_button = tk.Button(bottom_frame, text="Play/Pause", command=self.play_pause, state="disabled")
        self.play_pause_button.pack(side=tk.LEFT, padx=10)
        self.stop_button = tk.Button(bottom_frame, text="Stop", command=self.stop, state="disabled")
        self.stop_button.pack(side=tk.LEFT)

        tk.Label(bottom_frame, text="Calidad:", bg="lightgrey").pack(side=tk.LEFT, padx=(20, 5))
        self.quality_var = tk.StringVar()
        self.quality_menu = ttk.Combobox(bottom_frame, textvariable=self.quality_var, state="disabled", width=15)
        self.quality_menu.pack(side=tk.LEFT, padx=5)
        self.quality_menu.bind("<<ComboboxSelected>>", self.change_quality)

        tk.Label(bottom_frame, text="Subtítulos:", bg="lightgrey").pack(side=tk.LEFT, padx=(20, 5))
        self.subtitle_var = tk.StringVar()
        self.subtitle_menu = ttk.Combobox(bottom_frame, textvariable=self.subtitle_var, state="disabled", width=20)
        self.subtitle_menu.pack(side=tk.LEFT, padx=5)
        self.subtitle_menu.bind("<<ComboboxSelected>>", self.select_subtitle)
        
        # --- Etiqueta de Estado ---
        self.status_label = tk.Label(self.root, text="Introduce una URL para comenzar", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def set_status(self, text):
        self.status_label.config(text=text)

    def _is_valid_youtube_url(self, url):
        """Valida que la URL sea de YouTube y tenga formato correcto."""
        if not url or not isinstance(url, str):
            return False
        
        # Patrones válidos para URLs de YouTube
        youtube_patterns = [
            r'^https?://(www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
            r'^https?://(www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
            r'^https?://(www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            r'^https?://(www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in youtube_patterns:
            if re.match(pattern, url):
                return True
        return False

    def load_video(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Por favor, introduce una URL de YouTube.")
            return
            
        # Validar que sea una URL de YouTube válida
        if not self._is_valid_youtube_url(url):
            messagebox.showerror("Error", "Por favor, introduce una URL válida de YouTube.")
            return
            
        if not self.initialize_vlc():
            return

        self.current_url = url
        self.set_status("Cargando información del video...")
        self.reset_ui()
        
        thread = threading.Thread(target=self._get_video_info_thread)
        thread.daemon = True
        thread.start()

    def reset_ui(self):
        """Limpia la UI antes de cargar un nuevo video."""
        self.load_button.config(state="disabled")
        self.play_pause_button.config(state="disabled")
        self.stop_button.config(state="disabled")
        self.quality_menu.config(state="disabled")
        self.quality_menu.set("")
        self.available_formats.clear()
        self.subtitle_menu.config(state="disabled")
        self.subtitle_menu.set("")
        self.available_subtitles.clear()
        self.current_subtitle_lang = None
        if self.player: 
            self.player.stop()
        self._cleanup_subtitle_files()

    def _cleanup_subtitle_files(self):
        """Limpia archivos de subtítulos temporales."""
        subtitle_extensions = ['.vtt', '.srt']
        for ext in subtitle_extensions:
            file_path = f"subtitle{ext}"
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass

    def _get_video_info_thread(self):
        """Obtiene la lista de calidades y subtítulos."""
        try:
            ydl_opts = {
                'quiet': True, 
                'listsubtitles': True,
                'writesubtitles': False,
                'writeautomaticsub': False
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.current_url, download=False)
            
            # --- Procesar Calidades ---
            for f in info_dict.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') == 'none' and f.get('ext') == 'mp4':
                    quality_name = f.get('format_note', f'{f.get("height")}p')
                    self.available_formats[quality_name] = f['format_id']
            
            # --- Procesar Subtítulos ---
            # Subtítulos manuales
            subtitles = info_dict.get('subtitles', {})
            for lang_code, sub_list in subtitles.items():
                # Buscar nombres de idiomas más descriptivos
                lang_name = self._get_language_name(lang_code)
                self.available_subtitles[f"{lang_name} (Manual)"] = lang_code
            
            # Subtítulos automáticos
            auto_captions = info_dict.get('automatic_captions', {})
            for lang_code, sub_list in auto_captions.items():
                if lang_code not in subtitles:  # Solo si no hay subtítulo manual
                    lang_name = self._get_language_name(lang_code)
                    self.available_subtitles[f"{lang_name} (Auto)"] = lang_code

            self.root.after(0, self._on_video_info_loaded, info_dict.get('title', 'Video'))

        except Exception as e:
            # No exponer detalles del error por seguridad
            self.root.after(0, messagebox.showerror, "Error", "No se pudo obtener la información del video. Verifica la URL e intenta nuevamente.")
            self.root.after(0, self.load_button.config, {"state": "normal"})
            self.root.after(0, self.set_status, "Error al cargar. Intenta con otra URL.")

    def _get_language_name(self, lang_code):
        """Convierte códigos de idioma a nombres más legibles."""
        language_map = {
            'es': 'Español',
            'en': 'Inglés',
            'fr': 'Francés',
            'de': 'Alemán',
            'it': 'Italiano',
            'pt': 'Portugués',
            'ru': 'Ruso',
            'zh': 'Chino',
            'ja': 'Japonés',
            'ko': 'Coreano'
        }
        return language_map.get(lang_code, lang_code.upper())
            
    def _on_video_info_loaded(self, video_title):
        """Actualiza la GUI cuando la información está lista."""
        self.root.title(f"{video_title} - Reproductor")
        
        # --- Poblar menú de calidad ---
        qualities = sorted(self.available_formats.keys(), key=lambda q: int(''.join(filter(str.isdigit, q)) or 0), reverse=True)
        if qualities:
            self.quality_menu['values'] = qualities
            self.quality_menu.config(state="readonly")
            self.quality_var.set(qualities[0])
            self.change_quality() # Inicia la reproducción con la mejor calidad
        else:
            messagebox.showerror("Error", "No se encontraron formatos de video MP4 compatibles.")
            self.load_button.config(state="normal")
            self.set_status("Listo.")
            return

        # --- Poblar menú de subtítulos ---
        if self.available_subtitles:
            sub_list = ["Sin subtítulos"] + sorted(list(self.available_subtitles.keys()))
            self.subtitle_menu['values'] = sub_list
            self.subtitle_menu.config(state="readonly")
            self.subtitle_var.set("Sin subtítulos")

        self.load_button.config(state="normal")
        self.play_pause_button.config(state="normal")
        self.stop_button.config(state="normal")

    def change_quality(self, event=None):
        """Inicia la reproducción con la calidad seleccionada."""
        selected_quality_name = self.quality_var.get()
        format_id = self.available_formats.get(selected_quality_name)
        if not format_id: return

        self.set_status(f"Cargando calidad: {selected_quality_name}...")
        self.play_pause_button.config(state="disabled")

        thread = threading.Thread(target=self._get_stream_url_and_play, args=(format_id,))
        thread.daemon = True
        thread.start()

    def _get_stream_url_and_play(self, format_id):
        """
        Obtiene las URLs de video y audio por separado y las reproduce con VLC.
        """
        try:
            self.root.after(0, self.set_status, f"Cargando stream para {self.quality_var.get()}...")
            
            ydl_opts = {
                'format': f'{format_id}+bestaudio',
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.current_url, download=False)

            # --- CORRECCIÓN CLAVE ---
            # yt-dlp devuelve los formatos solicitados en 'requested_formats'
            if 'requested_formats' in info and len(info['requested_formats']) == 2:
                # Asumimos que el primero es el video y el segundo el audio
                video_url = info['requested_formats'][0]['url']
                audio_url = info['requested_formats'][1]['url']
            else:
                # Si no, es un formato pre-combinado (baja calidad)
                video_url = info['url']
                audio_url = None

            # Creamos el medio principal con el video
            media = self.vlc_instance.media_new(video_url)
            
            # Si hay un stream de audio separado, lo añadimos como opción
            if audio_url:
                media.add_option(f':input-slave={audio_url}')
            
            self.player.set_media(media)
            self.player.set_hwnd(self.video_frame.winfo_id())
            self.player.play()

            # Esperar a que el reproductor esté listo y luego aplicar subtítulos
            self.root.after(2000, self._reapply_current_subtitle)
            
            self.root.after(0, self.play_pause_button.config, {"state": "normal"})
            self.root.after(0, self.set_status, f"Reproduciendo en {self.quality_var.get()}")

        except Exception as e:
            # No exponer detalles del error por seguridad
            self.root.after(0, messagebox.showerror, "Error de Reproducción", "No se pudo cargar el stream. Intenta con otra calidad.")
            self.root.after(0, self.play_pause_button.config, {"state": "normal"})
            self.root.after(0, self.set_status, "Error al cambiar de calidad.")

    def _reapply_current_subtitle(self):
        """Reaplica el subtítulo actual después de cambiar la calidad."""
        if self.current_subtitle_lang and self.subtitle_var.get() != "Sin subtítulos":
            self._apply_subtitle_to_player()

    def select_subtitle(self, event=None):
        """Descarga y aplica el subtítulo seleccionado."""
        lang_name = self.subtitle_var.get()
        
        if lang_name == "Sin subtítulos":
            self.current_subtitle_lang = None
            if self.player:
                # Desactivar subtítulos
                self.player.video_set_spu(-1)
            self._cleanup_subtitle_files()
            self.set_status("Subtítulos desactivados")
            return

        if lang_name in self.available_subtitles:
            lang_code = self.available_subtitles[lang_name]
            self.current_subtitle_lang = lang_code
            
            # Primero intentar usar subtítulos embebidos de VLC
            if self._try_embedded_subtitles(lang_code):
                self.set_status(f"Usando subtítulos embebidos: {lang_name}")
            else:
                # Si no funciona, descargar el archivo
                self.set_status(f"Descargando subtítulo: {lang_name}...")
                thread = threading.Thread(target=self._download_subtitle_thread, args=(lang_code, lang_name))
                thread.daemon = True
                thread.start()

    def _try_embedded_subtitles(self, lang_code):
        """Intenta usar subtítulos que puedan estar embebidos en el stream."""
        if not self.player:
            return False
        
        try:
            # Obtener lista de pistas de subtítulos disponibles
            spu_count = self.player.video_get_spu_count()
            if spu_count > 0:
                spu_descriptions = self.player.video_get_spu_description()
                for i, (spu_id, spu_name) in enumerate(spu_descriptions):
                    spu_name_str = spu_name.decode('utf-8') if isinstance(spu_name, bytes) else str(spu_name)
                    if lang_code.lower() in spu_name_str.lower():
                        self.player.video_set_spu(spu_id)
                        return True
            return False
        except:
            return False
            
    def _download_subtitle_thread(self, lang_code, lang_name):
        """Descarga el archivo de subtítulo en segundo plano usando múltiples métodos."""
        try:
            # Limpiar archivos anteriores
            self._cleanup_subtitle_files()
            
            # Método 1: Intentar obtener URL directa del subtítulo
            subtitle_url = self._get_subtitle_url(lang_code)
            if subtitle_url:
                success = self._download_subtitle_from_url(subtitle_url, lang_code)
                if success:
                    self.root.after(500, self._apply_subtitle_to_player)
                    self.root.after(0, self.set_status, f"Subtítulo '{lang_name}' cargado correctamente.")
                    return
            
            # Método 2: Usar yt-dlp con configuración alternativa
            success = self._download_with_ytdlp_alternative(lang_code)
            if success:
                self.root.after(500, self._apply_subtitle_to_player)
                self.root.after(0, self.set_status, f"Subtítulo '{lang_name}' cargado correctamente.")
                return
            
            # Si ningún método funciona
            self.root.after(0, self.set_status, f"No se pudo descargar el subtítulo '{lang_name}'.")
                
        except Exception as e:
            # No exponer detalles del error por seguridad
            self.root.after(0, messagebox.showerror, "Error de Subtítulo", "No se pudo descargar el subtítulo.")
            self.root.after(0, self.set_status, "Error al descargar subtítulo.")

    def _get_subtitle_url(self, lang_code):
        """Obtiene la URL directa del subtítulo sin descargarlo."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.current_url, download=False)
            
            # Buscar en subtítulos manuales
            subtitles = info.get('subtitles', {})
            if lang_code in subtitles:
                for sub in subtitles[lang_code]:
                    if sub.get('ext') in ['vtt', 'srt']:
                        return sub.get('url')
            
            # Buscar en subtítulos automáticos
            auto_captions = info.get('automatic_captions', {})
            if lang_code in auto_captions:
                for sub in auto_captions[lang_code]:
                    if sub.get('ext') in ['vtt', 'srt']:
                        return sub.get('url')
            
            return None
        except:
            return None

    def _download_subtitle_from_url(self, url, lang_code):
        """Descarga el subtítulo directamente desde la URL."""
        try:
            import urllib.request
            
            # Determinar extensión del archivo
            ext = 'vtt' if 'vtt' in url.lower() else 'srt'
            filename = f"subtitle.{lang_code}.{ext}"
            
            # Descargar el archivo
            urllib.request.urlretrieve(url, filename)
            
            if os.path.exists(filename):
                self.subtitle_file = filename
                return True
            return False
        except:
            return False

    def _download_with_ytdlp_alternative(self, lang_code):
        """Método alternativo de descarga con yt-dlp."""
        try:
            # Configuración más permisiva
            ydl_opts = {
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': [lang_code],
                'skip_download': True,
                'outtmpl': {
                    'default': 'subtitle',
                    'subtitle': f'subtitle.{lang_code}'
                },
                'subtitlesformat': 'vtt',
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.current_url])
            
            # Buscar el archivo descargado con múltiples patrones
            possible_files = [
                f"subtitle.{lang_code}.vtt",
                f"subtitle.{lang_code}.srt", 
                "subtitle.vtt",
                "subtitle.srt"
            ]
            
            # También buscar archivos que puedan tener el ID del video
            import re
            video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', self.current_url)
            if video_id_match:
                video_id = video_id_match.group(1)
                possible_files.extend([
                    f"{video_id}.{lang_code}.vtt",
                    f"{video_id}.{lang_code}.srt"
                ])
            
            for filename in possible_files:
                if os.path.exists(filename):
                    # Renombrar a un nombre estándar
                    standard_name = "subtitle.vtt"
                    if filename != standard_name:
                        if os.path.exists(standard_name):
                            os.remove(standard_name)
                        os.rename(filename, standard_name)
                    self.subtitle_file = standard_name
                    return True
            
            return False
            
        except Exception as e:
            # Logging interno sin exponer al usuario
            # print(f"Error en método alternativo: {e}")  # Comentado por seguridad
            return False

    def _apply_subtitle_to_player(self):
        """Le dice a VLC que use el archivo de subtítulo."""
        if not self.player or not os.path.exists(self.subtitle_file):
            return
            
        try:
            # Obtener ruta absoluta del archivo
            full_path = os.path.abspath(self.subtitle_file)
            
            # En Windows, usar la ruta correcta para VLC
            if os.name == 'nt':
                file_uri = f"file:///{full_path.replace(os.sep, '/')}"
            else:
                file_uri = f"file://{full_path}"
            
            # Agregar el subtítulo como slave
            result = self.player.add_slave(vlc.MediaSlaveType.subtitle, file_uri, True)
            
            # También intentar configurar la pista de subtítulos
            if result == 0:  # Éxito
                # Esperar un poco y activar la primera pista de subtítulos
                time.sleep(0.5)
                self.player.video_set_spu(0)
                # print(f"Subtítulo aplicado: {file_uri}")  # Comentado por seguridad
            else:
                # print(f"Error al agregar subtítulo: {result}")  # Comentado por seguridad
                pass
                
        except Exception as e:
            # print(f"Error aplicando subtítulo: {e}")  # Comentado por seguridad
            pass

    def play_pause(self):
        if self.player: 
            self.player.pause()

    def stop(self):
        if self.player: 
            self.player.stop()

    def on_closing(self):
        if self.player: 
            self.player.stop()
        self._cleanup_subtitle_files()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubePlayerApp(root)
    root.mainloop()