import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import io

# Initialize API Server
app = FastAPI(
    title="ImageVisionAI",
    description="Real-Time Image Classification Web Application",
    version="0.0.1",
    terms_of_service=None,
    contact=None,
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)


@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    # Read image file
    image_data = await file.read()

    # Convert to PIL Image
    image = Image.open(io.BytesIO(image_data))

    # Example of processing the image
    # For instance, get the size of the image
    width, height = image.size

    # Return some response
    return JSONResponse(
        content={"filename": file.filename, "width": width, "height": height}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        debug=True,
        log_config="log.ini",
    )
