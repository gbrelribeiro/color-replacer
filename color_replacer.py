import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading
from PIL import Image, ImageTk
import numpy as np

# ── Pastas padrão ──────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR  = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(INPUT_DIR,  exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Paleta de cores ─────────────────────────────────────────────────────────────
BG        = "#0a0a0a"
SURFACE   = "#111111"
CARD      = "#1a1a1a"
ACCENT    = "#f5c518"   # amarelo
ACCENT2   = "#2563eb"   # azul
TEXT      = "#ffffff"
TEXT_DIM  = "#888888"
SUCCESS   = "#2563eb"
WARNING   = "#ffd166"

# ── Utilitários ────────────────────────────────────────────────────────────────
def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        raise ValueError("Cor inválida")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def replace_color(
    image_path: str,
    from_hex: str,
    to_hex: str,
    tolerance: int
) -> tuple[Image.Image, int]:
    img  = Image.open(image_path).convert("RGBA")
    arr  = np.array(img, dtype=np.int32)

    fr, fg, fb = hex_to_rgb(from_hex)
    tr, tg, tb = hex_to_rgb(to_hex)

    diff = np.sqrt(
        (arr[:, :, 0] - fr) ** 2 +
        (arr[:, :, 1] - fg) ** 2 +
        (arr[:, :, 2] - fb) ** 2
    )
    mask = diff <= tolerance

    result = arr.copy()
    result[mask, 0] = tr
    result[mask, 1] = tg
    result[mask, 2] = tb
    # mantém alpha original

    pixels_replaced = int(mask.sum())
    return Image.fromarray(result.astype(np.uint8), "RGBA"), pixels_replaced

def make_preview(img: Image.Image, size=(320, 320)) -> ImageTk.PhotoImage:
    img.thumbnail(size, Image.LANCZOS)
    w, h = img.size

    checker = Image.new("RGB", (w, h))
    tile = 12
    for y in range(0, h, tile):
        for x in range(0, w, tile):
            c = (40, 40, 40) if (x // tile + y // tile) % 2 == 0 else (55, 55, 55)
            for dy in range(min(tile, h - y)):
                for dx in range(min(tile, w - x)):
                    checker.putpixel((x + dx, y + dy), c)

    if img.mode == "RGBA":
        checker.paste(img, (0, 0), img.split()[3])
    else:
        checker.paste(img.convert("RGB"), (0, 0))
    return ImageTk.PhotoImage(checker)

# ── Aplicação ──────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Trocador de Cor")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._selected_file  = tk.StringVar(value="")
        self._from_hex_var   = tk.StringVar(value="FFFFFF")
        self._to_hex_var     = tk.StringVar(value="000000")
        self._tolerance_var  = tk.IntVar(value=30)
        self._preview_orig   = None
        self._preview_result = None
        self._result_img     = None

        self._build_ui()

    # ── UI ──────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # título
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=20, pady=(20, 12))
        tk.Label(header, text="Trocador de Cor", font=("Segoe UI", 20, "bold"),
                 bg=BG, fg=TEXT).pack(side="left")

        # separador
        tk.Frame(self, bg="#222222", height=1).pack(fill="x", padx=20, pady=(0, 12))

        content = tk.Frame(self, bg=BG)
        content.pack(padx=20, pady=0)

        left = tk.Frame(content, bg=BG)
        left.grid(row=0, column=0, sticky="n", padx=(0, 20))
        self._build_controls(left)

        right = tk.Frame(content, bg=BG)
        right.grid(row=0, column=1, sticky="n")
        self._build_previews(right)

        # barra de status
        self._status = tk.StringVar(value="Pronto.")
        tk.Label(self, textvariable=self._status, font=("Segoe UI", 8),
                 bg=SURFACE, fg=TEXT_DIM, anchor="w", padx=10
                 ).pack(fill="x", side="bottom")

    def _section(self, parent, title):
        f = tk.Frame(parent, bg=CARD, bd=0)
        f.pack(fill="x", pady=(0, 10))
        tk.Label(f, text=title, font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=TEXT).pack(anchor="w", padx=12, pady=(8, 4))
        inner = tk.Frame(f, bg=CARD)
        inner.pack(fill="x", padx=12, pady=(0, 10))
        return inner

    def _build_controls(self, parent):
        # ── seleção de arquivo ─────────────────────────────────────────────────
        sec1 = self._section(parent, "Imagem de entrada")

        browse_row = tk.Frame(sec1, bg=CARD)
        browse_row.pack(fill="x", pady=(0, 4))
        self._btn(browse_row, "📂  Procurar arquivo…", self._browse_file,
                  "#2a2a2a", side="left")

        self._file_label = tk.Label(
            sec1, text="Nenhum arquivo selecionado",
            font=("Consolas", 8), bg=CARD, fg=TEXT_DIM,
            anchor="w", wraplength=260
        )
        self._file_label.pack(fill="x", pady=(2, 0))

        # ── cor de origem ──────────────────────────────────────────────────────
        sec2 = self._section(parent, "Cor de origem (HEX)")

        from_row = tk.Frame(sec2, bg=CARD)
        from_row.pack(fill="x")

        tk.Label(from_row, text="#", font=("Consolas", 13, "bold"),
                 bg=CARD, fg=TEXT_DIM).pack(side="left")

        self._from_entry = tk.Entry(
            from_row, textvariable=self._from_hex_var,
            font=("Consolas", 13, "bold"), width=8,
            bg=SURFACE, fg=TEXT, insertbackground=TEXT,
            bd=0, highlightthickness=1, highlightcolor="#333333",
            highlightbackground="#222222"
        )
        self._from_entry.pack(side="left", padx=4)
        self._from_entry.bind("<KeyRelease>", self._update_from_swatch)

        self._from_swatch = tk.Label(from_row, width=3, bg="#ffffff",
                                     relief="flat", bd=0)
        self._from_swatch.pack(side="left", padx=6, ipady=10)

        self._btn(from_row, "Capturar da imagem",
                  self._pick_from_color, "#2a2a2a", side="left", padx=(8, 0))

        # ── cor de destino ─────────────────────────────────────────────────────
        sec3 = self._section(parent, "Cor de destino (HEX)")

        to_row = tk.Frame(sec3, bg=CARD)
        to_row.pack(fill="x")

        tk.Label(to_row, text="#", font=("Consolas", 13, "bold"),
                 bg=CARD, fg=TEXT_DIM).pack(side="left")

        self._to_entry = tk.Entry(
            to_row, textvariable=self._to_hex_var,
            font=("Consolas", 13, "bold"), width=8,
            bg=SURFACE, fg=TEXT, insertbackground=TEXT,
            bd=0, highlightthickness=1, highlightcolor="#333333",
            highlightbackground="#222222"
        )
        self._to_entry.pack(side="left", padx=4)
        self._to_entry.bind("<KeyRelease>", self._update_to_swatch)

        self._to_swatch = tk.Label(to_row, width=3, bg="#000000",
                                   relief="flat", bd=0)
        self._to_swatch.pack(side="left", padx=6, ipady=10)

        self._btn(to_row, "Capturar da imagem",
                  self._pick_to_color, "#2a2a2a", side="left", padx=(8, 0))

        # ── seta visual de troca ───────────────────────────────────────────────
        arrow_row = tk.Frame(parent, bg=BG)
        arrow_row.pack(fill="x", pady=(0, 4))

        tk.Label(arrow_row,
                 text="  substituir  →",
                 font=("Segoe UI", 9), bg=BG, fg=TEXT_DIM).pack(side="left")

        self._arrow_from = tk.Label(arrow_row, width=3, bg="#ffffff",
                                    relief="flat", bd=0)
        self._arrow_from.pack(side="left", padx=4, ipady=8)

        tk.Label(arrow_row, text="→", font=("Segoe UI", 12, "bold"),
                 bg=BG, fg=TEXT_DIM).pack(side="left", padx=6)

        self._arrow_to = tk.Label(arrow_row, width=3, bg="#000000",
                                  relief="flat", bd=0)
        self._arrow_to.pack(side="left", padx=4, ipady=8)

        # Sincroniza as setas com os swatches ao digitar
        self._from_hex_var.trace_add("write", self._sync_arrows)
        self._to_hex_var.trace_add("write", self._sync_arrows)

        # ── tolerância ────────────────────────────────────────────────────────
        sec4 = self._section(parent, "Tolerância de cor")

        tol_row = tk.Frame(sec4, bg=CARD)
        tol_row.pack(fill="x")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Horizontal.TScale",
                        background=CARD,
                        troughcolor="#222222",
                        sliderthickness=14,
                        sliderrelief="flat")

        self._tol_slider = ttk.Scale(
            tol_row, variable=self._tolerance_var,
            from_=0, to=150,
            orient="horizontal", length=210,
            style="Custom.Horizontal.TScale",
            command=lambda _: self._tol_label.config(
                text=str(self._tolerance_var.get()))
        )
        self._tol_slider.pack(side="left")

        self._tol_label = tk.Label(
            tol_row, text=str(self._tolerance_var.get()),
            font=("Consolas", 11, "bold"),
            bg=CARD, fg=TEXT, width=4
        )
        self._tol_label.pack(side="left")

        tk.Label(sec4,
                 text="0 = exata   30 = padrão   120 = amplo",
                 font=("Segoe UI", 8), bg=CARD, fg=TEXT_DIM
                 ).pack(anchor="w", pady=(2, 0))

        # ── botão processar ───────────────────────────────────────────────────
        self._process_btn = self._btn(parent, "▶  Trocar Cor",
                                      self._process, ACCENT)
        self._process_btn.config(fg="#0a0a0a")
        self._process_btn.pack(fill="x", ipady=8, pady=(6, 0))

        # ── salvar ────────────────────────────────────────────────────────────
        self._save_btn = self._btn(parent, "💾  Salvar PNG",
                                   self._save, ACCENT2)
        self._save_btn.pack(fill="x", ipady=8, pady=(6, 0))
        self._save_btn.config(state="disabled", bg="#2a2a2a", fg="#666666")

    def _build_previews(self, parent):
        for title, attr in [("Original", "_canvas_orig"),
                             ("Resultado", "_canvas_result")]:
            f = tk.Frame(parent, bg=CARD, bd=0)
            f.pack(fill="x", pady=(0, 10))
            tk.Label(f, text=title, font=("Segoe UI", 9, "bold"),
                     bg=CARD, fg=TEXT_DIM).pack(anchor="w", padx=12, pady=(8, 4))
            c = tk.Canvas(f, width=320, height=240,
                          bg=SURFACE, bd=0, highlightthickness=0)
            c.pack(padx=12, pady=(0, 10))
            setattr(self, attr, c)

    @staticmethod
    def _btn(parent, text, cmd, color, side=None, padx=0, **kw):
        b = tk.Button(
            parent, text=text, command=cmd,
            bg=color, fg=TEXT,
            font=("Segoe UI", 9, "bold"),
            relief="flat", bd=0, cursor="hand2",
            activebackground="#3a3a3a", activeforeground=TEXT,
            padx=10, **kw
        )
        if side:
            b.pack(side=side, padx=padx)
        return b

    # ── lógica ──────────────────────────────────────────────────────────────────
    def _browse_file(self):
        path = filedialog.askopenfilename(
            title="Selecionar imagem",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.bmp *.webp *.tiff"),
                ("Todos os arquivos", "*.*")
            ]
        )
        if not path:
            return
        self._selected_file.set(path)
        self._file_label.config(text=os.path.basename(path), fg=TEXT)
        self._load_original_preview(path)
        self._canvas_result.delete("all")
        self._result_img = None
        self._save_btn.config(state="disabled", bg="#2a2a2a", fg="#666666")
        self._status.set(f"Imagem carregada: {os.path.basename(path)}")

    def _load_original_preview(self, path):
        img   = Image.open(path)
        photo = make_preview(img)
        self._preview_orig = photo
        self._canvas_orig.delete("all")
        self._canvas_orig.create_image(160, 120, image=photo)

    def _update_from_swatch(self, _=None):
        val = self._from_hex_var.get().lstrip("#")
        if len(val) == 6:
            try:
                int(val, 16)
                self._from_swatch.config(bg="#" + val)
            except ValueError:
                pass

    def _update_to_swatch(self, _=None):
        val = self._to_hex_var.get().lstrip("#")
        if len(val) == 6:
            try:
                int(val, 16)
                self._to_swatch.config(bg="#" + val)
            except ValueError:
                pass

    def _sync_arrows(self, *_):
        fval = self._from_hex_var.get().lstrip("#")
        tval = self._to_hex_var.get().lstrip("#")
        if len(fval) == 6:
            try:
                int(fval, 16)
                self._arrow_from.config(bg="#" + fval)
            except ValueError:
                pass
        if len(tval) == 6:
            try:
                int(tval, 16)
                self._arrow_to.config(bg="#" + tval)
            except ValueError:
                pass

    def _pick_from_color(self):
        path = self._selected_file.get()
        if not path or not os.path.exists(path):
            messagebox.showwarning("Atenção", "Selecione uma imagem primeiro.")
            return
        ColorPickerWindow(self, path, self._from_hex_var, self._from_swatch)

    def _pick_to_color(self):
        path = self._selected_file.get()
        if not path or not os.path.exists(path):
            messagebox.showwarning("Atenção", "Selecione uma imagem primeiro.")
            return
        ColorPickerWindow(self, path, self._to_hex_var, self._to_swatch)

    def _process(self):
        path = self._selected_file.get()
        if not path or not os.path.exists(path):
            messagebox.showwarning("Atenção", "Selecione uma imagem primeiro.")
            return

        raw_from = self._from_hex_var.get().strip()
        raw_to   = self._to_hex_var.get().strip()
        from_hex = "#" + raw_from.lstrip("#")
        to_hex   = "#" + raw_to.lstrip("#")

        try:
            hex_to_rgb(from_hex)
        except ValueError:
            messagebox.showerror("Erro", "Cor de origem inválida. Use o formato RRGGBB.")
            return
        try:
            hex_to_rgb(to_hex)
        except ValueError:
            messagebox.showerror("Erro", "Cor de destino inválida. Use o formato RRGGBB.")
            return

        self._process_btn.config(state="disabled", text="⏳  Processando…")
        self._status.set("Processando…")
        threading.Thread(
            target=self._run_replacement,
            args=(path, from_hex, to_hex, self._tolerance_var.get()),
            daemon=True
        ).start()

    def _run_replacement(self, path, from_hex, to_hex, tolerance):
        try:
            result, replaced = replace_color(path, from_hex, to_hex, tolerance)
            self._result_img = result
            photo = make_preview(result.copy())
            self._preview_result = photo
            self.after(0, lambda: self._show_result(photo, replaced))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erro", str(e)))
            self.after(0, self._reset_btn)

    def _show_result(self, photo, replaced):
        self._canvas_result.delete("all")
        self._canvas_result.create_image(160, 120, image=photo)
        self._save_btn.config(state="normal", bg=ACCENT2, fg="#ffffff")
        self._status.set(f"✔  Concluído — {replaced:,} pixels substituídos.")
        self._reset_btn()

    def _reset_btn(self):
        self._process_btn.config(state="normal", text="▶  Trocar Cor")

    def _save(self):
        if self._result_img is None:
            return
        src      = self._selected_file.get()
        stem     = os.path.splitext(os.path.basename(src))[0]
        from_hex = self._from_hex_var.get().lstrip("#").upper()
        to_hex   = self._to_hex_var.get().lstrip("#").upper()
        name     = f"{stem}_{from_hex}_para_{to_hex}.png"
        dest     = os.path.join(OUTPUT_DIR, name)

        path = filedialog.asksaveasfilename(
            initialdir=OUTPUT_DIR,
            initialfile=name,
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("Todos", "*.*")]
        )
        if not path:
            return
        self._result_img.save(path)
        self._status.set(f"💾  Salvo em: {path}")
        messagebox.showinfo("Salvo!", f"Arquivo salvo:\n{path}")


# ── Janela de captura de cor ───────────────────────────────────────────────────
class ColorPickerWindow(tk.Toplevel):
    def __init__(self, master, image_path, hex_var, swatch):
        super().__init__(master)
        self.title("Capturar cor")
        self.configure(bg=BG)
        self.resizable(False, False)
        self._hex_var = hex_var
        self._swatch  = swatch

        img = Image.open(image_path).convert("RGBA")
        img.thumbnail((600, 500), Image.LANCZOS)
        self._img_pil   = img
        self._img_photo = ImageTk.PhotoImage(img)

        self._canvas = tk.Canvas(self, width=img.width, height=img.height,
                                 cursor="crosshair", bd=0, highlightthickness=0)
        self._canvas.pack()
        self._canvas.create_image(0, 0, anchor="nw", image=self._img_photo)
        self._canvas.bind("<Button-1>", self._pick)

        # preview do pixel sob o cursor
        self._hover_label = tk.Label(self, text="Passe o mouse e clique para capturar",
                                     font=("Segoe UI", 8), bg=BG, fg=TEXT_DIM)
        self._hover_label.pack(pady=4)
        self._canvas.bind("<Motion>", self._on_hover)

    def _on_hover(self, event):
        x, y = event.x, event.y
        if 0 <= x < self._img_pil.width and 0 <= y < self._img_pil.height:
            r, g, b, _ = self._img_pil.getpixel((x, y))
            hex_color = f"#{r:02X}{g:02X}{b:02X}"
            self._hover_label.config(
                text=f"Pixel ({x}, {y})  →  {hex_color}",
                bg=hex_color,
                fg="#000000" if (r * 299 + g * 587 + b * 114) > 128000 else "#ffffff"
            )

    def _pick(self, event):
        x, y = event.x, event.y
        r, g, b, _ = self._img_pil.getpixel((x, y))
        hex_color = f"{r:02X}{g:02X}{b:02X}"
        self._hex_var.set(hex_color)
        self._swatch.config(bg="#" + hex_color)
        self.destroy()


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()