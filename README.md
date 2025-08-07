# Federated Movie Recommender

A privacy-preserving movie recommendation system built with federated learning. This project demonstrates how to train a neural network on the MovieLens 100k dataset across multiple clients without sharing raw data, aggregate the model centrally using Flower, and serve personalized recommendations via a FastAPI endpoint. It's designed for developers interested in federated AI, with GPU acceleration for faster training and human-readable outputs (e.g., movie titles instead of IDs).

This repo focuses on the code and logic—large datasets like MovieLens are not included (see Setup below). Built in Bengaluru during late-night coding sessions on August 07, 2025—perfect for exploring first-principles in ML privacy and API design!

## Features

- **Federated Learning**: Clients train locally on private data splits (e.g., user ratings), and the server averages model weights using FedAvg—ensuring data never leaves the client.
- **GPU Acceleration**: Leverages NVIDIA GPUs with CUDA for faster training (tested on GTX 1050 Ti with CUDA 12.2).
- **Normalized Inputs**: User and movie IDs are scaled to prevent bias toward high-numbered items, leading to more accurate predictions.
- **API Endpoint**: `/recommend?user_id=&n=` returns top N movie suggestions with titles, IDs, and predicted ratings (scaled 1–5, rounded to 1 decimal place, filtered above a 2.0 threshold).
- **Readable Outputs**: Maps movie IDs to titles from `u.item` for user-friendly results (e.g., "Star Wars (1977)" instead of ID 50).
- **One-Command Launch**: `python run_app.py` starts the Flower server, clients, and FastAPI—all in one go.
- **Customizable**: Easy to tweak epochs, thresholds, or add features like genres.

## Prerequisites

- **Python**: 3.12 or higher (install from [python.org](https://www.python.org/)).
- **Libraries**: 
  - flwr (for federated learning)
  - tensorflow (for model training, with GPU support)
  - fastapi and uvicorn (for the API server)
  - pandas and numpy (for data handling)
- **Dataset**: MovieLens 100k (download from [grouplens.org](https://grouplens.org/datasets/movielens/100k/)—unzip to `ml-100k/` in the project root).
- **Hardware (Optional)**: NVIDIA GPU with CUDA 12.2+ for accelerated training.
- **Tools**: Git for cloning, a terminal for running commands.

**Note**: The `ml-100k` dataset and any virtual environments (e.g., `ml/`) are ignored in `.gitignore` to keep the repo lightweight. Download the dataset separately.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/sivaratrisrinivas/zipsearch.git
   cd zipsearch
   ```

2. (Optional) Create and activate a virtual environment:
   ```
   python -m venv ml
   source ml/bin/activate  # On Windows: ml\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install flwr tensorflow fastapi uvicorn pandas numpy
   ```

4. Download and prepare the dataset:
   - Get `ml-100k.zip` from [grouplens.org](https://grouplens.org/datasets/movielens/100k/).
   - Unzip it into the project root (you should have `ml-100k/u.data` and `ml-100k/u.item`).

## How to Run

1. Start the application (launches Flower server/clients and FastAPI):
   ```
   python run_app.py
   ```
   - This will:
     - Start the federated training (clients learn on data splits).
     - Aggregate and save the global model (`global_model.h5`).
     - Run the API server at http://127.0.0.1:8000.

2. Open your browser and go to http://127.0.0.1:8000/docs for the interactive API docs.

3. Test the endpoint (e.g., via browser or curl):
   ```
   curl "http://127.0.0.1:8000/recommend?user_id=4&n=5"
   ```

4. Stop the app: Press Ctrl+C in the terminal.

**Expected Logs**: You'll see GPU config messages, training progress (e.g., loss values), and "Uvicorn running on http://127.0.0.1:8000".

## Usage

The core API is `/recommend`, which generates personalized movie suggestions based on the federated model.

- **Endpoint**: `GET /recommend`
- **Parameters**:
  - `user_id` (int): The user to recommend for (e.g., 4).
  - `n` (int, optional): Number of recommendations (default 5, max 20).
- **Response**: JSON with user_id and a list of recommendations (movie_id, movie_title, predicted_rating rounded to 1 decimal).

**Example Response**:
```
{
  "user_id": 4,
  "recommendations": [
    {
      "movie_id": 50,
      "movie_title": "Star Wars (1977)",
      "predicted_rating": 4.2
    },
    {
      "movie_id": 100,
      "movie_title": "Fargo (1996)",
      "predicted_rating": 4.1
    },
    ...
  ]
}
```

**Notes**:
- Ratings are predicted on a 1–5 scale (like MovieLens) and filtered to show only those ≥2.0.
- If predictions are low/uniform, increase training epochs in `app.py` for better accuracy.

## Architecture Overview

- **Data Flow**: Load and split MovieLens ratings → Normalize IDs → Train local models on clients.
- **Federated Learning**: Flower clients (`SimpleClient`) fit models on private data; server aggregates via FedAvg.
- **Model**: Simple Keras neural net with dense layers, sigmoid output scaled to 1–5.
- **API**: FastAPI serves the global model for inference, mapping IDs to titles.
- **Async Launch**: asyncio runs server, clients, and Uvicorn concurrently.

From first principles: This breaks down recommendation into atomic parts—privacy via federation, learning via backprop, serving via HTTP—to build a scalable system.

## Contributing and Improvements

- **Future Ideas**:
  - Add movie genres/years from `u.item` to recommendations.
  - Support more clients or larger datasets (e.g., MovieLens 1M).
  - Integrate embeddings for user/movie IDs to boost accuracy.
  - Deploy to cloud (e.g., Docker + AWS/Heroku).

- **How to Contribute**:
  1. Fork the repo.
  2. Create a branch: `git checkout -b feature/new-thing`.
  3. Commit changes: `git commit -m "Add new feature"`.
  4. Push: `git push origin feature/new-thing`.
  5. Open a Pull Request.

Feel free to open issues for bugs or ideas!

