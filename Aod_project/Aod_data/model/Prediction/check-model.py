from tensorflow.keras.models import load_model

model = load_model("bundaran_hi.keras")
print(model.input.shape)