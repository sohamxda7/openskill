# Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

import tkinter as tk
from tkinter import filedialog, ttk

from openskill.apifinder.index import load_index, search
from openskill.ide.editor_support import (
    BRACKET_PALETTE,
    analyze_brackets,
    completion_candidates,
    should_show_completion_popup,
    symbol_fragment_bounds,
    syntax_highlight_ranges,
)
from openskill.interpreter.runtime import SkillSession, format_value


class OpenSkillWindow(object):
    def __init__(self, root):
        self.root = root
        self.root.title("OpenSKILL IDE")
        self.query = tk.StringVar()
        self.repl_input = tk.StringVar()
        self.current_path = None
        self.run_session = SkillSession()
        self.catalog_symbols = [entry["symbol"] for entry in load_index()]
        self._completion_popup = None
        self._completion_listbox = None
        self._completion_range = None

        self._build_layout()
        self._refresh_editor_decorations()

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

        ttk.Button(toolbar, text="Run", command=self._run_editor).grid(row=0, column=0, padx=(0, 8))
        ttk.Label(toolbar, text="API Finder").grid(row=0, column=1, padx=(8, 8))
        entry = ttk.Entry(toolbar, textvariable=self.query)
        entry.grid(row=0, column=2, sticky="ew")
        entry.bind("<Return>", self._on_search)
        ttk.Button(toolbar, text="Search", command=self._on_search).grid(row=0, column=3, padx=(8, 0))

        notebook = ttk.Notebook(self.root)
        notebook.grid(row=1, column=0, sticky="nsew", padx=(8, 4), pady=(0, 8))

        editor_frame = ttk.Frame(notebook, padding=8)
        editor_frame.rowconfigure(0, weight=3)
        editor_frame.rowconfigure(1, weight=1)
        editor_frame.columnconfigure(1, weight=1)

        self.line_numbers = tk.Text(
            editor_frame,
            width=5,
            wrap="none",
            padx=4,
            takefocus=0,
            state="disabled",
            background="#f3f4f6",
            foreground="#6b7280",
            relief="flat",
        )
        self.line_numbers.grid(row=0, column=0, sticky="ns")

        self.editor = tk.Text(editor_frame, wrap="none", width=80, undo=True)
        self.editor.grid(row=0, column=1, sticky="nsew")
        self.editor.bind("<KeyRelease>", self._on_editor_key_release)
        self.editor.bind("<ButtonRelease-1>", self._on_editor_changed)
        self.editor.bind("<Configure>", self._on_editor_changed)
        self.editor.bind("<Tab>", self._on_editor_tab)
        self.editor.bind("<Control-space>", self._on_editor_complete)
        self.editor.bind("<Escape>", self._hide_completion_popup)
        self.editor.bind("<Down>", self._completion_select_next)
        self.editor.bind("<Up>", self._completion_select_previous)
        self.editor.bind("<Return>", self._completion_accept)
        self.editor.configure(yscrollcommand=self._sync_editor_scroll)

        self.editor_scrollbar = ttk.Scrollbar(editor_frame, orient="vertical", command=self._on_editor_scrollbar)
        self.editor_scrollbar.grid(row=0, column=2, sticky="ns")

        self.editor.insert(
            "1.0",
            "; OpenSKILL editor\n"
            "(procedure (hello name)\n"
            "  (println (strcat \"Hello, \" name)))\n\n"
            "(hello \"world\")\n",
        )

        self.console = tk.Text(editor_frame, wrap="word", height=12)
        self.console.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(8, 0))
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

        self.editor.tag_configure("keyword", foreground="#1f5fbf")
        self.editor.tag_configure("matching_bracket", background="#fff2a8", foreground="#111827")
        self.editor.tag_configure("unmatched_bracket", foreground="#dc2626")
        for depth, color in enumerate(BRACKET_PALETTE):
            self.editor.tag_configure("bracket_depth_%d" % depth, foreground=color)

    def _editor_text(self):
        return self.editor.get("1.0", "end-1c")

    def _editor_cursor_offset(self):
        return len(self.editor.get("1.0", "insert"))

    def _offset_to_index(self, offset):
        return "1.0+%dc" % offset

    def _sync_editor_scroll(self, first, last):
        self.editor_scrollbar.set(first, last)
        self.line_numbers.yview_moveto(first)

    def _on_editor_scrollbar(self, *args):
        self.editor.yview(*args)
        self.line_numbers.yview(*args)

    def _update_line_numbers(self):
        last_line = int(self.editor.index("end-1c").split(".")[0])
        content = "\n".join(str(number) for number in range(1, last_line + 1))
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", content)
        self.line_numbers.configure(state="disabled")
        self.line_numbers.yview_moveto(self.editor.yview()[0])

    def _highlight_keywords(self):
        self.editor.tag_remove("keyword", "1.0", tk.END)
        text = self._editor_text()
        for start, end, _ in syntax_highlight_ranges(text, self.catalog_symbols, text):
            self.editor.tag_add("keyword", start, end)

    def _highlight_brackets(self):
        text = self._editor_text()
        depth_by_offset, match_by_offset, unmatched_offsets = analyze_brackets(text)
        for depth in range(len(BRACKET_PALETTE)):
            self.editor.tag_remove("bracket_depth_%d" % depth, "1.0", tk.END)
        self.editor.tag_remove("matching_bracket", "1.0", tk.END)
        self.editor.tag_remove("unmatched_bracket", "1.0", tk.END)

        for offset, depth in depth_by_offset.items():
            index = self._offset_to_index(offset)
            self.editor.tag_add("bracket_depth_%d" % (depth % len(BRACKET_PALETTE)), index, "%s+1c" % index)
        for offset in unmatched_offsets:
            index = self._offset_to_index(offset)
            self.editor.tag_add("unmatched_bracket", index, "%s+1c" % index)

        cursor_offset = self._editor_cursor_offset()
        for probe in (cursor_offset, cursor_offset - 1):
            if probe in match_by_offset:
                partner = match_by_offset[probe]
                for offset in (probe, partner):
                    index = self._offset_to_index(offset)
                    self.editor.tag_add("matching_bracket", index, "%s+1c" % index)
                break

        self.editor.tag_raise("matching_bracket")
        self.editor.tag_raise("unmatched_bracket")

    def _refresh_editor_decorations(self):
        self._highlight_keywords()
        self._highlight_brackets()
        self._update_line_numbers()

    def _current_completion_context(self, allow_empty=False):
        text = self._editor_text()
        cursor_offset = self._editor_cursor_offset()
        start, end, fragment = symbol_fragment_bounds(text, cursor_offset)
        if not fragment and not allow_empty:
            return None
        matches = completion_candidates(fragment, self.catalog_symbols, text)
        if not matches:
            return None
        return start, end, fragment, matches

    def _show_completion_popup(self, matches):
        bbox = self.editor.bbox("insert")
        if bbox is None:
            return
        if self._completion_popup is None:
            self._completion_popup = tk.Toplevel(self.root)
            self._completion_popup.wm_overrideredirect(True)
            self._completion_popup.attributes("-topmost", True)
            self._completion_listbox = tk.Listbox(self._completion_popup, exportselection=False, height=8)
            self._completion_listbox.pack(fill="both", expand=True)
            self._completion_listbox.bind("<Double-Button-1>", self._completion_accept)

        self._completion_listbox.delete(0, tk.END)
        for item in matches:
            self._completion_listbox.insert(tk.END, item)
        self._completion_listbox.selection_clear(0, tk.END)
        self._completion_listbox.selection_set(0)
        self._completion_listbox.activate(0)

        x, y, width, height = bbox
        del width
        root_x = self.editor.winfo_rootx()
        root_y = self.editor.winfo_rooty()
        self._completion_popup.geometry("+%d+%d" % (root_x + x, root_y + y + height))
        self._completion_popup.deiconify()

    def _hide_completion_popup(self, event=None):
        del event
        if self._completion_popup is not None:
            self._completion_popup.withdraw()
        self._completion_range = None
        return "break"

    def _refresh_completion_popup(self):
        if self._completion_popup is None or not self._completion_popup.winfo_viewable():
            return
        context = self._current_completion_context(allow_empty=True)
        if context is None:
            self._hide_completion_popup()
            return
        start, end, _, matches = context
        self._completion_range = (start, end)
        self._show_completion_popup(matches)

    def _auto_completion_context(self):
        context = self._current_completion_context()
        if context is None:
            return None
        start, end, fragment, matches = context
        if not should_show_completion_popup(fragment, matches):
            return None
        return start, end, fragment, matches

    def _maybe_show_completion_popup(self):
        context = self._auto_completion_context()
        if context is None:
            self._hide_completion_popup()
            return
        start, end, _, matches = context
        self._completion_range = (start, end)
        self._show_completion_popup(matches)

    def _insert_completion(self, replacement):
        start, end = self._completion_range
        self.editor.delete(self._offset_to_index(start), self._offset_to_index(end))
        self.editor.insert(self._offset_to_index(start), replacement)
        self.editor.mark_set("insert", self._offset_to_index(start + len(replacement)))
        self._hide_completion_popup()
        self._refresh_editor_decorations()

    def _completion_accept(self, event=None):
        del event
        if self._completion_popup is None or not self._completion_popup.winfo_viewable():
            return None
        selection = self._completion_listbox.curselection()
        if not selection:
            return "break"
        self._insert_completion(self._completion_listbox.get(selection[0]))
        return "break"

    def _completion_select_next(self, event=None):
        del event
        if self._completion_popup is None or not self._completion_popup.winfo_viewable():
            return None
        selection = self._completion_listbox.curselection()
        index = selection[0] if selection else 0
        next_index = min(index + 1, self._completion_listbox.size() - 1)
        self._completion_listbox.selection_clear(0, tk.END)
        self._completion_listbox.selection_set(next_index)
        self._completion_listbox.activate(next_index)
        return "break"

    def _completion_select_previous(self, event=None):
        del event
        if self._completion_popup is None or not self._completion_popup.winfo_viewable():
            return None
        selection = self._completion_listbox.curselection()
        index = selection[0] if selection else 0
        next_index = max(index - 1, 0)
        self._completion_listbox.selection_clear(0, tk.END)
        self._completion_listbox.selection_set(next_index)
        self._completion_listbox.activate(next_index)
        return "break"

    def _on_editor_complete(self, event=None):
        del event
        context = self._current_completion_context(allow_empty=True)
        if context is None:
            return "break"
        start, end, fragment, matches = context
        self._completion_range = (start, end)
        if len(matches) == 1 and matches[0] != fragment:
            self._insert_completion(matches[0])
            return "break"
        self._show_completion_popup(matches)
        return "break"

    def _on_editor_tab(self, event=None):
        del event
        if self._completion_popup is not None and self._completion_popup.winfo_viewable():
            return self._completion_accept()
        context = self._current_completion_context()
        if context is None:
            self.editor.insert("insert", "  ")
            self._refresh_editor_decorations()
            return "break"
        start, end, fragment, matches = context
        self._completion_range = (start, end)
        if len(matches) == 1:
            self._insert_completion(matches[0])
            return "break"
        if fragment and matches and matches[0] != fragment:
            self._show_completion_popup(matches)
            return "break"
        self.editor.insert("insert", "  ")
        self._refresh_editor_decorations()
        return "break"

    def _on_editor_changed(self, event=None):
        del event
        self._refresh_editor_decorations()
        self._refresh_completion_popup()

    def _on_editor_key_release(self, event=None):
        self._refresh_editor_decorations()
        if event is None:
            return
        if event.keysym in {"Up", "Down", "Left", "Right", "Return", "Escape", "Tab", "Prior", "Next", "Home", "End"}:
            self._refresh_completion_popup()
            return
        if event.keysym.startswith("Shift") or event.keysym.startswith("Control") or event.keysym.startswith("Alt"):
            return
        if event.keysym in {"BackSpace", "Delete"} or (event.char and event.char.isprintable()):
            self._maybe_show_completion_popup()
            return
        self._refresh_completion_popup()

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
            last_output = None
            if session.output:
                last_output = session.output[-1]
                self._append_console("\n".join(session.output))
                emitted = True
            rendered = format_value(result) if result is not None else None
            if rendered is not None and not (emitted and (result is True or rendered == last_output)):
                self._append_console(rendered)
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
            last_output = None
            if self.run_session.output:
                last_output = self.run_session.output[-1]
                self._append_console("\n".join(self.run_session.output), widget=self.repl_output)
                self.run_session.output[:] = []
                emitted = True
            rendered = format_value(result) if result is not None else None
            if rendered is not None and not (emitted and (result is True or rendered == last_output)):
                self._append_console(rendered, widget=self.repl_output)
        except Exception as exc:
            self._append_console(str(exc), widget=self.repl_output)

    def _open_file(self):
        path = filedialog.askopenfilename(filetypes=[("SKILL files", "*.il *.skill"), ("All files", "*.*")])
        if not path:
            return
        with open(path, "r") as handle:
            content = handle.read()
        self.current_path = path
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", content)
        self._refresh_editor_decorations()
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
