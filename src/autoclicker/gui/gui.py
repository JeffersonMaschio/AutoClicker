"""
AutoClicker - versão refatorada em arquivo único.

Em vez de classes (POO), cada "frame" da interface é criado por uma
função que monta os widgets e devolve o frame pronto. Estado que
antes ficava em atributos de instância (self.algumaCoisa) agora fica
em dicionários simples, guardados dentro do frame (frame.widgets) ou
em variáveis normais do escopo onde fazem sentido.
"""

import os
import threading
from math import inf

import customtkinter as ctk
import pyglet

from ..main import auto_click


# ---------------------------------------------------------------------------
# Tema
# ---------------------------------------------------------------------------

COLORS = {
    "bg": "#1a1a1a",
    "frameBg": "#222222",
    "border": "#c0c0c0",
    "text": "#c0c0c0",
    "hover": "#4f4f4f",
    "checkmark": "#2e2e2e",
    "comboFg": "#343638",
    "buttonBg": "#2e2e2e",
    "dropdownBg": "#1a1a1a",
}

# Referências dos widgets da janela ativa. As funções "obter*" leem daqui,
# então os callbacks não precisam receber os frames como argumentos.
estadoApp = {}

def criar_fontes():
    return {
        "titulo": ctk.CTkFont(family="Rubik", size=15, weight="bold"),
        "label": ctk.CTkFont(family="Rubik", size=12),
        "entry": ctk.CTkFont(family="Rubik", size=13),
    }


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def validar_numero(texto):
    if texto == "":
        return True
    return texto.isdigit() and len(texto) <= 4


def carregar_fontes_customizadas(assets_dir):
    pyglet.font.add_file(os.path.join(assets_dir, "Rubik-Regular.ttf"))
    pyglet.font.add_file(os.path.join(assets_dir, "Rubik-Bold.ttf"))


# ---------------------------------------------------------------------------
# Frame: Click Interval
# ---------------------------------------------------------------------------

def criar_campo_intervalo(frame, fontes, vcmd, row, col, texto):
    padx_entry = (5, 3) if col == 0 else 3
    entry = ctk.CTkEntry(
        frame, placeholder_text="0", width=50,
        validate="key", validatecommand=vcmd, text_color=COLORS["text"]
    )
    entry.grid(row=row, column=col, padx=padx_entry, pady=5)

    label = ctk.CTkLabel(frame, text=texto, font=fontes["label"], text_color=COLORS["text"])
    label.grid(row=row, column=col + 1)
    return entry


def criar_frame_click_interval(master, fontes, vcmd):
    frame = ctk.CTkFrame(master, fg_color=COLORS["frameBg"], border_color=COLORS["border"], border_width=1)

    label_titulo = ctk.CTkLabel(frame, text="[ Click Interval ]", font=fontes["titulo"], text_color=COLORS["text"])
    label_titulo.grid(row=0, column=0, columnspan=8, sticky="w", padx=10, pady=(3, 0))

    entry_hour = criar_campo_intervalo(frame, fontes, vcmd, row=1, col=0, texto="Hours")
    entry_min = criar_campo_intervalo(frame, fontes, vcmd, row=1, col=2, texto="Minutes")
    entry_sec = criar_campo_intervalo(frame, fontes, vcmd, row=1, col=4, texto="Seconds")
    entry_mil = criar_campo_intervalo(frame, fontes, vcmd, row=1, col=6, texto="Millisecs")
    entry_mil.insert(0, "100")

    # guarda as referências dos widgets no próprio frame, para ler depois
    frame.widgets = {
        "hour": entry_hour,
        "min": entry_min,
        "sec": entry_sec,
        "mil": entry_mil,
    }
    return frame


def obter_valores_intervalo():
    w = estadoApp["frame_interval"].widgets
    return {
        "hours": w["hour"].get(),
        "minutes": w["min"].get(),
        "seconds": w["sec"].get(),
        "millisecs": w["mil"].get(),
    } 


def obter_tempo_intervalo():
    v = obter_valores_intervalo()
    horas = int(v["hours"] or 0)
    minutos = int(v["minutes"] or 0)
    segundos = int(v["seconds"] or 0)
    milissegundos = int(v["millisecs"] or 0)
    return (horas * 3600 + minutos * 60 + segundos) + milissegundos / 1000

def return_interval():
    return obter_tempo_intervalo()


# ---------------------------------------------------------------------------
# Frame: Click Repeat
# ---------------------------------------------------------------------------

def criar_radio_repeat(frame, fontes, variavel, valor, row, texto, pady_extra):
    rad = ctk.CTkRadioButton(
        frame, text=texto, font=fontes["entry"],
        text_color=COLORS["text"], hover_color=COLORS["hover"],
        fg_color=COLORS["text"], variable=variavel, value=valor
    )
    rad.grid(row=row, column=0, sticky="w", padx=(10, 0), pady=pady_extra)
    return rad


def criar_frame_click_repeat(master, fontes):
    frame = ctk.CTkFrame(master, fg_color=COLORS["frameBg"], border_color=COLORS["border"], border_width=1)

    label_titulo = ctk.CTkLabel(frame, text="[ Click Repeat ]", font=fontes["titulo"], text_color=COLORS["text"])
    label_titulo.grid(row=0, column=0, sticky="w", padx=10, pady=(3, 0))

    # variável compartilhada pelo grupo de radio buttons: 1 = Repeat, 2 = Repeat until stopped
    var_repeat = ctk.IntVar(value=1)

    rad_repeat = criar_radio_repeat(frame, fontes, var_repeat, 1, row=1, texto="Repeat", pady_extra=5)
    rad_repeat_stop = criar_radio_repeat(frame, fontes, var_repeat, 2, row=2, texto="Repeat until stopped", pady_extra=(5, 7))

    frame.widgets = {
        "var_repeat": var_repeat,
        "repeat": rad_repeat,
        "repeat_stop": rad_repeat_stop,
    }
    return frame


def obter_valores_repeat():
    w = estadoApp["frame_repeat"].widgets
    valor = w["var_repeat"].get()
    return {
        "repeat": valor == 1,
        "repeatUntilStopped": valor == 2,
    }


# ---------------------------------------------------------------------------
# Frame: Click Option
# ---------------------------------------------------------------------------

def criar_option_menu(frame, fontes, row, texto, valores):
    label = ctk.CTkLabel(frame, text=texto, font=fontes["entry"], text_color=COLORS["text"])
    label.grid(row=row, column=0, padx=(15, 0), sticky="w")

    combo = ctk.CTkOptionMenu(
        frame, values=valores, width=85,
        fg_color=COLORS["comboFg"], button_color=COLORS["buttonBg"],
        button_hover_color=COLORS["hover"], dropdown_fg_color=COLORS["dropdownBg"],
        dropdown_text_color=COLORS["text"], dropdown_font=fontes["entry"],
        text_color=COLORS["text"]
    )
    combo.grid(row=row, column=1, pady=5)
    return combo


def criar_frame_click_option(master, fontes):
    frame = ctk.CTkFrame(master, fg_color=COLORS["frameBg"], border_color=COLORS["border"], border_width=1)

    label_titulo = ctk.CTkLabel(frame, text="[ Click Option ]", font=fontes["titulo"], text_color=COLORS["text"])
    label_titulo.grid(row=0, column=0, sticky="w", padx=(10, 0), pady=(3, 0))

    cmb_mouse = criar_option_menu(frame, fontes, row=1, texto="Mouse Button", valores=["Left", "Right", "Middle"])
    cmb_type = criar_option_menu(frame, fontes, row=2, texto="Click Type", valores=["Single", "Double"])

    frame.widgets = {
        "mouse": cmb_mouse,
        "type": cmb_type,
    }
    return frame


def obter_valores_option():
    w = estadoApp["frame_option"].widgets
    return {
        "mouseButton": w["mouse"].get(),
        "clickType": w["type"].get(),
    }


def obter_mouse_button():
    return estadoApp["frame_option"].widgets["mouse"].get()


def obter_click_type():
    return estadoApp["frame_option"].widgets["type"].get()


# ---------------------------------------------------------------------------
# Frame: Cursor Position
# ---------------------------------------------------------------------------

def criar_radio_cursor(frame, fontes, variavel, valor, row, texto, pady_extra):
    chb = ctk.CTkRadioButton(
        frame, text=texto, font=fontes["entry"],
        text_color=COLORS["text"], hover_color=COLORS["hover"],
        fg_color=COLORS["text"], variable=variavel, value=valor
    )
    chb.grid(row=row, column=0, padx=(10, 0), pady=pady_extra, sticky="w")
    return chb


def criar_frame_cursor_position(master, fontes):
    frame = ctk.CTkFrame(master, height=100, fg_color=COLORS["frameBg"], border_color=COLORS["border"], border_width=1)

    label_titulo = ctk.CTkLabel(frame, text="[ Cursor Position ]", font=fontes["titulo"], text_color=COLORS["text"])
    label_titulo.grid(row=0, column=0, sticky="w", padx=10, pady=(3, 0))

    var_position = ctk.IntVar(value=1)

    take_position = criar_radio_cursor(frame, fontes, var_position, 1, row=1, texto="Current Mouse Position", pady_extra=5)
    set_position = criar_radio_cursor(frame, fontes, var_position, 2, row=2, texto="Set Location", pady_extra=(5, 7))

    frame.widgets = {
        "var_position": var_position,
        "take_position": take_position,
        "set_position": set_position,
    }
    return frame


def obter_valores_cursor():
    w = estadoApp["frame_cursor"].widgets
    valor = w["var_position"].get()
    return {
        "currentMousePosition": valor == 1,
        "setLocation": valor == 2,
    }


# ---------------------------------------------------------------------------
# Frame: Controller
# ---------------------------------------------------------------------------

estadoController = {"ligado": False}
eventoParada = threading.Event()
eventoParada.set()


def toggle_controller():
    estadoController["ligado"] = not estadoController["ligado"]
    return estadoController["ligado"]


def criar_botao_controller(frame, row, texto, comando, pady_extra, cor_fundo=COLORS["buttonBg"]):
    botao = ctk.CTkButton(
        frame, text=texto, width=180, fg_color=cor_fundo,
        hover_color=COLORS["hover"], text_color=COLORS["text"],
        border_width=1, border_color=COLORS["border"], command=comando
    )
    botao.grid(row=row, column=0, padx=(10, 0), pady=pady_extra, sticky="nse")
    return botao

from evdev.genecodes_py import value
from pyglet.resource import text

def criar_frame_controller(master, fontes, ao_iniciar=None, ao_definir_hotkey=None):
    frame = ctk.CTkFrame(master, height=100, fg_color=COLORS["frameBg"], border_color=COLORS["border"], border_width=1)

    label_titulo = ctk.CTkLabel(frame, text="[ Controller ]", font=fontes["titulo"], text_color=COLORS["text"])
    label_titulo.grid(row=0, column=0, sticky="w", padx=10, pady=(3, 0))

    ligado = {"valor": False}

    def alternar_start():
        ligado["valor"] = not ligado["valor"]
        start_bt.configure(
            text="stop" if ligado["valor"] else "start",
            fg_color=COLORS["buttonBg"] if ligado["valor"] else COLORS["border"],
        )
        if ao_iniciar:
            ao_iniciar()

    start_bt = criar_botao_controller(
        frame, row=1, texto="start", comando=alternar_start,
        pady_extra=(0, 5), cor_fundo=COLORS["border"]
    )
    hotkey_bt = criar_botao_controller(frame, row=2, texto="Hotkey", comando=ao_definir_hotkey, pady_extra=(5, 8))

    frame.widgets = {
        "start_bt": start_bt,
        "hotkey_bt": hotkey_bt,
    }
    return frame


# ---------------------------------------------------------------------------
# App principal
# ---------------------------------------------------------------------------

def ao_clicar_start():
    # exemplo: já dá para pegar tudo pronto, de qualquer frame
    print(obter_valores_intervalo())
    print(obter_valores_repeat())
    print(obter_valores_option())
    print(obter_valores_cursor())
    ligado = toggle_controller()
    print("ligado:", ligado)
    if ligado:
        eventoParada.clear()
        threading.Thread(
            target=auto_click,
            args=(1.0, obter_tempo_intervalo(), inf, str(obter_mouse_button()), eventoParada),
            daemon=True,
        ).start()
    else:
        eventoParada.set()

def ao_clicar_hotkey():
    pass


def configurar_janela(app):
    largura, altura = 440, 315
    largura_tela = app.winfo_screenwidth()
    altura_tela = app.winfo_screenheight()
    x = (largura_tela // 2) - (largura // 2)
    y = (altura_tela // 2) - (altura // 2)
    app.geometry(f"{largura}x{altura}+{x}+{y}")
    app.minsize(largura, altura)
    app.resizable(False, False)

def criar_layout(app, fontes):
    global estadoApp
    estadoApp = {}

    frame = ctk.CTkFrame(app, fg_color=COLORS["bg"])
    frame.pack(fill="both", expand=True, pady=5, padx=5)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)

    vcmd = (app.register(validar_numero), "%P")

    frame_interval = criar_frame_click_interval(frame, fontes, vcmd)
    frame_interval.grid(row=0, column=0, columnspan=2, sticky="new", padx=5, pady=5)

    frame_right = ctk.CTkFrame(frame, fg_color="transparent")
    frame_right.grid(row=1, column=1, sticky="new")
    frame_right.grid_columnconfigure(0, weight=1)

    frame_repeat = criar_frame_click_repeat(frame_right, fontes)
    frame_repeat.grid(row=0, column=0, sticky="new", padx=5, pady=5)

    frame_option = criar_frame_click_option(frame_right, fontes)
    frame_option.grid(row=1, column=0, sticky="new", padx=5, pady=(3, 0))

    frame_left = ctk.CTkFrame(frame, fg_color="transparent")
    frame_left.grid(row=1, column=0, sticky="new")
    frame_left.grid_columnconfigure(0, weight=1)

    frame_cursor = criar_frame_cursor_position(frame_left, fontes)
    frame_cursor.grid(row=0, column=0, sticky="new", padx=5, pady=5)

    estadoApp["frame_interval"] = frame_interval
    estadoApp["frame_repeat"] = frame_repeat
    estadoApp["frame_option"] = frame_option
    estadoApp["frame_cursor"] = frame_cursor

    frame_controller = criar_frame_controller(
        frame_left, fontes,
        ao_iniciar=ao_clicar_start,
        ao_definir_hotkey=ao_clicar_hotkey,
    )
    frame_controller.grid(row=1, column=0, sticky="new", padx=5, pady=5)
    estadoApp["frame_controller"] = frame_controller

    return estadoApp


def criar_app():
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    carregar_fontes_customizadas(assets_dir)

    app = ctk.CTk(fg_color=COLORS["bg"])

    fontes = criar_fontes()  # só dá para criar CTkFont depois do CTk() já criado
    configurar_janela(app)
    criar_layout(app, fontes)

    return app

def run():
    app = criar_app()
    app.mainloop()





if __name__ == "__main__":
    run()
