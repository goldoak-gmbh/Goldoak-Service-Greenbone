import os
import datetime

def save_report(xml_content: str) -> str:
    """
    Saves the given XML content to a file named with the current UTC timestamp.
    Returns the full file path.
    """
    # Ensure the reports directory exists
    os.makedirs(os.getenv("REPORTS_DIR", "/app/reports"), exist_ok=True)
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"report_{timestamp}.xml"
    filepath = os.path.join(os.getenv("REPORTS_DIR", "/app/reports"), filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(xml_content)
    return filepath



