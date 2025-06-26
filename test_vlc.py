# test_vlc.py
print("Intentando importar vlc...")
import vlc
print("Importación exitosa.")

print("Intentando crear una instancia de VLC...")
try:
    instance = vlc.Instance()
    print("¡Instancia de VLC creada con éxito!")
    player = instance.media_player_new()
    print("Reproductor VLC creado con éxito.")
    print("\n>>> Tu configuración de Python y VLC parece ser correcta. <<<")
except Exception as e:
    print(f"\nXXX Error al inicializar VLC: {e} XXX")
    print("Revisa los puntos de la sección 'Causas y Soluciones'.")