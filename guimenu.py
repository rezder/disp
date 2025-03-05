import tkinter as tk


def addWinMenuItem(parentWin: tk.Toplevel,
                   menu: tk.Menu,
                   titleWin: str,
                   titleMenu: str = None
                   ) -> tuple[tk.Frame, tk.Toplevel]:
    if titleMenu is None:
        titleMenu = titleWin
    w = tk.Toplevel(parentWin)
    w.title(titleWin)
    w.protocol("WM_DELETE_WINDOW", w.withdraw)
    wf = tk.Frame(w)
    wf.pack()
    menu.add_command(label=titleMenu, command=w.deiconify)
    w.withdraw()  # This has to be this late else it will not work
    return wf, w
