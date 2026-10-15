import wayland_automation as wa


def clicar(x, y, botao="left"):
    wa.click(x, y, botao)


def autoClick(delayInicial, intervalo, duracao, botao="left"):
    wa.auto_click(initial_delay=delayInicial, interval=intervalo, duration=duracao, button=botao)


def posicaoAtualDoCursor():
    gerador = wa.mouse_position_generator(interval=0.1)
    return next(gerador)