import asyncio
import os
import urllib.request
import zipfile
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import flwr as fl
from flwr.server.strategy import FedAvg
import numpy as np
import uvicorn
import pandas as pd
from tensorflow import keras
import tensorflow as tf

# Safe GPU setup
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.set_visible_devices(gpus[0], 'GPU')
        tf.config.experimental.set_memory_growth(gpus[0], True)
        print("✅ Safe GPU config set!")
    except RuntimeError as e:
        print(f"GPU config error: {e} - Using CPU.")

def download_movielens_data():
    """Download and extract MovieLens 100k dataset if not present"""
    data_dir = 'ml-100k'
    data_file = os.path.join(data_dir, 'u.data')
    
    if os.path.exists(data_file):
        print("✅ MovieLens dataset already exists!")
        return
    
    print("📥 Downloading MovieLens 100k dataset...")
    url = "http://files.grouplens.org/datasets/movielens/ml-100k.zip"
    zip_path = "ml-100k.zip"
    
    try:
        # Download the dataset
        urllib.request.urlretrieve(url, zip_path)
        print("✅ Dataset downloaded!")
        
        # Extract the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('.')
        
        # Clean up
        os.remove(zip_path)
        print("✅ Dataset extracted and ready!")
        
    except Exception as e:
        print(f"❌ Error downloading dataset: {e}")
        # Create minimal dummy data for demo
        os.makedirs(data_dir, exist_ok=True)
        dummy_data = "1\t1\t5\t881250949\n2\t1\t4\t881250949\n1\t2\t3\t881250949\n"
        with open(data_file, 'w') as f:
            f.write(dummy_data)
        print("⚠️ Using minimal dummy data for demo")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Download dataset if needed
download_movielens_data()

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
try:
    with open('ml-100k/u.item', encoding='latin-1') as f:
        for line in f:
            parts = line.strip().split('|')
            if parts and parts[0].isdigit():
                movie_titles[int(parts[0])] = parts[1]
    print(f"✅ Loaded {len(movie_titles)} movie titles!")
except FileNotFoundError:
    print("⚠️ Movie titles file not found, using generic titles")
    # Create dummy movie titles for the ratings we have
    for movie_id in ratings['item'].unique():
        movie_titles[movie_id] = f"Movie #{movie_id}"

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
    return {"message": "Welcome to ZipSearch! Visit /static/index.html for the interface or /docs for API usage."}

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
