#!/usr/bin/env python3
"""
Advanced GUI Password Generator — built with Tkinter.
Dark cyberpunk theme, strength meter, clipboard integration, history panel.
"""
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.generator import PasswordGenerator, PasswordConfig
from utils.validators import validate_length, validate_char_types
from utils.clipboard import copy_to_clipboard_via_widget

# ── Palette ───────────────────────────────────────────────────────────────────
BG        = "#0D0D0D"
BG2       = "#141414"
BG3       = "#1C1C1C"
BORDER    = "#2A2A2A"
ACCENT    = "#00FF88"
ACCENT2   = "#00CCFF"
TEXT      = "#E8E8E8"
TEXT_DIM  = "#666666"
RED       = "#FF3B30"
ORANGE    = "#FF9500"
YELLOW    = "#FFD60A"
GREEN     = "#30D158"
BRIGHT_G  = "#00FF88"

STRENGTH_COLORS = ["#FF3B30", "#FF6B35", "#FFD60A", "#34C759", "#00FF88"]
STRENGTH_WIDTHS = [0.2, 0.4, 0.6, 0.8, 1.0]


class PasswordApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🔐 Secure Password Generator")
        self.geometry("780x700")
        self.minsize(700, 620)
        self.configure(bg=BG)
        self.resizable(True, True)

        self._history: list[str] = []
        self._current_password = tk.StringVar(value="")
        self._length_var = tk.IntVar(value=16)
        self._use_upper = tk.BooleanVar(value=True)
        self._use_lower = tk.BooleanVar(value=True)
        self._use_digits = tk.BooleanVar(value=True)
        self._use_symbols = tk.BooleanVar(value=True)
        self._excl_ambiguous = tk.BooleanVar(value=False)
        self._exclude_chars = tk.StringVar(value="")
        self._min_upper = tk.IntVar(value=1)
        self._min_lower = tk.IntVar(value=1)
        self._min_digits = tk.IntVar(value=1)
        self._min_symbols = tk.IntVar(value=1)
        self._batch_count = tk.IntVar(value=1)
        self._copy_flash_after = None

        self._setup_fonts()
        self._build_ui()
        self._generate()   # show a password on launch

    def _setup_fonts(self):
        self.font_mono  = tkfont.Font(family="Courier New", size=20, weight="bold")
        self.font_label = tkfont.Font(family="Helvetica", size=9)
        self.font_head  = tkfont.Font(family="Helvetica", size=11, weight="bold")
        self.font_small = tkfont.Font(family="Helvetica", size=8)
        self.font_btn   = tkfont.Font(family="Helvetica", size=10, weight="bold")

    # ── UI BUILD ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Title bar
        title_frame = tk.Frame(self, bg=BG, pady=12)
        title_frame.pack(fill="x", padx=24)
        tk.Label(title_frame, text="🔐  SECURE PASSWORD GENERATOR",
                 font=("Helvetica", 13, "bold"),
                 bg=BG, fg=ACCENT).pack(side="left")
        tk.Label(title_frame, text="cryptographically secure  ·  zero storage",
                 font=self.font_small, bg=BG, fg=TEXT_DIM).pack(side="right", pady=4)

        # Separator
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # Main content
        content = tk.Frame(self, bg=BG)
        content.pack(fill="both", expand=True, padx=24, pady=16)

        left = tk.Frame(content, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        right = tk.Frame(content, bg=BG, width=220)
        right.pack(side="right", fill="y", padx=(16, 0))
        right.pack_propagate(False)

        self._build_output_panel(left)
        self._build_options_panel(left)
        self._build_history_panel(right)

    def _build_output_panel(self, parent):
        panel = tk.Frame(parent, bg=BG2, bd=0, relief="flat",
                         highlightbackground=BORDER, highlightthickness=1)
        panel.pack(fill="x", pady=(0, 14))

        inner = tk.Frame(panel, bg=BG2, pady=14, padx=16)
        inner.pack(fill="x")

        tk.Label(inner, text="GENERATED PASSWORD", font=self.font_small,
                 bg=BG2, fg=TEXT_DIM, anchor="w").pack(fill="x")

        pwd_frame = tk.Frame(inner, bg=BG2)
        pwd_frame.pack(fill="x", pady=(6, 0))

        self._pwd_label = tk.Label(
            pwd_frame,
            textvariable=self._current_password,
            font=self.font_mono,
            bg=BG2, fg=ACCENT,
            anchor="w", wraplength=460,
            justify="left",
        )
        self._pwd_label.pack(side="left", fill="x", expand=True)

        # Copy button
        self._copy_btn = tk.Button(
            pwd_frame, text="COPY", font=self.font_btn,
            bg=ACCENT, fg=BG, relief="flat", cursor="hand2",
            activebackground=ACCENT2, activeforeground=BG,
            width=7, command=self._copy_password,
        )
        self._copy_btn.pack(side="right", padx=(12, 0))

        # Strength meter
        meter_frame = tk.Frame(inner, bg=BG2)
        meter_frame.pack(fill="x", pady=(12, 0))

        tk.Label(meter_frame, text="STRENGTH", font=self.font_small,
                 bg=BG2, fg=TEXT_DIM).pack(side="left")

        self._strength_label = tk.Label(
            meter_frame, text="", font=self.font_small,
            bg=BG2, fg=GREEN)
        self._strength_label.pack(side="left", padx=(8, 0))

        self._strength_tip = tk.Label(
            meter_frame, text="", font=self.font_small,
            bg=BG2, fg=TEXT_DIM)
        self._strength_tip.pack(side="right")

        bar_bg = tk.Frame(inner, bg=BORDER, height=4)
        bar_bg.pack(fill="x", pady=(4, 0))
        bar_bg.pack_propagate(False)

        self._strength_bar = tk.Frame(bar_bg, bg=GREEN, height=4)
        self._strength_bar.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)

        # Generate button
        gen_btn = tk.Button(
            inner, text="⟳  GENERATE NEW PASSWORD",
            font=self.font_btn, bg=BG3, fg=ACCENT,
            relief="flat", cursor="hand2",
            activebackground=BORDER, activeforeground=ACCENT,
            pady=10, command=self._generate,
            highlightbackground=BORDER, highlightthickness=1,
        )
        gen_btn.pack(fill="x", pady=(14, 0))

    def _build_options_panel(self, parent):
        panel = tk.Frame(parent, bg=BG2,
                         highlightbackground=BORDER, highlightthickness=1)
        panel.pack(fill="both", expand=True)

        inner = tk.Frame(panel, bg=BG2, padx=16, pady=14)
        inner.pack(fill="both", expand=True)

        tk.Label(inner, text="CONFIGURATION", font=self.font_small,
                 bg=BG2, fg=TEXT_DIM, anchor="w").pack(fill="x", pady=(0, 10))

        # Length row
        len_row = tk.Frame(inner, bg=BG2)
        len_row.pack(fill="x", pady=(0, 10))

        tk.Label(len_row, text="Length", font=self.font_label,
                 bg=BG2, fg=TEXT, width=14, anchor="w").pack(side="left")

        self._length_display = tk.Label(
            len_row, textvariable=self._length_var,
            font=("Courier New", 11, "bold"),
            bg=BG2, fg=ACCENT, width=4)
        self._length_display.pack(side="right")

        self._length_slider = tk.Scale(
            len_row, from_=4, to=128,
            orient="horizontal", variable=self._length_var,
            bg=BG2, fg=TEXT, troughcolor=BG3,
            highlightthickness=0, sliderrelief="flat",
            activebackground=ACCENT, showvalue=False,
            command=lambda _: None,
        )
        self._length_slider.pack(side="left", fill="x", expand=True, padx=(8, 8))

        # Character type checkboxes
        types_row = tk.Frame(inner, bg=BG2)
        types_row.pack(fill="x", pady=(0, 10))

        tk.Label(types_row, text="Characters", font=self.font_label,
                 bg=BG2, fg=TEXT, width=14, anchor="w").pack(side="left")

        checks_frame = tk.Frame(types_row, bg=BG2)
        checks_frame.pack(side="left", fill="x")

        for text, var in [
            ("A-Z", self._use_upper),
            ("a-z", self._use_lower),
            ("0-9", self._use_digits),
            ("!@#", self._use_symbols),
        ]:
            cb = tk.Checkbutton(
                checks_frame, text=text, variable=var,
                bg=BG2, fg=TEXT, selectcolor=BG3,
                activebackground=BG2, activeforeground=ACCENT,
                font=self.font_label,
            )
            cb.pack(side="left", padx=(0, 12))

        # Min counts
        mins_row = tk.Frame(inner, bg=BG2)
        mins_row.pack(fill="x", pady=(0, 10))

        tk.Label(mins_row, text="Min of each", font=self.font_label,
                 bg=BG2, fg=TEXT, width=14, anchor="w").pack(side="left")

        for label, var in [
            ("A-Z", self._min_upper),
            ("a-z", self._min_lower),
            ("0-9", self._min_digits),
            ("!@#", self._min_symbols),
        ]:
            tk.Label(mins_row, text=label, font=self.font_small,
                     bg=BG2, fg=TEXT_DIM).pack(side="left")
            sp = tk.Spinbox(
                mins_row, from_=0, to=10, width=3,
                textvariable=var,
                bg=BG3, fg=TEXT, insertbackground=ACCENT,
                relief="flat", font=self.font_small,
                highlightbackground=BORDER, highlightthickness=1,
            )
            sp.pack(side="left", padx=(2, 10))

        # Ambiguous + exclude chars
        extras_row = tk.Frame(inner, bg=BG2)
        extras_row.pack(fill="x", pady=(0, 10))

        tk.Checkbutton(
            extras_row, text="Exclude ambiguous (l, 1, O, 0, I)",
            variable=self._excl_ambiguous,
            bg=BG2, fg=TEXT, selectcolor=BG3,
            activebackground=BG2, activeforeground=ACCENT,
            font=self.font_label,
        ).pack(side="left")

        excl_row = tk.Frame(inner, bg=BG2)
        excl_row.pack(fill="x", pady=(0, 10))

        tk.Label(excl_row, text="Exclude chars", font=self.font_label,
                 bg=BG2, fg=TEXT, width=14, anchor="w").pack(side="left")

        self._excl_entry = tk.Entry(
            excl_row, textvariable=self._exclude_chars,
            bg=BG3, fg=TEXT, insertbackground=ACCENT,
            relief="flat", font=("Courier New", 11),
            highlightbackground=BORDER, highlightthickness=1,
        )
        self._excl_entry.pack(side="left", fill="x", expand=True)

        # Batch row
        batch_row = tk.Frame(inner, bg=BG2)
        batch_row.pack(fill="x")

        tk.Label(batch_row, text="Batch count", font=self.font_label,
                 bg=BG2, fg=TEXT, width=14, anchor="w").pack(side="left")

        tk.Spinbox(
            batch_row, from_=1, to=20, width=4,
            textvariable=self._batch_count,
            bg=BG3, fg=TEXT, insertbackground=ACCENT,
            relief="flat", font=self.font_small,
            highlightbackground=BORDER, highlightthickness=1,
        ).pack(side="left")

        tk.Label(batch_row,
                 text="(generates multiple, stored in history)",
                 font=self.font_small, bg=BG2, fg=TEXT_DIM).pack(side="left", padx=8)

    def _build_history_panel(self, parent):
        tk.Label(parent, text="HISTORY", font=self.font_small,
                 bg=BG, fg=TEXT_DIM, anchor="w").pack(fill="x", pady=(0, 6))

        list_frame = tk.Frame(parent,
                              bg=BG2, highlightbackground=BORDER, highlightthickness=1)
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, bg=BG3)
        scrollbar.pack(side="right", fill="y")

        self._history_list = tk.Listbox(
            list_frame,
            bg=BG2, fg=TEXT_DIM,
            selectbackground=BG3, selectforeground=ACCENT,
            relief="flat", font=("Courier New", 8),
            activestyle="none",
            yscrollcommand=scrollbar.set,
            highlightthickness=0,
        )
        self._history_list.pack(fill="both", expand=True)
        scrollbar.config(command=self._history_list.yview)
        self._history_list.bind("<Double-Button-1>", self._history_copy)

        # History controls
        ctrl = tk.Frame(parent, bg=BG)
        ctrl.pack(fill="x", pady=(6, 0))

        tk.Button(
            ctrl, text="Copy Selected", font=self.font_small,
            bg=BG3, fg=TEXT, relief="flat", cursor="hand2",
            activebackground=BORDER, activeforeground=ACCENT,
            command=self._history_copy,
        ).pack(side="left")

        tk.Button(
            ctrl, text="Clear", font=self.font_small,
            bg=BG3, fg=TEXT_DIM, relief="flat", cursor="hand2",
            activebackground=BORDER, activeforeground=RED,
            command=self._history_clear,
        ).pack(side="right")

    # ── ACTIONS ───────────────────────────────────────────────────────────────

    def _build_config(self) -> PasswordConfig | None:
        ok, err, length = validate_length(str(self._length_var.get()))
        if not ok:
            messagebox.showerror("Invalid Input", err)
            return None

        ok, err = validate_char_types(
            self._use_upper.get(), self._use_lower.get(),
            self._use_digits.get(), self._use_symbols.get(),
        )
        if not ok:
            messagebox.showerror("Invalid Input", err)
            return None

        return PasswordConfig(
            length=length,
            use_uppercase=self._use_upper.get(),
            use_lowercase=self._use_lower.get(),
            use_digits=self._use_digits.get(),
            use_symbols=self._use_symbols.get(),
            exclude_chars=self._exclude_chars.get(),
            exclude_ambiguous=self._excl_ambiguous.get(),
            min_uppercase=self._min_upper.get(),
            min_lowercase=self._min_lower.get(),
            min_digits=self._min_digits.get(),
            min_symbols=self._min_symbols.get(),
        )

    def _generate(self):
        config = self._build_config()
        if config is None:
            return

        gen = PasswordGenerator(config)
        count = max(1, self._batch_count.get())

        passwords = gen.generate_batch(count)
        main_pwd = passwords[0]
        self._current_password.set(main_pwd)

        # Update strength
        score, label, color, tip = PasswordGenerator.evaluate_strength(main_pwd)
        self._strength_label.config(text=label, fg=STRENGTH_COLORS[score])
        self._strength_tip.config(text=tip)
        self._strength_bar.place(relwidth=STRENGTH_WIDTHS[score])
        self._strength_bar.config(bg=STRENGTH_COLORS[score])

        # Add to history
        for pwd in passwords:
            self._history.insert(0, pwd)
            self._history_list.insert(0, pwd[:26] + ("…" if len(pwd) > 26 else ""))

        # Cap history
        if len(self._history) > 50:
            self._history = self._history[:50]
            for i in range(self._history_list.size() - 50):
                self._history_list.delete(tk.END)

    def _copy_password(self):
        pwd = self._current_password.get()
        if not pwd:
            return
        success = copy_to_clipboard_via_widget(pwd, self)
        if success:
            orig = self._copy_btn.cget("text")
            self._copy_btn.config(text="✓ COPIED", bg=GREEN, fg=BG)
            if self._copy_flash_after:
                self.after_cancel(self._copy_flash_after)
            self._copy_flash_after = self.after(
                1800,
                lambda: self._copy_btn.config(text=orig, bg=ACCENT, fg=BG),
            )
        else:
            messagebox.showwarning("Clipboard", "Could not access clipboard.")

    def _history_copy(self, _event=None):
        sel = self._history_list.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx < len(self._history):
            copy_to_clipboard_via_widget(self._history[idx], self)
            self._current_password.set(self._history[idx])

    def _history_clear(self):
        self._history.clear()
        self._history_list.delete(0, tk.END)


def main():
    app = PasswordApp()
    app.mainloop()


if __name__ == "__main__":
    main()