"""
AutoClicker - versão refatorada em arquivo único.

Em vez de classes (POO), cada "frame" da interface é criado por uma
função que monta os widgets e devolve o frame pronto. Estado que
antes ficava em atributos de instância (self.algumaCoisa) agora fica
em dicionários simples, guardados dentro do frame (frame.widgets) ou
em variáveis normais do escopo onde fazem sentido.
"""

import os
import customtkinter as ctk
import pyglet
from .main import autoClick


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

# Referências dos widgets da janela ativa. As funções `obter*` leem daqui,
# então os callbacks não precisam receber os frames como argumentos.
estadoApp = {}


def criarFontes():
    return {
        "titulo": ctk.CTkFont(family="Rubik", size=15, weight="bold"),
        "label": ctk.CTkFont(family="Rubik", size=12),
        "entry": ctk.CTkFont(family="Rubik", size=13),
    }


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def validarNumero(texto):
    if texto == "":
        return True
    return texto.isdigit() and len(texto) <= 4


def carregarFontesCustomizadas(assetsDir):
    pyglet.font.add_file(os.path.join(assetsDir, "Rubik-Regular.ttf"))
    pyglet.font.add_file(os.path.join(assetsDir, "Rubik-Bold.ttf"))


# ---------------------------------------------------------------------------
# Frame: Click Interval
# ---------------------------------------------------------------------------

def criarCampoIntervalo(frame, fontes, vcmd, row, col, texto):
    padxEntry = (5, 3) if col == 0 else 3
    entry = ctk.CTkEntry(
        frame, placeholder_text="0", width=50,
        validate="key", validatecommand=vcmd, text_color=COLORS["text"]
    )
    entry.grid(row=row, column=col, padx=padxEntry, pady=5)

    label = ctk.CTkLabel(frame, text=texto, font=fontes["label"], text_color=COLORS["text"])
    label.grid(row=row, column=col + 1)
    return entry


def criarFrameClickInterval(master, fontes, vcmd):
    frame = ctk.CTkFrame(master, fg_color=COLORS["frameBg"], border_color=COLORS["border"], border_width=1)

    labelTitulo = ctk.CTkLabel(frame, text="[ Click Interval ]", font=fontes["titulo"], text_color=COLORS["text"])
    labelTitulo.grid(row=0, column=0, columnspan=8, sticky="w", padx=10, pady=(3, 0))

    entryHour = criarCampoIntervalo(frame, fontes, vcmd, row=1, col=0, texto="Hours")
    entryMin = criarCampoIntervalo(frame, fontes, vcmd, row=1, col=2, texto="Minutes")
    entrySec = criarCampoIntervalo(frame, fontes, vcmd, row=1, col=4, texto="Seconds")
    entryMil = criarCampoIntervalo(frame, fontes, vcmd, row=1, col=6, texto="Millisecs")

    # guarda as referências dos widgets no próprio frame, para ler depois
    frame.widgets = {
        "hour": entryHour,
        "min": entryMin,
        "sec": entrySec,
        "mil": entryMil,
    }
    return frame


def obterValoresIntervalo():
    w = estadoApp["frameInterval"].widgets
    return {
        "hours": w["hour"].get(),
        "minutes": w["min"].get(),
        "seconds": w["sec"].get(),
        "millisecs": w["mil"].get(),
    } 


def obterTempoIntervalo():
    v = obterValoresIntervalo()
    horas = int(v["hours"] or 0)
    minutos = int(v["minutes"] or 0)
    segundos = int(v["seconds"] or 0)
    milissegundos = int(v["millisecs"] or 0)
    return (horas * 3600 + minutos * 60 + segundos) + milissegundos / 1000

def returnInterval():
    return obterTempoIntervalo()


# ---------------------------------------------------------------------------
# Frame: Click Repeat
# ---------------------------------------------------------------------------

def criarRadioRepeat(frame, fontes, variavel, valor, row, texto, padyExtra):
    rad = ctk.CTkRadioButton(
        frame, text=texto, font=fontes["entry"],
        text_color=COLORS["text"], hover_color=COLORS["hover"],
        fg_color=COLORS["text"], variable=variavel, value=valor
    )
    rad.grid(row=row, column=0, sticky="w", padx=(10, 0), pady=padyExtra)
    return rad


def criarFrameClickRepeat(master, fontes):
    frame = ctk.CTkFrame(master, fg_color=COLORS["frameBg"], border_color=COLORS["border"], border_width=1)

    labelTitulo = ctk.CTkLabel(frame, text="[ Click Repeat ]", font=fontes["titulo"], text_color=COLORS["text"])
    labelTitulo.grid(row=0, column=0, sticky="w", padx=10, pady=(3, 0))

    # variável compartilhada pelo grupo de radio buttons: 1 = Repeat, 2 = Repeat until stopped
    varRepeat = ctk.IntVar(value=1)

    radRepeat = criarRadioRepeat(frame, fontes, varRepeat, 1, row=1, texto="Repeat", padyExtra=5)
    # radRepeatStop = criarRadioRepeat(frame, fontes, varRepeat, 2, row=2, texto="Repeat until stopped", padyExtra=(5, 7))

    frame.widgets = {
        "varRepeat": varRepeat,
        "repeat": radRepeat,
        # "repeatStop": radRepeatStop,
    }
    return frame


def obterValoresRepeat():
    w = estadoApp["frameRepeat"].widgets
    valor = w["varRepeat"].get()
    return {
        "repeat": valor == 1,
        "repeatUntilStopped": valor == 2,
    }


# ---------------------------------------------------------------------------
# Frame: Click Option
# ---------------------------------------------------------------------------

def criarOptionMenu(frame, fontes, row, texto, valores):
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


def criarFrameClickOption(master, fontes):
    frame = ctk.CTkFrame(master, fg_color=COLORS["frameBg"], border_color=COLORS["border"], border_width=1)

    labelTitulo = ctk.CTkLabel(frame, text="[ Click Option ]", font=fontes["titulo"], text_color=COLORS["text"])
    labelTitulo.grid(row=0, column=0, sticky="w", padx=(10, 0), pady=(3, 0))

    cmbMouse = criarOptionMenu(frame, fontes, row=1, texto="Mouse Button", valores=["Left", "Right", "Middle"])
    cmbType = criarOptionMenu(frame, fontes, row=2, texto="Click Type", valores=["Single", "Double"])

    frame.widgets = {
        "mouse": cmbMouse,
        "type": cmbType,
    }
    return frame


def obterValoresOption():
    w = estadoApp["frameOption"].widgets
    return {
        "mouseButton": w["mouse"].get(),
        "clickType": w["type"].get(),
    }


def obterMouseButton():
    return estadoApp["frameOption"].widgets["mouse"].get()


def obterClickType():
    return estadoApp["frameOption"].widgets["type"].get()


# ---------------------------------------------------------------------------
# Frame: Cursor Position
# ---------------------------------------------------------------------------

def criarCheckboxCursor(frame, row, texto, padyExtra):
    chb = ctk.CTkCheckBox(
        frame, text=texto, border_width=1.5, text_color=COLORS["text"],
        hover_color=COLORS["hover"], fg_color=COLORS["text"], checkmark_color=COLORS["checkmark"]
    )
    chb.grid(row=row, column=0, padx=(10, 0), pady=padyExtra, sticky="w")
    return chb


def criarFrameCursorPosition(master, fontes):
    frame = ctk.CTkFrame(master, height=100, fg_color=COLORS["frameBg"], border_color=COLORS["border"], border_width=1)

    labelTitulo = ctk.CTkLabel(frame, text="[ Cursor Position ]", font=fontes["titulo"], text_color=COLORS["text"])
    labelTitulo.grid(row=0, column=0, sticky="w", padx=10, pady=(3, 0))

    takePosition = criarCheckboxCursor(frame, row=1, texto="Current Mouse Position", padyExtra=5)
    setPosition = criarCheckboxCursor(frame, row=2, texto="Set Location", padyExtra=(5, 7))

    frame.widgets = {
        "takePosition": takePosition,
        "setPosition": setPosition,
    }
    return frame


def obterValoresCursor():
    w = estadoApp["frameCursor"].widgets
    return {
        "currentMousePosition": bool(w["takePosition"].get()),
        "setLocation": bool(w["setPosition"].get()),
    }


# ---------------------------------------------------------------------------
# Frame: Controller
# ---------------------------------------------------------------------------

estadoController = {"ligado": False}


def toggleController():
    estadoController["ligado"] = not estadoController["ligado"]
    return estadoController["ligado"]


def criarBotaoController(frame, row, texto, comando, padyExtra):
    botao = ctk.CTkButton(
        frame, text=texto, width=180, fg_color=COLORS["buttonBg"],
        hover_color=COLORS["hover"], text_color=COLORS["text"],
        border_width=1, border_color=COLORS["border"], command=comando
    )
    botao.grid(row=row, column=0, padx=(10, 0), pady=padyExtra, sticky="nse")
    return botao


def criarFrameController(master, fontes, aoIniciar=None, aoDefinirHotkey=None):
    frame = ctk.CTkFrame(master, height=100, fg_color=COLORS["frameBg"], border_color=COLORS["border"], border_width=1)

    labelTitulo = ctk.CTkLabel(frame, text="[ Controller ]", font=fontes["titulo"], text_color=COLORS["text"])
    labelTitulo.grid(row=0, column=0, sticky="w", padx=10, pady=(3, 0))

    startBt = criarBotaoController(frame, row=1, texto="Start/Stop", comando=aoIniciar, padyExtra=(0, 5))
    hotkeyBt = criarBotaoController(frame, row=2, texto="Hotkey", comando=aoDefinirHotkey, padyExtra=(5, 8))

    frame.widgets = {
        "startBt": startBt,
        "hotkeyBt": hotkeyBt,
    }
    return frame


# ---------------------------------------------------------------------------
# App principal
# ---------------------------------------------------------------------------

def aoClicarStart():
    # exemplo: já dá pra pegar tudo pronto, de qualquer frame
    print(obterValoresIntervalo())
    print(obterValoresRepeat())
    print(obterValoresOption())
    print(obterValoresCursor())
    print("ligado:", toggleController())

    autoClick(1.0, obterTempoIntervalo, 999999, obterMouseButton())

def aoClicarHotkey():
    pass


def configurarJanela(app):
    largura, altura = 440, 315
    larguraTela = app.winfo_screenwidth()
    alturaTela = app.winfo_screenheight()
    x = (larguraTela // 2) - (largura // 2)
    y = (alturaTela // 2) - (altura // 2)
    app.geometry(f"{largura}x{altura}+{x}+{y}")
    app.minsize(largura, altura)
    app.resizable(False, False)

def criarLayout(app, fontes):
    global estadoApp
    estadoApp = {}

    frame = ctk.CTkFrame(app, fg_color=COLORS["bg"])
    frame.pack(fill="both", expand=True, pady=5, padx=5)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)

    vcmd = (app.register(validarNumero), "%P")

    frameInterval = criarFrameClickInterval(frame, fontes, vcmd)
    frameInterval.grid(row=0, column=0, columnspan=2, sticky="new", padx=5, pady=5)

    frameRight = ctk.CTkFrame(frame, fg_color="transparent")
    frameRight.grid(row=1, column=1, sticky="new")
    frameRight.grid_columnconfigure(0, weight=1)

    frameRepeat = criarFrameClickRepeat(frameRight, fontes)
    frameRepeat.grid(row=0, column=0, sticky="new", padx=5, pady=5)

    frameOption = criarFrameClickOption(frameRight, fontes)
    frameOption.grid(row=1, column=0, sticky="new", padx=5, pady=(3, 0))

    frameLeft = ctk.CTkFrame(frame, fg_color="transparent")
    frameLeft.grid(row=1, column=0, sticky="new")
    frameLeft.grid_columnconfigure(0, weight=1)

    frameCursor = criarFrameCursorPosition(frameLeft, fontes)
    frameCursor.grid(row=0, column=0, sticky="new", padx=5, pady=5)

    estadoApp["frameInterval"] = frameInterval
    estadoApp["frameRepeat"] = frameRepeat
    estadoApp["frameOption"] = frameOption
    estadoApp["frameCursor"] = frameCursor

    frameController = criarFrameController(
        frameLeft, fontes,
        aoIniciar=aoClicarStart,
        aoDefinirHotkey=aoClicarHotkey,
    )
    frameController.grid(row=1, column=0, sticky="new", padx=5, pady=5)
    estadoApp["frameController"] = frameController

    return estadoApp


def criarApp():
    assetsDir = os.path.join(os.path.dirname(__file__), "assets")
    carregarFontesCustomizadas(assetsDir)

    app = ctk.CTk(fg_color=COLORS["bg"])

    fontes = criarFontes()  # só dá pra criar CTkFont depois do CTk() já criado
    configurarJanela(app)
    criarLayout(app, fontes)

    return app

def run():
    app = criarApp()
    app.mainloop()


if __name__ == "__main__":
    run()
