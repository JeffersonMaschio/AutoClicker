import threading
import time

import wayland_automation as wa

def auto_click(delay_inicial, intervalo, duracao, botao: str = "left", parar=None):
    """Clica no intervalo configurado até o tempo acabar ou ``parar`` ser sinalizado."""
    mouse = wa.Mouse()
    codigo_botao = {"left": 0x110, "right": 0x111}.get(botao.lower(), 0x110)
    evento_parada = parar or threading.Event()

    try:
        if evento_parada.wait(delay_inicial):
            return

        inicio = time.monotonic()
        while not evento_parada.is_set() and time.monotonic() - inicio < duracao:
            mouse.send_click(codigo_botao)
            if evento_parada.wait(intervalo):
                break
    finally:
        mouse.sock.close()

def posicao_atual_do_cursor():
    gerador = wa.mouse_position_generator(interval=0.1)
    return next(gerador)

