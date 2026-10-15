import wayland_automation as wa

def auto_click(delay_inicial, intervalo, duracao, botao: str = "left"):
    wa.auto_click(initial_delay=delay_inicial, interval=intervalo, duration=duracao, button=botao)

def posicao_atual_do_cursor():
    gerador = wa.mouse_position_generator(interval=0.1)
    return next(gerador)