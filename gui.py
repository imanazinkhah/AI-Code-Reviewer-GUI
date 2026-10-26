
import os
import threading
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from reviewer.syntax_checker import check_syntax
from reviewer.quality_checker import check_quality
from reviewer.function_analyzer import analyze_functions
from reviewer.complexity_analyzer import analyze_complexity
from reviewer.security_checker import check_security
from reviewer.report import generate_report
from reviewer.html_report import generate_html_report
from reviewer.ai_reviewer import review_with_ai


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
APP_TITLE = "AI Code Reviewer"

BG = "#0B1020"
SIDEBAR_BG = "#101729"
PANEL_BG = "#151F33"
CARD_BG = "#19253B"
BORDER = "#2A3852"

TEXT = "#E8EEF8"
MUTED = "#93A4BD"
BLUE = "#3B82F6"
BLUE_HOVER = "#2563EB"
CYAN = "#22D3EE"
GREEN = "#34D399"
ORANGE = "#FBBF24"
RED = "#F87171"


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def display_value(value):
    """Convert analysis output into readable text."""
    if value is None:
        return "No results available."

    if isinstance(value, str):
        return value

    if isinstance(value, dict):
        if not value:
            return "No results available."

        return "\n".join(
            f"{key}: {display_value(item)}"
            for key, item in value.items()
        )

    if isinstance(value, (list, tuple, set)):
        if not value:
            return "No issues found."

        return "\n".join(
            f"{index}. {display_value(item)}"
            for index, item in enumerate(value, start=1)
        )

    return str(value)


def count_items(value):
    """Count results without assuming a specific output structure."""
    if value is None:
        return 0

    if isinstance(value, (list, tuple, set, dict)):
        return len(value)

    if isinstance(value, str):
        return 0 if not value.strip() else 1

    return 0


def syntax_is_valid(result):
    """Interpret common syntax-check result formats."""
    if isinstance(result, bool):
        return result

    if isinstance(result, dict):
        for key in ("valid", "is_valid", "success", "syntax_valid"):
            if key in result:
                return bool(result[key])

        for key in ("error", "errors", "exception"):
            if key in result and result[key]:
                return False

        # Unknown dictionary structure: do not assume failure.
        return True

    if isinstance(result, (list, tuple)):
        if not result:
            return True

        # A tuple such as (True, message) or (False, error).
        if isinstance(result[0], bool):
            return result[0]

    if result is None:
        return True

    if isinstance(result, str):
        lowered = result.lower()

        if any(
            phrase in lowered
            for phrase in (
                "syntax error",
                "invalid syntax",
                "syntaxerror",
                "traceback",
            )
        ):
            return False

    return True


def format_score(score):
    """Display a score returned by the existing report module."""
    if score is None:
        return "—"

    if isinstance(score, bool):
        return str(score)

    if isinstance(score, (int, float)):
        if isinstance(score, float):
            return f"{score:.1f}"
        return str(score)

    return str(score)


# --------------------------------------------------
# Main application
# --------------------------------------------------

class AICodeReviewerApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry("1240x800")
        self.minsize(1000, 650)
        self.configure(fg_color=BG)

        self.selected_file = ctk.StringVar(value="")
        self.status_text = ctk.StringVar(value="Ready")
        self.current_view = "Dashboard"
        self.analysis_data = None
        self.is_analyzing = False

        self.nav_buttons = {}
        self.view_frames = {}

        self._build_layout()
        self.show_view("Dashboard")

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_area()
        self._build_status_bar()

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=225,
            corner_radius=0,
            fg_color=SIDEBAR_BG,
            border_width=0,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(20, weight=1)

        # Logo
        logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
        )
        logo_frame.pack(fill="x", padx=18, pady=(24, 28))

        logo = ctk.CTkLabel(
            logo_frame,
            text="AI",
            width=44,
            height=44,
            corner_radius=12,
            fg_color=BLUE,
            text_color="white",
            font=ctk.CTkFont(size=19, weight="bold"),
        )
        logo.pack(side="left")

        logo_text = ctk.CTkFrame(
            logo_frame,
            fg_color="transparent",
        )
        logo_text.pack(side="left", padx=10)

        ctk.CTkLabel(
            logo_text,
            text="Code Reviewer",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT,
        ).pack(anchor="w")

        ctk.CTkLabel(
            logo_text,
            text="PYTHON ANALYSIS",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=MUTED,
        ).pack(anchor="w", pady=(3, 0))

        ctk.CTkLabel(
            self.sidebar,
            text="WORKSPACE",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=MUTED,
        ).pack(anchor="w", padx=22, pady=(0, 10))

        nav_items = [
            ("Dashboard", "⌂"),
            ("Code Quality", "◈"),
            ("Security", "◆"),
            ("Functions", "ƒ"),
            ("AI Review", "✦"),
        ]

        for label, symbol in nav_items:
            button = ctk.CTkButton(
                self.sidebar,
                text=f"   {symbol}    {label}",
                anchor="w",
                height=43,
                corner_radius=9,
                fg_color="transparent",
                hover_color="#202D45",
                text_color=MUTED,
                font=ctk.CTkFont(size=13),
                command=lambda name=label: self.show_view(name),
            )
            button.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[label] = button

        # Bottom information
        bottom = ctk.CTkFrame(
            self.sidebar,
            fg_color=PANEL_BG,
            corner_radius=12,
            border_width=1,
            border_color=BORDER,
        )
        bottom.pack(side="bottom", fill="x", padx=12, pady=16)

        ctk.CTkLabel(
            bottom,
            text="AI-POWERED ANALYSIS",
            text_color=CYAN,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).pack(anchor="w", padx=12, pady=(12, 5))

        ctk.CTkLabel(
            bottom,
            text="Static checks + Gemini review",
            text_color=MUTED,
            font=ctk.CTkFont(size=10),
            wraplength=175,
            justify="left",
        ).pack(anchor="w", padx=12, pady=(0, 12))

    def _build_main_area(self):
        self.main = ctk.CTkFrame(
            self,
            fg_color=BG,
            corner_radius=0,
        )
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        # Top bar
        self.topbar = ctk.CTkFrame(
            self.main,
            fg_color=BG,
            corner_radius=0,
            height=76,
        )
        self.topbar.grid(row=0, column=0, sticky="ew", padx=28)
        self.topbar.grid_columnconfigure(0, weight=1)

        title_area = ctk.CTkFrame(
            self.topbar,
            fg_color="transparent",
        )
        title_area.grid(row=0, column=0, sticky="w", pady=18)

        self.page_title = ctk.CTkLabel(
            title_area,
            text="Dashboard",
            font=ctk.CTkFont(size=23, weight="bold"),
            text_color=TEXT,
        )
        self.page_title.pack(anchor="w")

        self.page_subtitle = ctk.CTkLabel(
            title_area,
            text="Analyze, inspect and improve your Python code.",
            font=ctk.CTkFont(size=11),
            text_color=MUTED,
        )
        self.page_subtitle.pack(anchor="w", pady=(3, 0))

        self.file_badge = ctk.CTkLabel(
            self.topbar,
            text="NO FILE SELECTED",
            text_color=MUTED,
            fg_color=PANEL_BG,
            corner_radius=8,
            padx=12,
            pady=8,
            font=ctk.CTkFont(size=10, weight="bold"),
        )
        self.file_badge.grid(row=0, column=1, sticky="e", pady=20)

        # View container
        self.content = ctk.CTkFrame(
            self.main,
            fg_color=BG,
            corner_radius=0,
        )
        self.content.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=28,
            pady=(0, 14),
        )
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self._build_dashboard()
        self._build_quality_view()
        self._build_security_view()
        self._build_functions_view()
        self._build_ai_view()

    def _build_status_bar(self):
        self.statusbar = ctk.CTkFrame(
            self,
            height=31,
            corner_radius=0,
            fg_color="#0D1424",
            border_width=1,
            border_color=BORDER,
        )
        self.statusbar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.statusbar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.statusbar,
            text="●",
            text_color=GREEN,
            font=ctk.CTkFont(size=10),
        ).grid(row=0, column=0, padx=(14, 6), pady=5)

        ctk.CTkLabel(
            self.statusbar,
            textvariable=self.status_text,
            text_color=MUTED,
            font=ctk.CTkFont(size=10),
        ).grid(row=0, column=1, sticky="w", pady=5)

        ctk.CTkLabel(
            self.statusbar,
            text="AI CODE REVIEWER",
            text_color="#64748B",
            font=ctk.CTkFont(size=9, weight="bold"),
        ).grid(row=0, column=2, padx=14, pady=5)

    # --------------------------------------------------
    # Reusable UI components
    # --------------------------------------------------

    def _make_panel(self, parent, title, subtitle=None):
        panel = ctk.CTkFrame(
            parent,
            fg_color=PANEL_BG,
            corner_radius=14,
            border_width=1,
            border_color=BORDER,
        )

        header = ctk.CTkFrame(
            panel,
            fg_color="transparent",
        )
        header.pack(fill="x", padx=17, pady=(15, 7))

        ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT,
        ).pack(anchor="w")

        if subtitle:
            ctk.CTkLabel(
                header,
                text=subtitle,
                font=ctk.CTkFont(size=10),
                text_color=MUTED,
            ).pack(anchor="w", pady=(4, 0))

        return panel

    def _make_textbox(self, parent, height=240):
        textbox = ctk.CTkTextbox(
            parent,
            height=height,
            corner_radius=10,
            fg_color="#0E1627",
            border_width=1,
            border_color=BORDER,
            text_color=TEXT,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word",
        )
        return textbox

    def _set_text(self, textbox, value):
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("1.0", display_value(value))
        textbox.configure(state="disabled")

    def _make_metric_card(self, parent, title, value, color):
        card = ctk.CTkFrame(
            parent,
            fg_color=CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=BORDER,
        )

        ctk.CTkLabel(
            card,
            text=title.upper(),
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=MUTED,
        ).pack(anchor="w", padx=15, pady=(14, 6))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=color,
        )
        value_label.pack(anchor="w", padx=15, pady=(0, 14))

        return card, value_label

    # --------------------------------------------------
    # Dashboard
    # --------------------------------------------------

    def _build_dashboard(self):
        frame = ctk.CTkScrollableFrame(
            self.content,
            fg_color=BG,
            corner_radius=0,
        )
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="metrics")

        self.view_frames["Dashboard"] = frame

        # File selection panel
        file_panel = self._make_panel(
            frame,
            "Source Code",
            "Select a Python file to start the analysis.",
        )
        file_panel.grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="ew",
            pady=(0, 16),
        )
        file_panel.grid_columnconfigure(0, weight=1)

        file_row = ctk.CTkFrame(
            file_panel,
            fg_color="transparent",
        )
        file_row.pack(fill="x", padx=17, pady=(4, 17))
        file_row.grid_columnconfigure(0, weight=1)

        self.file_entry = ctk.CTkEntry(
            file_row,
            textvariable=self.selected_file,
            height=39,
            placeholder_text="Choose a .py file...",
            fg_color="#0E1627",
            border_color=BORDER,
            text_color=TEXT,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
        )
        self.file_entry.grid(row=0, column=0, sticky="ew", padx=(0, 9))

        self.browse_button = ctk.CTkButton(
            file_row,
            text="Browse",
            width=95,
            height=39,
            fg_color="#26354F",
            hover_color="#344865",
            text_color=TEXT,
            command=self.browse_file,
        )
        self.browse_button.grid(row=0, column=1, padx=(0, 9))

        self.analyze_button = ctk.CTkButton(
            file_row,
            text="▶  Analyze Code",
            width=145,
            height=39,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.start_analysis,
        )
        self.analyze_button.grid(row=0, column=2)

        # Metrics
        metrics = ctk.CTkFrame(frame, fg_color="transparent")
        metrics.grid(
            row=1,
            column=0,
            columnspan=4,
            sticky="ew",
            pady=(0, 16),
        )
        metrics.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="metric_cards")

        metric_specs = [
            ("Quality Score", "—", CYAN),
            ("Quality Issues", "—", ORANGE),
            ("Security Warnings", "—", RED),
            ("Functions", "—", GREEN),
        ]

        self.metric_values = {}

        for index, (title, value, color) in enumerate(metric_specs):
            card, value_label = self._make_metric_card(
                metrics,
                title,
                value,
                color,
            )
            card.grid(
                row=0,
                column=index,
                sticky="ew",
                padx=(0 if index == 0 else 5, 5 if index < 3 else 0),
            )
            self.metric_values[title] = value_label

        # Summary and actions
        lower = ctk.CTkFrame(frame, fg_color="transparent")
        lower.grid(
            row=2,
            column=0,
            columnspan=4,
            sticky="nsew",
        )
        lower.grid_columnconfigure((0, 1), weight=1)
        lower.grid_rowconfigure(0, weight=1)

        summary_panel = self._make_panel(
            lower,
            "Analysis Overview",
            "Summary of the most recent analysis.",
        )
        summary_panel.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 7),
        )

        self.summary_text = self._make_textbox(summary_panel, height=230)
        self.summary_text.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=(0, 14),
        )
        self._set_text(
            self.summary_text,
            "Welcome to AI Code Reviewer.\n\n"
            "1. Select a Python file.\n"
            "2. Click Analyze Code.\n"
            "3. Review the results in the sidebar.\n"
            "4. Open the generated HTML report.",
        )

        actions_panel = self._make_panel(
            lower,
            "Quick Actions",
            "Open detailed results or export your report.",
        )
        actions_panel.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(7, 0),
        )

        action_area = ctk.CTkFrame(
            actions_panel,
            fg_color="transparent",
        )
        action_area.pack(fill="both", expand=True, padx=14, pady=(6, 14))

        self.report_button = ctk.CTkButton(
            action_area,
            text="Open HTML Report",
            height=42,
            fg_color="#26354F",
            hover_color="#344865",
            text_color=TEXT,
            command=self.open_report,
        )
        self.report_button.pack(fill="x", pady=(0, 9))

        ctk.CTkButton(
            action_area,
            text="View Code Quality",
            height=42,
            fg_color="transparent",
            border_width=1,
            border_color=BORDER,
            hover_color="#202D45",
            text_color=TEXT,
            command=lambda: self.show_view("Code Quality"),
        ).pack(fill="x", pady=5)

        ctk.CTkButton(
            action_area,
            text="View Security Analysis",
            height=42,
            fg_color="transparent",
            border_width=1,
            border_color=BORDER,
            hover_color="#202D45",
            text_color=TEXT,
            command=lambda: self.show_view("Security"),
        ).pack(fill="x", pady=5)

        ctk.CTkButton(
            action_area,
            text="View Gemini Review",
            height=42,
            fg_color="transparent",
            border_width=1,
            border_color=BORDER,
            hover_color="#202D45",
            text_color=TEXT,
            command=lambda: self.show_view("AI Review"),
        ).pack(fill="x", pady=5)

    # --------------------------------------------------
    # Detail views
    # --------------------------------------------------

    def _build_quality_view(self):
        frame = ctk.CTkFrame(self.content, fg_color=BG, corner_radius=0)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        self.view_frames["Code Quality"] = frame

        panel = self._make_panel(
            frame,
            "Code Quality Analysis",
            "Issues detected by the existing quality checker.",
        )
        panel.grid(row=0, column=0, sticky="nsew")
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        self.quality_text = self._make_textbox(panel, height=400)
        self.quality_text.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15),
        )
        self._set_text(
            self.quality_text,
            "Run an analysis to view code quality results.",
        )

    def _build_security_view(self):
        frame = ctk.CTkFrame(self.content, fg_color=BG, corner_radius=0)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        self.view_frames["Security"] = frame

        panel = self._make_panel(
            frame,
            "Security Analysis",
            "Potentially unsafe patterns detected in the source code.",
        )
        panel.grid(row=0, column=0, sticky="nsew")

        self.security_text = self._make_textbox(panel, height=400)
        self.security_text.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15),
        )
        self._set_text(
            self.security_text,
            "Run an analysis to view security results.",
        )

    def _build_functions_view(self):
        frame = ctk.CTkFrame(self.content, fg_color=BG, corner_radius=0)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        self.view_frames["Functions"] = frame

        panel = self._make_panel(
            frame,
            "Function Analysis",
            "Functions, parameters and other details from the analyzer.",
        )
        panel.grid(row=0, column=0, sticky="nsew")

        self.functions_text = self._make_textbox(panel, height=400)
        self.functions_text.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15),
        )
        self._set_text(
            self.functions_text,
            "Run an analysis to view function details.",
        )

    def _build_ai_view(self):
        frame = ctk.CTkFrame(self.content, fg_color=BG, corner_radius=0)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        self.view_frames["AI Review"] = frame

        panel = self._make_panel(
            frame,
            "Gemini AI Code Review",
            "AI-generated feedback for readability, maintainability and potential improvements.",
        )
        panel.grid(row=0, column=0, sticky="nsew")

        self.ai_text = self._make_textbox(panel, height=400)
        self.ai_text.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15),
        )
        self._set_text(
            self.ai_text,
            "Gemini's review will appear here after analysis.\n\n"
            "Make sure GEMINI_API_KEY is configured in your environment.",
        )

    # --------------------------------------------------
    # Navigation
    # --------------------------------------------------

    def show_view(self, view_name):
        if view_name not in self.view_frames:
            return

        self.current_view = view_name

        for name, frame in self.view_frames.items():
            frame.grid_remove()

        self.view_frames[view_name].grid()
        self.page_title.configure(text=view_name)

        subtitles = {
            "Dashboard": "Analyze, inspect and improve your Python code.",
            "Code Quality": "Review code quality findings.",
            "Security": "Inspect potential security concerns.",
            "Functions": "Explore functions and complexity results.",
            "AI Review": "Review AI-generated suggestions from Gemini.",
        }

        self.page_subtitle.configure(text=subtitles.get(view_name, ""))

        for name, button in self.nav_buttons.items():
            if name == view_name:
                button.configure(
                    fg_color="#1D3154",
                    text_color="#FFFFFF",
                )
            else:
                button.configure(
                    fg_color="transparent",
                    text_color=MUTED,
                )

    # --------------------------------------------------
    # File selection
    # --------------------------------------------------

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a Python file",
            initialdir=str(BASE_DIR),
            filetypes=[
                ("Python files", "*.py"),
                ("All files", "*.*"),
            ],
        )

        if file_path:
            self.selected_file.set(file_path)
            self.file_badge.configure(
                text=Path(file_path).name.upper(),
                text_color=CYAN,
            )
            self.status_text.set("Python file selected.")

    # --------------------------------------------------
    # Analysis workflow
    # --------------------------------------------------

    def start_analysis(self):
        if self.is_analyzing:
            return

        file_path = self.selected_file.get().strip()

        if not file_path:
            messagebox.showwarning(
                "No file selected",
                "Please select a Python file first.",
            )
            return

        path = Path(file_path)

        if not path.is_file():
            messagebox.showerror(
                "File not found",
                "The selected file does not exist.",
            )
            return

        if path.suffix.lower() != ".py":
            messagebox.showwarning(
                "Invalid file",
                "Please select a .py Python file.",
            )
            return

        self.is_analyzing = True
        self.analyze_button.configure(
            state="disabled",
            text="Analyzing...",
        )
        self.browse_button.configure(state="disabled")
        self.status_text.set("Analyzing source code...")

        self._set_text(
            self.summary_text,
            "Analysis is running...\n\n"
            "Static analysis and Gemini review may take a little time.",
        )

        self._set_text(self.quality_text, "Analysis is running...")
        self._set_text(self.security_text, "Analysis is running...")
        self._set_text(self.functions_text, "Analysis is running...")
        self._set_text(self.ai_text, "Waiting for Gemini review...")

        worker = threading.Thread(
            target=self.run_analysis,
            args=(str(path.resolve()),),
            daemon=True,
        )
        worker.start()

    def run_analysis(self, file_path):
        try:
            syntax_result = check_syntax(file_path)

            if not syntax_is_valid(syntax_result):
                result = {
                    "success": False,
                    "syntax_result": syntax_result,
                    "error": (
                        "The source file contains a syntax error. "
                        "Fix it before running the other analyses."
                    ),
                }

                self.after(
                    0,
                    lambda data=result: self.finish_analysis(data),
                )
                return

            quality_issues = check_quality(file_path)
            function_results = analyze_functions(file_path)
            complexity_results = analyze_complexity(file_path)
            security_issues = check_security(file_path)

            ai_review = None
            ai_error = None

            try:
                ai_review = review_with_ai(file_path)

                if ai_review is None:
                    ai_review = "Gemini returned no review text."

            except Exception as exc:
                ai_error = str(exc)
                ai_review = (
                    "Gemini AI review could not be completed.\n\n"
                    f"Details: {exc}\n\n"
                    "Check your API key, internet connection, model name "
                    "and API quota. The static analysis results are still available."
                )

            # Preserve the existing report module.
            score = generate_report(
                file_path,
                syntax_result,
                quality_issues,
                function_results,
                complexity_results,
                security_issues,
            )

            # The existing HTML generator saves to Path.cwd().
            # Temporarily use the project directory so report.html
            # is generated in the expected location.
            previous_dir = Path.cwd()

            try:
                os.chdir(BASE_DIR)

                generate_html_report(
                    file_path,
                    syntax_result,
                    quality_issues,
                    function_results,
                    complexity_results,
                    security_issues,
                    score,
                    ai_review=ai_review,
                )
            finally:
                os.chdir(previous_dir)

            result = {
                "success": True,
                "file_path": file_path,
                "syntax_result": syntax_result,
                "quality_issues": quality_issues,
                "function_results": function_results,
                "complexity_results": complexity_results,
                "security_issues": security_issues,
                "score": score,
                "ai_review": ai_review,
                "ai_error": ai_error,
                "report_path": BASE_DIR / "report.html",
            }

        except Exception as exc:
            result = {
                "success": False,
                "error": str(exc),
            }

        self.after(
            0,
            lambda data=result: self.finish_analysis(data),
        )

    # --------------------------------------------------
    # Display analysis results
    # --------------------------------------------------

    def finish_analysis(self, result):
        self.is_analyzing = False

        self.analyze_button.configure(
            state="normal",
            text="▶  Analyze Code",
        )
        self.browse_button.configure(state="normal")

        if not result.get("success"):
            error = result.get("error", "An unexpected error occurred.")

            if "syntax_result" in result:
                self._set_text(
                    self.summary_text,
                    "SYNTAX CHECK FAILED\n\n"
                    + display_value(result["syntax_result"])
                    + "\n\n"
                    + error,
                )
                self._set_text(
                    self.quality_text,
                    "Other checks were not run because the syntax check failed.",
                )
                self._set_text(
                    self.security_text,
                    "Other checks were not run because the syntax check failed.",
                )
                self._set_text(
                    self.functions_text,
                    "Other checks were not run because the syntax check failed.",
                )
                self._set_text(
                    self.ai_text,
                    "Gemini review was not run because the syntax check failed.",
                )
                self.status_text.set("Syntax check failed.")
            else:
                self._set_text(
                    self.summary_text,
                    "ANALYSIS FAILED\n\n" + error,
                )
                self.status_text.set("Analysis failed.")

                messagebox.showerror(
                    "Analysis Error",
                    error,
                )

            return

        self.analysis_data = result

        file_path = result["file_path"]
        quality_issues = result["quality_issues"]
        function_results = result["function_results"]
        complexity_results = result["complexity_results"]
        security_issues = result["security_issues"]
        score = result["score"]
        ai_review = result["ai_review"]
        report_path = result["report_path"]

        quality_count = count_items(quality_issues)
        security_count = count_items(security_issues)
        function_count = count_items(function_results)

        self.metric_values["Quality Score"].configure(
            text=format_score(score),
        )
        self.metric_values["Quality Issues"].configure(
            text=str(quality_count),
        )
        self.metric_values["Security Warnings"].configure(
            text=str(security_count),
        )
        self.metric_values["Functions"].configure(
            text=str(function_count),
        )

        summary = (
            "ANALYSIS COMPLETED\n\n"
            f"File: {Path(file_path).name}\n"
            f"Syntax: Valid\n"
            f"Quality issues: {quality_count}\n"
            f"Security warnings: {security_count}\n"
            f"Function analysis entries: {function_count}\n"
            f"Quality score: {format_score(score)}\n\n"
            f"HTML report:\n{report_path}\n\n"
            f"Gemini review: "
            f"{'Unavailable' if result.get('ai_error') else 'Completed'}"
        )

        self._set_text(self.summary_text, summary)

        self._set_text(
            self.quality_text,
            quality_issues if quality_issues else "No quality issues found.",
        )

        self._set_text(
            self.security_text,
            security_issues if security_issues else "No security warnings found.",
        )

        function_text = (
            "FUNCTION ANALYSIS\n\n"
            + display_value(function_results)
            + "\n\nCOMPLEXITY ANALYSIS\n\n"
            + display_value(complexity_results)
        )
        self._set_text(self.functions_text, function_text)

        self._set_text(self.ai_text, ai_review)

        if result.get("ai_error"):
            self.status_text.set(
                "Static analysis completed; Gemini review needs attention."
            )
        else:
            self.status_text.set("Analysis completed successfully.")

        self.file_badge.configure(
            text=Path(file_path).name.upper(),
            text_color=GREEN,
        )

        self.show_view("Dashboard")

    # --------------------------------------------------
    # HTML report
    # --------------------------------------------------

    def open_report(self):
        report_path = BASE_DIR / "report.html"

        if not report_path.is_file():
            messagebox.showinfo(
                "Report not found",
                "No HTML report is available yet. Run an analysis first.",
            )
            return

        try:
            webbrowser.open(report_path.resolve().as_uri())
            self.status_text.set("HTML report opened in your browser.")
        except Exception as exc:
            messagebox.showerror(
                "Could not open report",
                str(exc),
            )


# --------------------------------------------------
# Start application
# --------------------------------------------------

if __name__ == "__main__":
    app = AICodeReviewerApp()
    app.mainloop()
