import sys
import os

# Use the xqt compatibility layer for PyQt/PySide
from ezdxf.addons.xqt import QtWidgets, QtCore

# Import from the main script to create the drawing if it doesn't exist
from main import create_dxf_drawing
from gemini_client import get_gemini_response
from drawing_processor import process_drawing_commands

# ezdxf imports
import ezdxf
from ezdxf import recover
from ezdxf.addons.drawing.qtviewer import CADViewer
from ezdxf.addons.drawing.config import Configuration

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAD Generator")
        self.setGeometry(100, 100, 1200, 800)

        # Main widget and layout
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QVBoxLayout(main_widget)

        # Create the CAD viewer widget
        self.cad_viewer = CADViewer()
        main_layout.addWidget(self.cad_viewer)

        # Controls widget and layout
        controls_widget = QtWidgets.QWidget()
        controls_layout = QtWidgets.QHBoxLayout(controls_widget)
        main_layout.addWidget(controls_widget)

        # Text input box
        self.prompt_input = QtWidgets.QLineEdit()
        self.prompt_input.setPlaceholderText("Enter your drawing command...")
        controls_layout.addWidget(self.prompt_input)

        # Generate button
        self.generate_button = QtWidgets.QPushButton("Generate")
        self.generate_button.clicked.connect(self.on_generate)
        controls_layout.addWidget(self.generate_button)

        # Create and load the initial DXF file
        self.ensure_initial_drawing()
        self.load_dxf("drawing.dxf")

    def ensure_initial_drawing(self):
        dxf_file = "drawing.dxf"
        if not os.path.exists(dxf_file):
            print(f"'{dxf_file}' not found. Creating a new one.")
            create_dxf_drawing()

    def load_dxf(self, filepath):
        try:
            doc, auditor = recover.readfile(filepath)
            if auditor.has_errors:
                error_message = "\n".join(auditor.errors)
                QtWidgets.QMessageBox.critical(self, "DXF Loading Error", f"The DXF file has errors:\n{error_message}")
                doc = ezdxf.new()
        except (IOError, ezdxf.DXFStructureError) as e:
            QtWidgets.QMessageBox.critical(self, "File Error", f"Could not load DXF file: {e}")
            doc = ezdxf.new()

        self.cad_viewer.set_document(doc, doc.audit())
        self.cad_viewer.draw_layout("Model")

    def on_generate(self):
        prompt = self.prompt_input.text()
        if not prompt:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter a prompt.")
            return

        self.generate_button.setEnabled(False)
        self.prompt_input.setEnabled(False)

        # Using a QProgressDialog for better user feedback
        progress = QtWidgets.QProgressDialog("Generating drawing with Gemini...", "Cancel", 0, 0, self)
        progress.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        progress.show()

        # Call the Gemini API
        response_json = get_gemini_response(prompt)

        progress.close()

        # Clear the old drawing and process the new commands
        doc = self.cad_viewer.doc
        msp = doc.modelspace()
        msp.clear()

        success, message = process_drawing_commands(doc, response_json)

        if success:
            # Redraw the canvas
            self.cad_viewer.draw_layout("Model")
            QtWidgets.QMessageBox.information(self, "Success", message)
        else:
            # Show an error message
            QtWidgets.QMessageBox.critical(self, "Processing Error", message)

        self.generate_button.setEnabled(True)
        self.prompt_input.setEnabled(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
