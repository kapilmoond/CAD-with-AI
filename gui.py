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

class CADGeneratorWindow(CADViewer):
    def __init__(self):
        # Pass a config to the CADViewer constructor
        super().__init__(config=Configuration())
        self.setWindowTitle("AI CAD Generator")

        # The CADViewer (self) is the central widget. We need to add our controls to it.
        # The default CADViewer is a QMainWindow with a QSplitter as the central widget.
        # The splitter contains the CAD widget and a sidebar. We can add our controls to the sidebar.

        # Create a new widget for our controls
        self.controls_widget = QtWidgets.QWidget()
        controls_layout = QtWidgets.QVBoxLayout(self.controls_widget)

        # Text input box
        self.prompt_input = QtWidgets.QLineEdit()
        self.prompt_input.setPlaceholderText("Enter your drawing command...")
        controls_layout.addWidget(self.prompt_input)

        # Generate button
        self.generate_button = QtWidgets.QPushButton("Generate Drawing")
        self.generate_button.clicked.connect(self.on_generate)
        controls_layout.addWidget(self.generate_button)

        # Add the controls to the bottom of the existing sidebar
        # The default sidebar is a QSplitter at self.sidebar
        self.sidebar.addWidget(self.controls_widget)

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
                # This will be displayed in the sidebar by the parent class
                print(f"The DXF file '{filepath}' has errors.")
        except (IOError, ezdxf.DXFStructureError) as e:
            QtWidgets.QMessageBox.critical(self, "File Error", f"Could not load DXF file: {e}")
            doc, auditor = ezdxf.new(), ezdxf.new().audit()

        self.set_document(doc, auditor)

    def on_generate(self):
        prompt = self.prompt_input.text()
        if not prompt:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter a prompt.")
            return

        self.generate_button.setEnabled(False)
        self.prompt_input.setEnabled(False)

        progress = QtWidgets.QProgressDialog("Generating drawing with Gemini...", "Cancel", 0, 0, self)
        progress.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        progress.show()

        # Call the Gemini API
        response_json = get_gemini_response(prompt)

        progress.close()

        # The CADViewer's CADWidget is stored in self._cad
        # The document is in self._cad.doc
        doc = self._cad.doc
        if doc is None:
            # If there's no document, create a new one
            doc, auditor = ezdxf.new(), ezdxf.new().audit()
            self.set_document(doc, auditor)
            doc = self._cad.doc # refresh doc reference

        msp = doc.modelspace()
        msp.clear()

        success, message = process_drawing_commands(doc, response_json)

        if success:
            # Redraw the canvas by calling the inherited draw_layout method
            self.draw_layout(self._cad.current_layout, reset_view=False)
            QtWidgets.QMessageBox.information(self, "Success", message)
        else:
            QtWidgets.QMessageBox.critical(self, "Processing Error", message)

        self.generate_button.setEnabled(True)
        self.prompt_input.setEnabled(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # The main window is now our custom CADGeneratorWindow
    window = CADGeneratorWindow()
    window.show()
    sys.exit(app.exec())
