import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

import nltk

from app.core.nlp_engine import generate_summary, get_top_keywords, paraphrase_summary
from app.ui.theme import DARK_THEME, LIGHT_THEME


class SummarizerMainWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Free Text Summarizer")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)
        self.windowing_system = self.root.tk.call("tk", "windowingsystem")

        self.current_theme = LIGHT_THEME
        self.selected_keywords: set[str] = set()
        self.bullet_mode = False
        self.chip_widgets: list[tk.Button] = []

        self.font_family = self._get_font_family()
        self.font_title = (self.font_family, 22, "bold")
        self.font_main = (self.font_family, 12)
        self.font_small = (self.font_family, 10)

        self._build_ui()
        self.refresh_theme()
        self.update_word_count()
        self.update_output_stats()
        self.rebuild_keyword_chips()

    def _get_font_family(self) -> str:
        if self.windowing_system == "aqua":
            return "SF Pro Text"
        if self.windowing_system == "win32":
            return "Segoe UI"
        return "Helvetica"

    def _build_ui(self) -> None:
        self.card = tk.Frame(self.root, bg=self.current_theme["card_bg"], padx=24, pady=20)
        self.card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.title = tk.Label(
            self.card,
            text="Free Text Summarizer",
            font=self.font_title,
            bg=self.current_theme["card_bg"],
            fg=self.current_theme["fg"],
        )
        self.title.pack(pady=(0, 16))

        self.top_bar = tk.Frame(self.card, bg=self.current_theme["card_bg"])
        self.top_bar.pack(fill=tk.X, pady=(0, 12))

        self._build_mode_controls()
        self._build_length_controls()
        self._build_clear_button()
        self._build_content_panes()
        self._build_bottom_actions()
        self._build_theme_button()

    def _build_mode_controls(self) -> None:
        self.mode_frame = tk.Frame(self.top_bar, bg=self.current_theme["card_bg"])
        self.mode_frame.pack(side=tk.LEFT)

        self.mode_paragraph = tk.Button(
            self.mode_frame,
            text="Paragraph",
            font=(self.font_family, 10, "bold"),
            relief=tk.SOLID,
            borderwidth=0,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=self.set_mode_paragraph,
            bg=self.current_theme["card_bg"],
            fg=self.current_theme["mode_active_fg"],
        )
        self.mode_paragraph.pack(side=tk.LEFT, padx=2)

        self.mode_bullet = tk.Button(
            self.mode_frame,
            text="Bullet Points",
            font=(self.font_family, 10),
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=self.set_mode_bullet,
            bg=self.current_theme["card_bg"],
            fg=self.current_theme["mode_inactive_fg"],
        )
        self.mode_bullet.pack(side=tk.LEFT, padx=2)

    def _build_length_controls(self) -> None:
        self.slider_frame = tk.Frame(self.top_bar, bg=self.current_theme["card_bg"])
        self.slider_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=40)

        slider_row = tk.Frame(self.slider_frame, bg=self.current_theme["card_bg"])
        slider_row.pack(fill=tk.X)

        self.length_title = tk.Label(
            slider_row,
            text="Summary Length:",
            font=self.font_small,
            bg=self.current_theme["card_bg"],
            fg=self.current_theme["fg"],
        )
        self.length_title.pack(side=tk.LEFT, padx=(0, 8))

        self.short_label = tk.Label(
            slider_row,
            text="Short",
            font=self.font_small,
            bg=self.current_theme["card_bg"],
            fg=self.current_theme["label_muted"],
        )
        self.short_label.pack(side=tk.LEFT)

        self.scale_var = tk.DoubleVar(value=0.35)
        self.length_scale = ttk.Scale(
            slider_row,
            from_=0.15,
            to=0.85,
            variable=self.scale_var,
            orient=tk.HORIZONTAL,
            length=220,
            style="TScale",
        )
        self.length_scale.pack(side=tk.LEFT, padx=6)

        self.long_label = tk.Label(
            slider_row,
            text="Long",
            font=self.font_small,
            bg=self.current_theme["card_bg"],
            fg=self.current_theme["label_muted"],
        )
        self.long_label.pack(side=tk.LEFT)

    def _build_clear_button(self) -> None:
        self.clear_btn = tk.Button(
            self.top_bar,
            text="Clear",
            font=(self.font_family, 10, "bold"),
            cursor="hand2",
            command=self.clear_all,
            bg=self.current_theme["card_bg"],
            fg=self.current_theme["trash_fg"],
            bd=0,
            highlightthickness=0,
            padx=10,
            pady=6,
        )
        self.clear_btn.pack(side=tk.RIGHT)

    def _build_content_panes(self) -> None:
        paned = tk.PanedWindow(self.card, orient=tk.HORIZONTAL, bg=self.current_theme["card_bg"], sashwidth=6)
        paned.pack(fill=tk.BOTH, expand=True, pady=8)

        self.left_pane = tk.Frame(paned, bg=self.current_theme["card_bg"])
        self.right_pane = tk.Frame(paned, bg=self.current_theme["card_bg"])
        paned.add(self.left_pane, minsize=320)
        paned.add(self.right_pane, minsize=320)

        self.input_box = scrolledtext.ScrolledText(
            self.left_pane,
            wrap=tk.WORD,
            font=self.font_main,
            height=14,
            bg=self.current_theme["input_bg"],
            fg=self.current_theme["input_fg"],
            insertbackground=self.current_theme["input_fg"],
            relief=tk.FLAT,
            padx=10,
            pady=10,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.current_theme["input_border"],
        )
        self.input_box.pack(fill=tk.BOTH, expand=True)
        self.input_box.bind("<KeyRelease>", lambda _e: self.on_input_changed())

        self.label_keywords = tk.Label(
            self.left_pane,
            text="Select keywords",
            font=self.font_small,
            bg=self.current_theme["card_bg"],
            fg=self.current_theme["fg"],
        )
        self.label_keywords.pack(anchor=tk.W, pady=(8, 4))

        self.chip_frame = tk.Frame(self.left_pane, bg=self.current_theme["card_bg"])
        self.chip_frame.pack(fill=tk.X, pady=(0, 4))

        self.word_label = tk.Label(
            self.left_pane,
            text="0 words",
            font=self.font_small,
            bg=self.current_theme["card_bg"],
            fg=self.current_theme["label_muted"],
        )
        self.word_label.pack(anchor=tk.W)

        self.output_box = scrolledtext.ScrolledText(
            self.right_pane,
            wrap=tk.WORD,
            font=self.font_main,
            height=14,
            bg=self.current_theme["input_bg"],
            fg=self.current_theme["input_fg"],
            insertbackground=self.current_theme["input_fg"],
            relief=tk.FLAT,
            padx=10,
            pady=10,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.current_theme["input_border"],
        )
        self.output_box.pack(fill=tk.BOTH, expand=True)

        self.output_stats_label = tk.Label(
            self.right_pane,
            text="0 sentences • 0 words",
            font=self.font_small,
            bg=self.current_theme["card_bg"],
            fg=self.current_theme["label_muted"],
        )
        self.output_stats_label.pack(anchor=tk.W)

    def _build_bottom_actions(self) -> None:
        self.bottom_bar = tk.Frame(self.card, bg=self.current_theme["card_bg"])
        self.bottom_bar.pack(fill=tk.X, pady=(12, 0))

        self.summarize_btn = tk.Button(
            self.bottom_bar,
            text="Summarize",
            font=(self.font_family, 11, "bold"),
            command=self.do_summarize,
            cursor="hand2",
            padx=32,
            pady=10,
            bg=self.current_theme["accent"],
            fg="white",
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            activebackground=self.current_theme["accent_hover"],
            activeforeground="white",
        )
        self.summarize_btn.pack(side=tk.LEFT, padx=(0, 10), pady=2)

        self.paraphrase_btn = tk.Button(
            self.bottom_bar,
            text="Paraphrase Summary",
            font=(self.font_family, 10),
            command=self.do_paraphrase,
            cursor="hand2",
            padx=20,
            pady=10,
            bg=self.current_theme["card_bg"],
            fg=self.current_theme["accent"],
            relief=tk.FLAT,
            bd=1,
            highlightbackground=self.current_theme["accent"],
            highlightthickness=1,
            highlightcolor=self.current_theme["accent"],
        )
        self.paraphrase_btn.pack(side=tk.LEFT, padx=5)

        self.download_btn = tk.Button(
            self.bottom_bar,
            text="Save",
            font=(self.font_family, 10, "bold"),
            cursor="hand2",
            command=self.do_download,
            bg=self.current_theme["card_bg"],
            fg=self.current_theme["fg"],
            bd=0,
            highlightthickness=0,
            padx=10,
            pady=6,
        )
        self.download_btn.pack(side=tk.RIGHT, padx=4)

        self.copy_btn = tk.Button(
            self.bottom_bar,
            text="Copy",
            font=(self.font_family, 10, "bold"),
            cursor="hand2",
            command=self.do_copy,
            bg=self.current_theme["card_bg"],
            fg=self.current_theme["fg"],
            bd=0,
            highlightthickness=0,
            padx=10,
            pady=6,
        )
        self.copy_btn.pack(side=tk.RIGHT)

    def _build_theme_button(self) -> None:
        self.theme_btn = tk.Button(
            self.card,
            text="Toggle Theme",
            font=self.font_small,
            command=self.toggle_theme,
            cursor="hand2",
            bg=self.current_theme["card_bg"],
            fg=self.current_theme["label_muted"],
            bd=0,
            highlightthickness=0,
            padx=10,
            pady=4,
        )
        self.theme_btn.pack(anchor=tk.E, pady=(8, 0))

    def on_input_changed(self) -> None:
        self.update_word_count()
        self.rebuild_keyword_chips()

    def get_num_sentences(self) -> int:
        return max(2, int(5 + self.scale_var.get() * 15))

    def set_mode_paragraph(self) -> None:
        self.bullet_mode = False
        self.mode_paragraph.config(relief=tk.SOLID, borderwidth=0, font=(self.font_family, 10, "bold"))
        self.mode_bullet.config(relief=tk.FLAT, font=(self.font_family, 10))
        self.refresh_theme()

    def set_mode_bullet(self) -> None:
        self.bullet_mode = True
        self.mode_bullet.config(relief=tk.SOLID, borderwidth=0, font=(self.font_family, 10, "bold"))
        self.mode_paragraph.config(relief=tk.FLAT, font=(self.font_family, 10))
        self.refresh_theme()

    def clear_all(self) -> None:
        self.input_box.delete("1.0", tk.END)
        self.output_box.delete("1.0", tk.END)
        self.selected_keywords.clear()
        self.update_word_count()
        self.update_output_stats()
        self.rebuild_keyword_chips()

    def do_summarize(self) -> None:
        text = self.input_box.get("1.0", tk.END)
        if not text.strip():
            return

        summary = generate_summary(
            text,
            self.get_num_sentences(),
            bullet_mode=self.bullet_mode,
            boost_keywords=sorted(self.selected_keywords) if self.selected_keywords else None,
        )
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, summary)
        self.update_output_stats()

    def do_paraphrase(self) -> None:
        text = self.output_box.get("1.0", tk.END)
        if not text.strip():
            return

        rewritten = paraphrase_summary(text)
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, rewritten)
        self.update_output_stats()

    def do_download(self) -> None:
        text = self.output_box.get("1.0", tk.END)
        if not text.strip():
            messagebox.showinfo("Save Summary", "No summary to save.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return

        with open(path, "w", encoding="utf-8") as file:
            file.write(text)
        messagebox.showinfo("Save Summary", "Summary saved.")

    def do_copy(self) -> None:
        text = self.output_box.get("1.0", tk.END)
        if not text:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)

    def rebuild_keyword_chips(self) -> None:
        for widget in self.chip_widgets:
            widget.destroy()
        self.chip_widgets.clear()

        text = self.input_box.get("1.0", tk.END)
        keywords = get_top_keywords(text, top_n=8)
        self.selected_keywords.intersection_update(keywords)

        for keyword in keywords:
            selected = keyword in self.selected_keywords
            button = tk.Button(
                self.chip_frame,
                text=keyword,
                font=self.font_small,
                cursor="hand2",
                relief=tk.FLAT,
                bd=0,
                padx=10,
                pady=4,
                bg=self.current_theme["chip_selected_bg"] if selected else self.current_theme["chip_bg"],
                fg=self.current_theme["fg"],
                highlightthickness=1,
                highlightbackground=(
                    self.current_theme["chip_selected_border"] if selected else self.current_theme["chip_border"]
                ),
                command=lambda kw=keyword: self.toggle_keyword(kw),
            )
            button.pack(side=tk.LEFT, padx=4, pady=4)
            self.chip_widgets.append(button)

    def toggle_keyword(self, keyword: str) -> None:
        if keyword in self.selected_keywords:
            self.selected_keywords.remove(keyword)
        else:
            self.selected_keywords.add(keyword)
        self.rebuild_keyword_chips()

    def update_word_count(self) -> None:
        text = self.input_box.get("1.0", tk.END)
        self.word_label.config(text=f"{len(text.split())} words")

    def update_output_stats(self) -> None:
        text = self.output_box.get("1.0", tk.END).strip()
        if not text:
            self.output_stats_label.config(text="0 sentences • 0 words")
            return

        sentences = len(nltk.sent_tokenize(text))
        words = len(text.split())
        self.output_stats_label.config(text=f"{sentences} sentences • {words} words")

    def toggle_theme(self) -> None:
        self.current_theme = DARK_THEME if self.current_theme is LIGHT_THEME else LIGHT_THEME
        self.refresh_theme()

    def refresh_theme(self) -> None:
        theme = self.current_theme
        self.root.configure(bg=theme["bg"])

        self.card.configure(bg=theme["card_bg"])
        self.title.configure(bg=theme["card_bg"], fg=theme["fg"])
        self.top_bar.configure(bg=theme["card_bg"])
        self.mode_frame.configure(bg=theme["card_bg"])
        self.slider_frame.configure(bg=theme["card_bg"])
        self.bottom_bar.configure(bg=theme["card_bg"])
        self.left_pane.configure(bg=theme["card_bg"])
        self.right_pane.configure(bg=theme["card_bg"])
        self.chip_frame.configure(bg=theme["card_bg"])

        self.mode_paragraph.configure(
            bg=theme["card_bg"],
            fg=theme["mode_active_fg"] if not self.bullet_mode else theme["mode_inactive_fg"],
        )
        self.mode_bullet.configure(
            bg=theme["card_bg"],
            fg=theme["mode_inactive_fg"] if not self.bullet_mode else theme["mode_active_fg"],
        )

        self.length_title.configure(bg=theme["card_bg"], fg=theme["fg"])
        self.short_label.configure(bg=theme["card_bg"], fg=theme["label_muted"])
        self.long_label.configure(bg=theme["card_bg"], fg=theme["label_muted"])

        self.clear_btn.configure(
            bg=theme["card_bg"],
            fg=theme["trash_fg"],
            activebackground=theme["input_bg"],
            activeforeground=theme["fg"],
        )

        self.input_box.configure(
            bg=theme["input_bg"],
            fg=theme["input_fg"],
            insertbackground=theme["input_fg"],
            highlightbackground=theme["input_border"],
        )
        self.output_box.configure(
            bg=theme["input_bg"],
            fg=theme["input_fg"],
            insertbackground=theme["input_fg"],
            highlightbackground=theme["input_border"],
        )

        self.label_keywords.configure(bg=theme["card_bg"], fg=theme["fg"])
        self.word_label.configure(bg=theme["card_bg"], fg=theme["label_muted"])
        self.output_stats_label.configure(bg=theme["card_bg"], fg=theme["label_muted"])

        self.summarize_btn.configure(
            bg=theme["accent"],
            fg="white",
            activebackground=theme["accent_hover"],
            activeforeground="white",
        )
        self.paraphrase_btn.configure(
            bg=theme["card_bg"],
            fg=theme["accent"],
            activebackground=theme["accent_light"],
            activeforeground=theme["accent"],
            highlightbackground=theme["accent"],
            highlightcolor=theme["accent"],
        )
        self.copy_btn.configure(
            bg=theme["card_bg"],
            fg=theme["fg"],
            activebackground=theme["input_bg"],
            activeforeground=theme["accent"],
        )
        self.download_btn.configure(
            bg=theme["card_bg"],
            fg=theme["fg"],
            activebackground=theme["input_bg"],
            activeforeground=theme["accent"],
        )
        self.theme_btn.configure(bg=theme["card_bg"], fg=theme["label_muted"])

        for button in self.chip_widgets:
            keyword = button.cget("text")
            selected = keyword in self.selected_keywords
            button.configure(
                bg=theme["chip_selected_bg"] if selected else theme["chip_bg"],
                fg=theme["fg"],
                activebackground=theme["chip_selected_bg"] if selected else theme["chip_bg"],
                highlightbackground=theme["chip_selected_border"] if selected else theme["chip_border"],
            )

        try:
            ttk.Style().configure("TScale", troughcolor=theme["slider_trough"])
        except Exception:
            pass


def run_app() -> None:
    root = tk.Tk()
    SummarizerMainWindow(root)
    root.mainloop()
