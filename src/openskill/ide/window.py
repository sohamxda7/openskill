import tkinter as tk
from tkinter import filedialog, ttk

from openskill.apifinder.index import search
from openskill.interpreter.runtime import SkillSession, format_value


class OpenSkillWindow(object):
    def __init__(self, root):
        self.root = root
        self.root.title("OpenSKILL IDE")
        self.query = tk.StringVar()
        self.repl_input = tk.StringVar()
        self.current_path = None
        self.run_session = SkillSession()

        self._build_layout()
        self._highlight_editor()

    def _build_layout(self):
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(1, weight=1)
        self.root.minsize(960, 640)

        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Open", command=self._open_file)
        file_menu.add_command(label="Save", command=self._save_file)
        file_menu.add_command(label="Save As", command=self._save_file_as)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

        toolbar = ttk.Frame(self.root, padding=8)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        toolbar.columnconfigure(2, weight=1)

        ttk.Button(toolbar, text="Run", command=self._run_editor).grid(
            row=0, column=0, padx=(0, 8)
        )
        ttk.Label(toolbar, text="API Finder").grid(row=0, column=1, padx=(8, 8))
        entry = ttk.Entry(toolbar, textvariable=self.query)
        entry.grid(row=0, column=2, sticky="ew")
        entry.bind("<Return>", self._on_search)
        ttk.Button(toolbar, text="Search", command=self._on_search).grid(
            row=0, column=3, padx=(8, 0)
        )

        notebook = ttk.Notebook(self.root)
        notebook.grid(row=1, column=0, sticky="nsew", padx=(8, 4), pady=(0, 8))

        editor_frame = ttk.Frame(notebook, padding=8)
        editor_frame.rowconfigure(0, weight=3)
        editor_frame.rowconfigure(1, weight=1)
        editor_frame.columnconfigure(0, weight=1)
        self.editor = tk.Text(editor_frame, wrap="none", width=80, undo=True)
        self.editor.grid(row=0, column=0, sticky="nsew")
        self.editor.bind("<KeyRelease>", self._highlight_editor)
        self.editor.insert(
            "1.0",
            "; OpenSKILL editor\n"
            "(procedure (hello name)\n"
            "  (println (strcat \"Hello, \" name)))\n\n"
            "(hello \"world\")\n",
        )
        self.console = tk.Text(editor_frame, wrap="word", height=12)
        self.console.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        notebook.add(editor_frame, text="Editor")

        repl_frame = ttk.Frame(notebook, padding=8)
        repl_frame.rowconfigure(0, weight=1)
        repl_frame.columnconfigure(0, weight=1)
        self.repl_output = tk.Text(repl_frame, wrap="word", height=18)
        self.repl_output.grid(row=0, column=0, sticky="nsew")
        repl_entry = ttk.Entry(repl_frame, textvariable=self.repl_input)
        repl_entry.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        repl_entry.bind("<Return>", self._run_repl_line)
        notebook.add(repl_frame, text="REPL")

        side_frame = ttk.Frame(self.root)
        side_frame.grid(row=1, column=1, sticky="nsew", padx=(4, 8), pady=(0, 8))
        side_frame.rowconfigure(0, weight=1)
        side_frame.rowconfigure(1, weight=1)
        side_frame.columnconfigure(0, weight=1)

        results_frame = ttk.LabelFrame(side_frame, text="API Results", padding=8)
        results_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 4))
        results_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        self.results = tk.Text(results_frame, wrap="word", width=40, height=12)
        self.results.grid(row=0, column=0, sticky="nsew")

        log_frame = ttk.LabelFrame(side_frame, text="Console Log", padding=8)
        log_frame.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        self.log = tk.Text(log_frame, wrap="word", width=40, height=8)
        self.log.grid(row=0, column=0, sticky="nsew")
        self.log.insert("1.0", "GUI shell ready.\n")

    def _highlight_editor(self, event=None):
        del event
        keywords = [
            "procedure", "lambda", "setq", "let", "if", "when", "unless",
            "case", "for", "foreach", "while", "progn", "quote", "load",
        ]
        self.editor.tag_remove("keyword", "1.0", tk.END)
        self.editor.tag_configure("keyword", foreground="#1f5fbf")
        for keyword in keywords:
            start = "1.0"
            while True:
                match = self.editor.search(r"\m{0}\M".format(keyword), start, stopindex=tk.END, regexp=True)
                if not match:
                    break
                end = "{0}+{1}c".format(match, len(keyword))
                self.editor.tag_add("keyword", match, end)
                start = end

    def _append_console(self, message, widget=None):
        widget = widget or self.console
        widget.insert(tk.END, message.rstrip() + "\n")
        widget.see(tk.END)

    def _run_editor(self):
        source = self.editor.get("1.0", tk.END)
        session = SkillSession()
        try:
            result = session.eval_text(source, filename=self.current_path or "<editor>")
            self.console.delete("1.0", tk.END)
            emitted = False
            if session.output:
                self._append_console("\n".join(session.output))
                emitted = True
            if result is not None and not (emitted and result is True):
                self._append_console(format_value(result))
            self.log.insert(tk.END, "Run succeeded.\n")
        except Exception as exc:
            self.console.delete("1.0", tk.END)
            self._append_console(str(exc))
            self.log.insert(tk.END, "Run failed.\n")

    def _run_repl_line(self, event=None):
        del event
        line = self.repl_input.get().strip()
        self.repl_input.set("")
        if not line:
            return
        try:
            result = self.run_session.eval_text(line, filename="<gui-repl>")
            emitted = False
            if self.run_session.output:
                self._append_console("\n".join(self.run_session.output), widget=self.repl_output)
                self.run_session.output[:] = []
                emitted = True
            if result is not None and not (emitted and result is True):
                self._append_console(format_value(result), widget=self.repl_output)
        except Exception as exc:
            self._append_console(str(exc), widget=self.repl_output)

    def _open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("SKILL files", "*.il *.skill"), ("All files", "*.*")]
        )
        if not path:
            return
        with open(path, "r") as handle:
            content = handle.read()
        self.current_path = path
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", content)
        self._highlight_editor()
        self.log.insert(tk.END, "Opened {0}\n".format(path))

    def _save_file(self):
        if not self.current_path:
            return self._save_file_as()
        with open(self.current_path, "w") as handle:
            handle.write(self.editor.get("1.0", tk.END))
        self.log.insert(tk.END, "Saved {0}\n".format(self.current_path))

    def _save_file_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".il",
            filetypes=[("SKILL files", "*.il *.skill"), ("All files", "*.*")],
        )
        if not path:
            return
        self.current_path = path
        self._save_file()

    def _on_search(self, event=None):
        del event
        query = self.query.get().strip()
        self.results.delete("1.0", tk.END)
        if not query:
            self.results.insert("1.0", "Enter a symbol or substring to search.\n")
            return

        matches = search(query)
        if not matches:
            self.results.insert("1.0", "No API entries matched '{0}'.\n".format(query))
            self.log.insert(tk.END, "Search miss: {0}\n".format(query))
            return

        for item in matches:
            self.results.insert(
                tk.END,
                "{symbol} [{kind}]\n"
                "Signature: {signature}\n"
                "Returns: {returns}\n"
                "{summary}\n"
                "Example: {example}\n\n".format(
                    symbol=item.get("symbol", ""),
                    kind=item.get("kind", ""),
                    signature=item.get("signature", "n/a"),
                    returns=item.get("returns", "n/a"),
                    summary=item.get("summary", ""),
                    example=item.get("example", ""),
                ),
            )
        self.log.insert(tk.END, "Search hit: {0}\n".format(query))


def launch():
    root = tk.Tk()
    OpenSkillWindow(root)
    root.mainloop()
    return 0
