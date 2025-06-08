import base64
from pdf2image import convert_from_path
from pathlib import Path
import io

def export_dashboard_to_images(sdk, workspace_id, dashboard_id, export_file_name="test"):
    # Export a dashboard in PDF format
    export_path = Path.cwd() / "input"
    export_path.mkdir(parents=True, exist_ok=True)
    sdk.export.export_pdf(
        workspace_id=workspace_id,
        dashboard_id=dashboard_id,
        file_name=export_file_name,
        store_path=export_path,
        metadata={}
    )

    # Convert PDF to images
    images = convert_from_path(export_path / (export_file_name + ".pdf"), dpi=300)  # Change dpi for quality

    image_data = []
    for i, img in enumerate(images):
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        image_data.append(img_str)  # Store base64 string if needed

    # Return the list of base64-encoded images (or just `images` if raw images are needed)
    return image_data  # or `return image_data` if you need base64 strings 