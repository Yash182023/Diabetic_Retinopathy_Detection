from fastapi import FastAPI, File, UploadFile
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import io
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import tensorflow as tf

# Create FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom activation function
def swish(x):
    return x * tf.sigmoid(x)

# Define the FixedDropout class
from tensorflow.keras.layers import Dropout

class FixedDropout(Dropout):
    def _get_noise_shape(self, inputs):
        if self.noise_shape is None:
            return self.noise_shape
        return [inputs.shape[0]] + list(self.noise_shape[1:])

# Register the custom objects
tf.keras.utils.get_custom_objects().update({
    'FixedDropout': FixedDropout,
    'swish': swish
})

# Load the model with the custom objects

# MODEL_PATH = "model_phase2_best.h5" # best model so far, for Gaussian

MODEL_PATH = "model_phase2_best_bell_graham.h5" # -- for Bell graham
try:
    model = load_model(MODEL_PATH, compile=False)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    # If loading fails, you might want to handle this case
    # For example, by providing a default model or showing an error message
    raise

# Define class names
CLASS_NAMES = ["No DR", "Mild", "Moderate", "Severe", "Proliferative DR"]

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    # Read and preprocess the image
    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0  # Normalize
    img_array = np.expand_dims(img_array, axis=0)

    # Make prediction
    predictions = model.predict(img_array)
    predicted_class = CLASS_NAMES[np.argmax(predictions)]

    return {"class": predicted_class, "confidence": float(np.max(predictions))}

# Mount static files AFTER defining all API routes
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)