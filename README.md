
# Reproductor de YouTube Avanzado

Este proyecto es una aplicación de escritorio para reproducir videos de YouTube con funcionalidades avanzadas, desarrollada en Python usando Tkinter para la interfaz gráfica y VLC como motor de reproducción.

## Características

- **Reproducción de videos de YouTube**: Reproduce directamente desde URLs de YouTube sin necesidad de descargar
- **Selección de calidad**: Permite elegir entre diferentes resoluciones disponibles (720p, 1080p, etc.)
- **Soporte de subtítulos**: Carga subtítulos manuales y automáticos en múltiples idiomas
- **Interfaz intuitiva**: Ventana simple con controles de reproducción (play/pause, stop)
- **Streams separados**: Maneja video y audio por separado para mejor calidad
- **Compatibilidad**: Funciona con la mayoría de videos de YouTube públicos

## Archivos del proyecto

- `main.py`: Aplicación principal con la interfaz gráfica y toda la funcionalidad del reproductor
- `test_vlc.py`: Script de prueba para verificar que VLC esté correctamente instalado y configurado
- `icono.ico`: Icono de la aplicación

# Install

Primero, necesitas tener instalado el VLC Media Player en tu sistema. La librería de Python lo necesita para funcionar.
Descarga VLC aquí: https://www.videolan.org/vlc/
(Asegúrate de instalar la versión que coincida con la arquitectura de tu Python, es decir, si usas Python de 64 bits, instala VLC de 64 bits).
Luego, instala las librerías de Python necesarias usando pip:

```bash
pip install python-vlc yt-dlp
```

## Necesario

1. **Tkinter**: Para crear la ventana y los controles (botones, campo de texto, etc.). Viene incluida con Python, así que no necesitas instalar nada.
2. **yt-dlp**: Para obtener la información del video de YouTube, las URL de los streams (video y audio) y los subtítulos. Es una versión mejorada y más actualizada de youtube-dl.
3. **python-vlc**: Para reproducir el video en nuestra ventana de Tkinter. Esta librería es un "binding" (un puente) al motor de VLC Media Player, que es extremadamente potente y compatible con casi cualquier formato.

