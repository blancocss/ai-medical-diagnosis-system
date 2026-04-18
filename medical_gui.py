"""
Medical Diagnosis System - Main GUI
====================================
Improved version: QThread prediction, lazy loading, logging,
modern styling, defensive error handling, PyInstaller-safe paths.
"""

import sys
import os
import logging
import time
from datetime import datetime

# ── PyQt5 ────────────────────────────────────────────────────────────────────
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QCheckBox, QMessageBox, QScrollArea, QProgressBar, QFileDialog,
    QLineEdit, QSplashScreen, QFrame, QSizePolicy, QSpacerItem
)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

# ── Project modules ───────────────────────────────────────────────────────────
from translator_helper import translate_to_arabic
from medical_dictionary import disease_translation, medical_advice, disease_description
from medical_report import generate_medical_report

# =============================================================================
# LOGGING SETUP
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("diagnosis_app.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("MedicalApp")


# =============================================================================
# RESOURCE PATH HELPER  (works both in dev and PyInstaller bundle)
# =============================================================================
def resource_path(relative_path: str) -> str:
    """Return absolute path, compatible with PyInstaller's sys._MEIPASS."""
    try:
        base = sys._MEIPASS          # type: ignore[attr-defined]
    except AttributeError:
        base = os.path.abspath(".")
    return os.path.join(base, relative_path)


# =============================================================================
# BACKGROUND WORKER  – runs heavy work off the main thread
# =============================================================================
class DiagnosisWorker(QThread):
    """
    QThread that performs model loading, prediction, and subprocess call.
    Emits signals so the GUI can update safely from the main thread.
    """
    progress   = pyqtSignal(int)          # 0-100
    finished   = pyqtSignal(dict)         # result dict on success
    error      = pyqtSignal(str)          # human-readable error message

    def __init__(self, model, input_data: list, symptom_count: int):
        super().__init__()
        self._model        = model
        self._input_data   = input_data
        self._symptom_count = symptom_count

    def run(self):
        import subprocess, joblib

        try:
            # ── Prediction ────────────────────────────────────────────────
            t0 = time.perf_counter()
            self.progress.emit(40)

            prediction    = self._model.predict([self._input_data])
            probabilities = self._model.predict_proba([self._input_data])
            disease       = prediction[0]
            probability   = float(max(probabilities[0])) * 100

            pred_ms = (time.perf_counter() - t0) * 1000
            logger.info("Prediction completed in %.1f ms – disease: %s (%.1f%%)",
                        pred_ms, disease, probability)
            self.progress.emit(60)

            # ── RiskAnalyzer subprocess ───────────────────────────────────
            exe_path = resource_path("RiskAnalyzer.exe")
            if not os.path.isfile(exe_path):
                raise FileNotFoundError(f"RiskAnalyzer.exe not found at: {exe_path}")

            t1 = time.perf_counter()
            result = subprocess.run(
                [exe_path],
                input=f"{self._symptom_count}\n{probability}",
                text=True,
                capture_output=True,
                timeout=10,
            )
            sub_ms = (time.perf_counter() - t1) * 1000
            logger.info("RiskAnalyzer completed in %.1f ms", sub_ms)
            self.progress.emit(90)

            if result.returncode != 0:
                raise RuntimeError(
                    f"RiskAnalyzer exited with code {result.returncode}: {result.stderr.strip()}"
                )

            output = result.stdout.strip()
            parts  = output.split("|")
            if len(parts) != 5:
                raise ValueError(f"Unexpected RiskAnalyzer output: '{output}'")

            risk, severity, recommendation, case_type, score = parts

            # Arabic translation (graceful fallback)
            arabic_disease = disease_translation.get(disease, disease)
            advice         = medical_advice.get(disease, recommendation)

            self.progress.emit(100)
            self.finished.emit({
                "disease":          disease,
                "arabic_disease":   arabic_disease,
                "probability":      probability,
                "risk":             risk,
                "severity":         severity,
                "recommendation":   recommendation,
                "case":             case_type,
                "score":            score,
                "advice":           advice,
            })

        except subprocess.TimeoutExpired:
            logger.error("RiskAnalyzer timed out")
            self.error.emit("Risk analysis timed out. Please try again.")
        except FileNotFoundError as e:
            logger.error("File not found: %s", e)
            self.error.emit(str(e))
        except Exception as e:
            logger.exception("Unexpected error during diagnosis")
            self.error.emit(f"Diagnosis error: {e}")


# =============================================================================
# MODEL LOADER THREAD  – loads model and CSV without blocking GUI startup
# =============================================================================
class StartupLoader(QThread):
    """Loads model + dataset in background; emits when ready."""
    ready = pyqtSignal(object, list)   # (model, symptom_columns)
    error = pyqtSignal(str)

    def run(self):
        import joblib, pandas as pd

        t0 = time.perf_counter()
        try:
            # Load dataset to get symptom column names
            csv_path = resource_path("Training.csv")
            if not os.path.isfile(csv_path):
                raise FileNotFoundError(f"Training.csv not found at: {csv_path}")

            data = pd.read_csv(csv_path)
            data = data.loc[:, ~data.columns.str.contains(r'^Unnamed')]
            symptom_cols = [c for c in data.columns if c != "prognosis"]

            # Load ML model
            model_path = resource_path("medical_model.pkl")
            if not os.path.isfile(model_path):
                raise FileNotFoundError(f"medical_model.pkl not found at: {model_path}")

            model = joblib.load(model_path)

            elapsed = (time.perf_counter() - t0) * 1000
            logger.info("Startup load completed in %.1f ms (%d symptoms)", elapsed, len(symptom_cols))
            self.ready.emit(model, symptom_cols)

        except Exception as e:
            logger.exception("Startup load failed")
            self.error.emit(str(e))


# =============================================================================
# MAIN GUI WINDOW
# =============================================================================
APP_STYLESHEET = """
/* ── Global ── */
QWidget {
    background-color: #F0F4F8;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
    color: #1A202C;
}

/* ── Title bar panel ── */
#titlePanel {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1A56A0, stop:1 #2E86C1);
    border-radius: 12px;
    padding: 8px;
}
#titleLabel {
    color: white;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 0.5px;
}
#subtitleLabel {
    color: #BEE3F8;
    font-size: 11px;
}

/* ── Input fields ── */
QLineEdit {
    background: white;
    padding: 9px 14px;
    border-radius: 8px;
    border: 1.5px solid #CBD5E0;
    font-size: 13px;
}
QLineEdit:focus {
    border-color: #2E86C1;
}

/* ── Buttons ── */
QPushButton {
    background-color: #2E86C1;
    color: white;
    padding: 10px 20px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    border: none;
    min-height: 36px;
}
QPushButton:hover  { background-color: #1A6EA0; }
QPushButton:pressed { background-color: #154E72; }
QPushButton:disabled { background-color: #A0AEC0; color: #E2E8F0; }

#resetBtn  { background-color: #718096; }
#resetBtn:hover { background-color: #4A5568; }
#exportBtn { background-color: #38A169; }
#exportBtn:hover { background-color: #276749; }
#reportBtn { background-color: #805AD5; }
#reportBtn:hover { background-color: #553C9A; }

/* ── Progress bar ── */
QProgressBar {
    background: #E2E8F0;
    border-radius: 6px;
    height: 12px;
    text-align: center;
    font-size: 10px;
    color: #2D3748;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #2E86C1, stop:1 #38B2AC);
    border-radius: 6px;
}

/* ── Result panel ── */
#resultPanel {
    background: white;
    border: 2px solid #BEE3F8;
    border-radius: 12px;
    padding: 16px;
}
#resultTitle {
    font-size: 14px;
    font-weight: 700;
    color: #1A56A0;
}

/* ── Scroll area ── */
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical {
    background: #E2E8F0;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #A0AEC0;
    border-radius: 4px;
    min-height: 20px;
}

/* ── Checkboxes ── */
QCheckBox {
    padding: 4px 6px;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px; height: 16px;
    border-radius: 4px;
    border: 1.5px solid #CBD5E0;
    background: white;
}
QCheckBox::indicator:checked {
    background-color: #2E86C1;
    border-color: #2E86C1;
    image: url(data:image/svg+xml;utf8,<svg/>);
}
QCheckBox:hover { background: #EBF8FF; border-radius: 6px; }

/* ── Status label ── */
#statusLabel {
    color: #718096;
    font-size: 11px;
    font-style: italic;
}
"""


class MedicalGUI(QWidget):
    """
    Main application window.
    - Loads data/model in background thread on startup
    - Runs prediction in QThread (non-blocking UI)
    - Full error handling and logging throughout
    """

    def __init__(self):
        super().__init__()
        self.model          = None          # loaded by StartupLoader
        self.symptom_cols   = []
        self.checkboxes     = []
        self.last_result    = None          # cached for export/PDF
        self._worker        = None          # DiagnosisWorker reference

        self._init_window()
        self._build_ui()
        self._start_background_load()

    # ── Window setup ─────────────────────────────────────────────────────────
    def _init_window(self):
        self.setWindowTitle("Medical Diagnosis System")
        self.setMinimumSize(760, 820)
        self.resize(780, 860)
        icon_path = resource_path("medical_icon.ico")
        if os.path.isfile(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setStyleSheet(APP_STYLESHEET)

        # Centre on screen
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width()  - self.width())  // 2,
            (screen.height() - self.height()) // 2,
        )

    # ── UI Construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        # ── Title panel ──────────────────────────────────────────────────────
        title_panel = QFrame()
        title_panel.setObjectName("titlePanel")
        tp_layout = QVBoxLayout(title_panel)
        tp_layout.setContentsMargins(12, 10, 12, 10)
        tp_layout.setSpacing(2)

        lbl_title = QLabel("🩺  Medical Diagnosis System")
        lbl_title.setObjectName("titleLabel")
        lbl_title.setAlignment(Qt.AlignCenter)

        lbl_sub = QLabel("AI-Powered Symptom Analysis & Risk Assessment")
        lbl_sub.setObjectName("subtitleLabel")
        lbl_sub.setAlignment(Qt.AlignCenter)

        tp_layout.addWidget(lbl_title)
        tp_layout.addWidget(lbl_sub)
        root.addWidget(title_panel)

        # ── Patient name ─────────────────────────────────────────────────────
        self.patient_input = QLineEdit()
        self.patient_input.setPlaceholderText("👤  Enter patient name (optional)")
        root.addWidget(self.patient_input)

        # ── Search bar ───────────────────────────────────────────────────────
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍  Search symptoms…")
        self.search_bar.textChanged.connect(self._filter_symptoms)
        root.addWidget(self.search_bar)

        # ── Status label ─────────────────────────────────────────────────────
        self.status_label = QLabel("⏳  Loading model and symptoms…")
        self.status_label.setObjectName("statusLabel")
        root.addWidget(self.status_label)

        # ── Symptom scroll area ──────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(280)
        self._scroll_widget = QWidget()
        self._scroll_layout = QVBoxLayout(self._scroll_widget)
        self._scroll_layout.setSpacing(2)
        self._scroll_layout.setContentsMargins(4, 4, 4, 4)
        self._scroll_layout.addStretch()          # push items to top
        scroll.setWidget(self._scroll_widget)
        root.addWidget(scroll)

        # ── Buttons row ──────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.diagnose_btn = QPushButton("🔬  Diagnose")
        self.diagnose_btn.clicked.connect(self._run_prediction)
        self.diagnose_btn.setEnabled(False)       # enabled after load

        self.reset_btn = QPushButton("🔄  Reset")
        self.reset_btn.setObjectName("resetBtn")
        self.reset_btn.clicked.connect(self._reset_fields)

        self.export_btn = QPushButton("💾  Export")
        self.export_btn.setObjectName("exportBtn")
        self.export_btn.clicked.connect(self._export_result)

        self.report_btn = QPushButton("📄  PDF Report")
        self.report_btn.setObjectName("reportBtn")
        self.report_btn.clicked.connect(self._create_report)

        for btn in (self.diagnose_btn, self.reset_btn, self.export_btn, self.report_btn):
            btn_row.addWidget(btn)
        root.addLayout(btn_row)

        # ── Progress bar ─────────────────────────────────────────────────────
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setFormat("%p%")
        root.addWidget(self.progress)

        # ── Result panel ─────────────────────────────────────────────────────
        result_frame = QFrame()
        result_frame.setObjectName("resultPanel")
        rf_layout = QVBoxLayout(result_frame)
        rf_layout.setContentsMargins(12, 12, 12, 12)
        rf_layout.setSpacing(6)

        res_title = QLabel("Diagnosis Result")
        res_title.setObjectName("resultTitle")
        rf_layout.addWidget(res_title)

        self.result_label = QLabel("No diagnosis yet. Select symptoms and press Diagnose.")
        self.result_label.setWordWrap(True)
        self.result_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.result_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.result_label.setMinimumHeight(130)
        rf_layout.addWidget(self.result_label)

        root.addWidget(result_frame)

    # ── Background startup loader ─────────────────────────────────────────────
    def _start_background_load(self):
        self._loader = StartupLoader()
        self._loader.ready.connect(self._on_startup_ready)
        self._loader.error.connect(self._on_startup_error)
        self._loader.start()

    def _on_startup_ready(self, model, symptom_cols):
        self.model        = model
        self.symptom_cols = symptom_cols
        self._build_checkboxes()
        self.diagnose_btn.setEnabled(True)
        self.status_label.setText(
            f"✅  Ready — {len(symptom_cols)} symptoms loaded."
        )
        self.progress.setValue(0)
        logger.info("GUI ready. %d symptoms available.", len(symptom_cols))

    def _on_startup_error(self, msg: str):
        self.status_label.setText(f"❌  Load error: {msg}")
        QMessageBox.critical(self, "Startup Error",
                             f"Failed to load required files:\n\n{msg}\n\n"
                             "Ensure Training.csv and medical_model.pkl are present.")
        logger.error("Startup error: %s", msg)

    # ── Checkbox management ───────────────────────────────────────────────────
    def _build_checkboxes(self):
        """Populate the scroll area with one checkbox per symptom."""
        # Clear existing (in case of reload)
        for cb in self.checkboxes:
            cb.deleteLater()
        self.checkboxes.clear()

        # Remove the trailing stretch before adding items
        stretch = self._scroll_layout.takeAt(self._scroll_layout.count() - 1)

        for symptom in self.symptom_cols:
            arabic = translate_to_arabic(symptom.replace("_", " "))
            cb = QCheckBox(f"{symptom.replace('_', ' ')}  ({arabic})")
            cb.setProperty("symptom", symptom)   # store raw key
            self._scroll_layout.addWidget(cb)
            self.checkboxes.append(cb)

        self._scroll_layout.addStretch()          # restore bottom stretch

    def _filter_symptoms(self, text: str):
        """Show/hide checkboxes based on search text."""
        text = text.lower()
        for cb in self.checkboxes:
            cb.setVisible(text in cb.text().lower())

    # ── Prediction ────────────────────────────────────────────────────────────
    def _run_prediction(self):
        if self.model is None:
            QMessageBox.warning(self, "Not Ready", "Model is still loading. Please wait.")
            return

        input_data     = [1 if cb.isChecked() else 0 for cb in self.checkboxes]
        symptom_count  = sum(input_data)

        if symptom_count == 0:
            QMessageBox.warning(self, "No Symptoms", "Please select at least one symptom.")
            return

        # Disable controls during processing
        self._set_controls_enabled(False)
        self.result_label.setText("⏳  Analysing symptoms…")
        self.progress.setValue(10)

        self._worker = DiagnosisWorker(self.model, input_data, symptom_count)
        self._worker.progress.connect(self.progress.setValue)
        self._worker.finished.connect(self._on_prediction_done)
        self._worker.error.connect(self._on_prediction_error)
        self._worker.start()

    def _on_prediction_done(self, result: dict):
        self.last_result = result
        self._set_controls_enabled(True)

        d   = result
        txt = (
            f"<b>Disease:</b>  {d['disease']}<br>"
            f"<b>Arabic:</b>   {d['arabic_disease']}<br><br>"
            f"<b>Probability:</b>  {d['probability']:.1f}%<br>"
            f"<b>Risk Level:</b>   {d['risk']}<br>"
            f"<b>Severity:</b>     {d['severity']}<br>"
            f"<b>Case Type:</b>    {d['case']}<br>"
            f"<b>Risk Score:</b>   {d['score']}<br><br>"
            f"<b>Advice:</b>       {d['advice']}<br>"
            f"<b>Recommendation:</b> {d['recommendation']}"
        )
        self.result_label.setText(txt)
        self.result_label.setTextFormat(Qt.RichText)
        logger.info("Result displayed: %s %.1f%%", d['disease'], d['probability'])

    def _on_prediction_error(self, msg: str):
        self._set_controls_enabled(True)
        self.progress.setValue(0)
        self.result_label.setText(f"⚠️  {msg}")
        QMessageBox.warning(self, "Diagnosis Error", msg)

    # ── Reset ─────────────────────────────────────────────────────────────────
    def _reset_fields(self):
        for cb in self.checkboxes:
            cb.setChecked(False)
        self.patient_input.clear()
        self.search_bar.clear()
        self.progress.setValue(0)
        self.result_label.setText("No diagnosis yet. Select symptoms and press Diagnose.")
        self.last_result = None
        self._filter_symptoms("")   # show all symptoms

    # ── Export result ─────────────────────────────────────────────────────────
    def _export_result(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Result", "Run a diagnosis first.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Result", f"diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt)"
        )
        if not path:
            return

        try:
            d = self.last_result
            lines = [
                "Medical Diagnosis Result",
                "=" * 40,
                f"Date:          {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Patient:       {self.patient_input.text() or 'N/A'}",
                f"Disease:       {d['disease']}",
                f"Arabic:        {d['arabic_disease']}",
                f"Probability:   {d['probability']:.1f}%",
                f"Risk Level:    {d['risk']}",
                f"Severity:      {d['severity']}",
                f"Case Type:     {d['case']}",
                f"Risk Score:    {d['score']}",
                f"Advice:        {d['advice']}",
                f"Recommendation:{d['recommendation']}",
            ]
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            QMessageBox.information(self, "Saved", f"Result saved to:\n{path}")
            logger.info("Result exported to %s", path)
        except OSError as e:
            QMessageBox.critical(self, "Save Error", f"Could not write file:\n{e}")
            logger.error("Export failed: %s", e)

    # ── PDF report ────────────────────────────────────────────────────────────
    def _create_report(self):
        if not self.last_result:
            QMessageBox.warning(self, "No Result", "Run a diagnosis first.")
            return

        patient_name = self.patient_input.text().strip() or "Patient"
        d = self.last_result
        try:
            report_file = generate_medical_report(
                patient_name,
                d["disease"],
                d["arabic_disease"],
                d["probability"],
                d["risk"],
                d["severity"],
                d["case"],
                d["score"],
                d["advice"],
                d["recommendation"],
            )
            QMessageBox.information(self, "Report Generated",
                                    f"PDF report saved:\n{report_file}")
            logger.info("PDF report generated: %s", report_file)
        except Exception as e:
            QMessageBox.critical(self, "Report Error", f"Could not generate PDF:\n{e}")
            logger.exception("PDF generation failed")

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _set_controls_enabled(self, enabled: bool):
        for w in (self.diagnose_btn, self.reset_btn, self.export_btn,
                  self.report_btn, self.patient_input, self.search_bar):
            w.setEnabled(enabled)

    def closeEvent(self, event):
        """Graceful shutdown: wait for any running worker thread."""
        if self._worker and self._worker.isRunning():
            logger.info("Waiting for worker thread to finish…")
            self._worker.quit()
            self._worker.wait(2000)
        logger.info("Application closed.")
        event.accept()


# =============================================================================
# ENTRY POINT
# =============================================================================
def main():
    app_start = time.perf_counter()

    app = QApplication(sys.argv)
    app.setApplicationName("Medical Diagnosis System")
    app.setApplicationVersion("2.0")

    # Splash screen
    splash_pix = QPixmap(400, 200)
    splash_pix.fill(QColor("#1A56A0"))
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.showMessage(
        "  Loading Medical Diagnosis System…",
        Qt.AlignBottom | Qt.AlignLeft,
        Qt.white,
    )
    splash.show()
    app.processEvents()

    window = MedicalGUI()
    window.show()
    splash.finish(window)

    elapsed = (time.perf_counter() - app_start) * 1000
    logger.info("Application window shown in %.1f ms", elapsed)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
