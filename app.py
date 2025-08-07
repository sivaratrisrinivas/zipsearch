import asyncio
from fastapi import FastAPI
import flwr as fl
from flwr.server.strategy import FedAvg
import numpy as np
import uvicorn
import pandas as pd
from tensorflow import keras
import tensorflow as tf
import os

# Safe GPU setup
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.set_visible_devices(gpus[0], 'GPU')
        tf.config.experimental.set_memory_growth(gpus[0], True)
        print("✅ Safe GPU config set!")
    except RuntimeError as e:
        print(f"GPU config error: {e} - Using CPU.")

app = FastAPI()

# Load MovieLens data
ratings = pd.read_csv('ml-100k/u.data', sep='\t', names=['user', 'item', 'rating', 'timestamp'])

# Get normalization denominators
max_user = ratings['user'].max()
max_item = ratings['item'].max()

# Prepare normalized input for each client
def get_normalized_inputs(data):
    x = data[['user', 'item']].values.astype(np.float32)
    x[:,0] /= max_user
    x[:,1] /= max_item
    y = data['rating'].values
    return x, y

data_client1 = ratings[ratings['user'] <= 300]
data_client2 = ratings[ratings['user'] > 300]
x1, y1 = get_normalized_inputs(data_client1)
x2, y2 = get_normalized_inputs(data_client2)

# Load movie_id => movie_title dictionary
movie_titles = {}
with open('ml-100k/u.item', encoding='latin-1') as f:
    for line in f:
        parts = line.strip().split('|')
        if parts and parts[0].isdigit():
            movie_titles[int(parts[0])] = parts[1]

def get_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(2,)),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')  # Outputs 0-1, scale to 1-5 later
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

class SimpleClient(fl.client.NumPyClient):
    def __init__(self, x_train, y_train):
        self.model = get_model()
        self.x_train = x_train
        self.y_train = y_train

    def get_parameters(self, config):
        return self.model.get_weights()

    def fit(self, parameters, config):
        self.model.set_weights(parameters)
        self.model.fit(self.x_train, self.y_train, epochs=5, batch_size=32, verbose=0)  # Increased epochs for better learning
        return self.model.get_weights(), len(self.x_train), {}

    def evaluate(self, parameters, config):
        self.model.set_weights(parameters)
        loss = self.model.evaluate(self.x_train, self.y_train, verbose=0)
        return loss, len(self.x_train), {"loss": loss}

async def start_flower_server():
    strategy = FedAvg(min_available_clients=2)
    await fl.server.start_server(
        server_address="0.0.0.0:8080",
        config=fl.server.ServerConfig(num_rounds=1),
        strategy=strategy
    )
    # Save global model after training
    global_model = get_model()
    if hasattr(strategy, "parameters"):
        weights = fl.common.parameters_to_ndarrays(strategy.parameters)
        global_model.set_weights(weights)
        global_model.save("global_model.h5")
        print("✅ Saved global model after federated training!")

async def start_client(client_id, x_train, y_train):
    client = SimpleClient(x_train, y_train)
    await fl.client.start_numpy_client(server_address="0.0.0.0:8080", client=client)

async def start_uvicorn():
    config = uvicorn.Config("__main__:app", host="127.0.0.1", port=8000, log_level="info", reload=False)
    server = uvicorn.Server(config)
    await server.serve()

def load_global_model():
    model = get_model()
    if os.path.exists("global_model.h5"):
        model = keras.models.load_model("global_model.h5")
    return model

MAX_RESULTS = 20
MIN_RATING_THRESHOLD = 2.0  # Only show recommendations above this rating

@app.get("/")
async def root():
    return {"message": "Welcome! See /docs for API usage."}

@app.get("/recommend")
def recommend(user_id: int, n: int = 5):
    n = min(n, MAX_RESULTS)
    model = load_global_model()
    all_movie_ids = np.array(sorted(movie_titles.keys()))
    # Normalize the input for recommendations
    user_norm = user_id / max_user
    movie_norms = all_movie_ids / max_item
    user_column = np.full_like(movie_norms, user_norm)
    input_pairs = np.stack([user_column, movie_norms], axis=1).astype(np.float32)
    predictions = model.predict(input_pairs, verbose=0).flatten()
    # Scale sigmoid output (0-1) to 1-5 range
    predictions = 1 + predictions * 4
    # Sort and filter by threshold
    sorted_indices = predictions.argsort()[::-1]
    recommendations = []
    for i in sorted_indices:
        if len(recommendations) >= n:
            break
        mid = int(all_movie_ids[i])
        rating = round(float(predictions[i]), 1)  # Round to 1 decimal place
        if rating >= MIN_RATING_THRESHOLD:
            recommendations.append({
                "movie_id": mid,
                "movie_title": movie_titles[mid],
                "predicted_rating": rating
            })
    return {"user_id": user_id, "recommendations": recommendations}

async def main():
    server_task = asyncio.create_task(start_flower_server())
    await asyncio.sleep(1)
    client1_task = asyncio.create_task(start_client(1, x1, y1))
    client2_task = asyncio.create_task(start_client(2, x2, y2))
    app_task = asyncio.create_task(start_uvicorn())
    await asyncio.gather(server_task, client1_task, client2_task, app_task)

if __name__ == "__main__":
    asyncio.run(main())
