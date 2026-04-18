import sys
import os
import joblib
import pandas as pd
import subprocess
import time

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QCheckBox,
    QMessageBox,
    QScrollArea,
    QProgressBar,
    QFileDialog,
    QLineEdit,
    QSplashScreen
)

from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt

from translator_helper import translate_to_arabic

from medical_dictionary import (
    disease_translation,
    medical_advice,
    disease_description
)

from medical_report import generate_medical_report


# =========================
# RESOURCE PATH
# =========================

def resource_path(relative_path):

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# =========================
# GUI CLASS
# =========================

class MedicalGUI(QWidget):

    def __init__(self):

        super().__init__()

        self.model = None
        self.data_loaded = False

        self.setWindowTitle("Medical Diagnosis System")

        self.setGeometry(
            300,
            80,
            720,
            820
        )

        self.setWindowIcon(
            QIcon(
                resource_path(
                    "medical_icon.ico"
                )
            )
        )

        # STYLE

        self.setStyleSheet("""

        QWidget {
            background-color: #f4f7fb;
            font-family: Segoe UI;
            font-size: 14px;
        }

        QPushButton {
            background-color: #2E86C1;
            color: white;
            padding: 12px;
            border-radius: 12px;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #1B4F72;
        }

        QLineEdit {
            padding: 10px;
            border-radius: 10px;
            border: 1px solid #ccc;
        }

        """)

        layout = QVBoxLayout()

        title = QLabel(
            "Medical Diagnosis System"
        )

        title.setFont(
            QFont(
                "Arial",
                18,
                QFont.Bold
            )
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(title)

        # NAME

        self.patient_input = QLineEdit()
        self.patient_input.setPlaceholderText(
            "Enter patient name"
        )
        layout.addWidget(self.patient_input)

        # SEARCH

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(
            "Search symptoms"
        )
        self.search_bar.textChanged.connect(
            self.filter_symptoms
        )
        layout.addWidget(self.search_bar)

        # SCROLL

        scroll = QScrollArea()
        scroll_widget = QWidget()

        self.scroll_layout = QVBoxLayout()
        self.checkboxes = []

        scroll_widget.setLayout(
            self.scroll_layout
        )

        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)

        layout.addWidget(scroll)

        # BUTTONS

        self.button = QPushButton("Diagnose")
        self.button.clicked.connect(self.predict)
        layout.addWidget(self.button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_fields)
        layout.addWidget(self.reset_button)

        self.export_button = QPushButton("Export Result")
        self.export_button.clicked.connect(self.export_result)
        layout.addWidget(self.export_button)

        self.report_button = QPushButton("Generate PDF Report")
        self.report_button.clicked.connect(self.create_report)
        layout.addWidget(self.report_button)

        # PROGRESS

        self.progress = QProgressBar()
        self.progress.setValue(0)

        layout.addWidget(self.progress)

        # RESULT

        self.result_label = QLabel()

        self.result_label.setStyleSheet("""

        background-color: white;
        border: 2px solid #2E86C1;
        border-radius: 15px;
        padding: 15px;

        """)

        layout.addWidget(self.result_label)

        self.setLayout(layout)

        self.load_data_if_needed()

    # =========================

    def load_data_if_needed(self):

        if not self.data_loaded:

            self.progress.setValue(5)

            data = pd.read_csv(
                resource_path("Training.csv")
            )

            data = data.loc[
                :, ~data.columns.str.contains('^Unnamed')
            ]

            self.symptom_columns = list(
                data.columns
            )

            self.symptom_columns.remove(
                "prognosis"
            )

            self.create_checkboxes()

            self.data_loaded = True

            self.progress.setValue(10)

    # =========================

    def create_checkboxes(self):

        self.checkboxes.clear()

        for symptom in self.symptom_columns:

            arabic = translate_to_arabic(
                symptom.replace("_", " ")
            )

            checkbox = QCheckBox(
                f"{symptom} ({arabic})"
            )

            self.scroll_layout.addWidget(
                checkbox
            )

            self.checkboxes.append(
                checkbox
            )

    # =========================

    def load_model_if_needed(self):

        if self.model is None:

            self.progress.setValue(20)

            self.model = joblib.load(
                resource_path(
                    "medical_model.pkl"
                )
            )

            self.progress.setValue(30)

    # =========================

    def filter_symptoms(self):

        text = self.search_bar.text().lower()

        for checkbox in self.checkboxes:

            checkbox.setVisible(
                text in checkbox.text().lower()
            )

    # =========================

    def reset_fields(self):

        for checkbox in self.checkboxes:
            checkbox.setChecked(False)

        self.progress.setValue(0)

        self.result_label.setText("")

    # =========================

    def export_result(self):

        if not hasattr(self, "last_result"):

            QMessageBox.warning(
                self,
                "Warning",
                "No result to export."
            )

            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Result",
            "",
            "Text Files (*.txt)"
        )

        if file_path:

            with open(
                file_path,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    self.result_label.text()
                )

            QMessageBox.information(
                self,
                "Success",
                "Result saved successfully."
            )

    # =========================

    def create_report(self):

        if not hasattr(self, "last_result"):

            QMessageBox.warning(
                self,
                "Error",
                "Run diagnosis first"
            )

            return

        patient_name = self.patient_input.text()

        if patient_name == "":
            patient_name = "Patient"

        report_file = generate_medical_report(
            patient_name,
            self.last_result["disease"],
            self.last_result["arabic_disease"],
            self.last_result["probability"],
            self.last_result["risk"],
            self.last_result["severity"],
            self.last_result["case"],
            self.last_result["score"],
            self.last_result["advice"],
            self.last_result["recommendation"]
        )

        QMessageBox.information(
            self,
            "Success",
            f"Report saved:\n{report_file}"
        )

    # =========================

    def predict(self):

        self.load_model_if_needed()

        input_data = []

        for checkbox in self.checkboxes:

            if checkbox.isChecked():
                input_data.append(1)
            else:
                input_data.append(0)

        if sum(input_data) == 0:

            QMessageBox.warning(
                self,
                "Warning",
                "Please select at least one symptom."
            )

            return

        try:

            self.progress.setValue(50)

            prediction = self.model.predict(
                [input_data]
            )

            probabilities = self.model.predict_proba(
                [input_data]
            )

            disease = prediction[0]

            probability = max(
                probabilities[0]
            ) * 100

            symptom_count = sum(
                input_data
            )

            result = subprocess.run(
                [
                    resource_path(
                        "RiskAnalyzer.exe"
                    )
                ],
                input=f"{symptom_count}\n{probability}",
                text=True,
                capture_output=True,
                timeout=10
            )

            output = result.stdout.strip()

            risk, severity, recommendation, case, score = output.split("|")

            self.progress.setValue(100)

            self.last_result = {
                "disease": disease,
                "probability": probability
            }

            self.result_label.setText(

                f"Disease:\n{disease}\n\n"

                f"Probability:\n{probability:.2f}%\n\n"

                f"Risk Level:\n{risk}\n\n"

                f"Severity:\n{severity}\n\n"

                f"Case Type:\n{case}\n\n"

                f"Risk Score:\n{score}\n\n"

                f"Advice:\n{recommendation}"

            )

        except Exception as e:

            QMessageBox.warning(
                self,
                "Error",
                str(e)
            )


# =========================

app = QApplication(sys.argv)

splash = QSplashScreen(QPixmap())

splash.showMessage(
    "Loading Medical System...",
    Qt.AlignBottom,
    Qt.black
)

splash.show()

app.processEvents()

time.sleep(0.5)

window = MedicalGUI()

window.show()

splash.finish(window)

sys.exit(app.exec_())