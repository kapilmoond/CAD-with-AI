import ezdxf
from ezdxf.enums import TextEntityAlignment

def create_dxf_drawing():
    # Create a new DXF document
    doc = ezdxf.new()
    # Get the modelspace
    msp = doc.modelspace()

    # Add a line
    msp.add_line((0, 0), (100, 0))

    # Add a circle
    msp.add_circle((50, 25), radius=20)

    # Add a rectangle (as a closed polyline)
    points = [(0, 50), (100, 50), (100, 100), (0, 100)]
    msp.add_lwpolyline(points, close=True)

    # Add a text
    msp.add_text(
        "Hello, ezdxf!",
        height=5,
    ).set_placement((50, 120), align=TextEntityAlignment.CENTER)


    # Save the document
    doc.saveas("drawing.dxf")
    print("DXF file 'drawing.dxf' created successfully.")

if __name__ == "__main__":
    create_dxf_drawing()
