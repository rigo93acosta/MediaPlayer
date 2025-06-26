
# Install

Primero, necesitas tener instalado el VLC Media Player en tu sistema. La librería de Python lo necesita para funcionar.
Descarga VLC aquí: https://www.videolan.org/vlc/
(Asegúrate de instalar la versión que coincida con la arquitectura de tu Python, es decir, si usas Python de 64 bits, instala VLC de 64 bits).
Luego, instala las librerías de Python necesarias usando pip:

```bash
pip install pytube python-vlc yt-dlp
```

## Necesario

1. Tkinter: Para crear la ventana y los controles (botones, campo de texto, etc.). Viene incluida con Python, así que no necesitas instalar nada.
2. pytube: Para obtener la información del video de YouTube, las URL de los streams (video y audio) y los subtítulos.
3. python-vlc: Para reproducir el video en nuestra ventana de Tkinter. Esta librería es un "binding" (un puente) al motor de VLC Media Player, que es extremadamente potente y compatible con casi cualquier formato.

