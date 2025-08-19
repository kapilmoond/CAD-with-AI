import json
import ezdxf

def process_drawing_commands(doc, commands_json: str):
    """
    Parses a JSON string of drawing commands and applies them to a DXF document.

    Args:
        doc: An ezdxf document object.
        commands_json: A JSON string containing the drawing commands.

    Returns:
        A tuple of (bool, str) indicating success and a message.
    """
    try:
        data = json.loads(commands_json)
    except json.JSONDecodeError:
        return False, "Error: Invalid JSON format from LLM."

    if "commands" not in data or not isinstance(data["commands"], list):
        return False, "Error: JSON missing 'commands' list."

    msp = doc.modelspace()
    for command in data["commands"]:
        cmd_type = command.get("command")
        if cmd_type == "line":
            start = command.get("start")
            end = command.get("end")
            if start and end:
                msp.add_line(tuple(start), tuple(end))
            else:
                return False, f"Error: Incomplete line command: {command}"
        elif cmd_type == "circle":
            center = command.get("center")
            radius = command.get("radius")
            if center and radius:
                msp.add_circle(tuple(center), radius)
            else:
                return False, f"Error: Incomplete circle command: {command}"
        elif cmd_type == "text":
            text = command.get("text")
            insert = command.get("insert")
            height = command.get("height", 2.5) # Default height
            if text and insert:
                msp.add_text(text, dxfattribs={"insert": tuple(insert), "height": height})
            else:
                return False, f"Error: Incomplete text command: {command}"
        else:
            return False, f"Error: Unknown command type '{cmd_type}'"

    return True, "Drawing updated successfully."
