# ZipSearch

This is a movie recommendation system that suggests movies you might like based on what other people have rated, but with a twist: your personal data never leaves your device.

## The Problem This Solves

Traditional recommendation systems work by collecting everyone's movie ratings into one big database. Companies like Netflix know exactly what you've watched and when. This system does something different: it learns from everyone's preferences without anyone having to share their actual viewing history.

Think of it like this: imagine you and your friends want to create a shared "best movies" list, but nobody wants to reveal which specific movies they've watched. This system lets you do exactly that.

## How It Actually Works

### The Privacy Protection (Why "Federated Learning")

Instead of sending your movie ratings to a central server, the system works like this:

1. **Your data stays on your device**: Your movie ratings never leave your computer
2. **Only the "learning" gets shared**: Your device learns patterns from your ratings and shares only those patterns (not the actual ratings)
3. **Everyone's patterns get combined**: A central coordinator combines everyone's learned patterns into one smart recommendation system
4. **You get recommendations**: The combined system can suggest movies without ever knowing what you specifically rated

This is like having a group of friends who each read different books, then share only their "reading preferences" (not which specific books they read) to help everyone find new books they'd enjoy.

### The Technical Pieces

**The Brain (Neural Network)**:
- A simple artificial brain that learns to predict movie ratings
- Takes in a user ID and movie ID, outputs a predicted rating (1-5 stars)
- Uses two layers: one that finds patterns, one that makes the final prediction

**The Data (MovieLens Dataset)**:
- 100,000 real movie ratings from 943 users rating 1,682 movies
- Each rating tells us: which user, which movie, what rating (1-5), when
- We split this data between two "virtual users" to simulate the privacy-preserving setup

**The Coordination (Flower Framework)**:
- Manages the privacy-preserving learning process
- Ensures multiple devices can train together without sharing raw data
- Combines everyone's learning into one final recommendation system

**The Interface (FastAPI)**:
- A web service that lets you ask for movie recommendations
- You provide a user ID, it returns movie suggestions with predicted ratings
- Includes actual movie titles (like "Star Wars") instead of just numbers

### Why This Approach Matters

**Privacy**: Your viewing history stays private, but you still benefit from everyone else's preferences

**Accuracy**: The system learns from a diverse group of people, making better recommendations than just looking at your own history

**Scalability**: This could work with millions of users without creating a privacy nightmare

**Real-world relevance**: This is how future recommendation systems might work as privacy becomes more important

## What You Need to Run This

**Software**:
- Python 3.12+ (the programming language everything is written in)
- Several Python libraries for machine learning and web services
- The MovieLens dataset (100k movie ratings - you download this separately)

**Hardware**:
- Any modern computer (GPU optional but makes training faster)
- About 2GB of free space for the dataset and libraries

**Time**: About 10 minutes to set up, 2 minutes to run

## Setting It Up

1. **Get the code**:
   ```bash
   git clone https://github.com/sivaratrisrinivas/zipsearch.git
   cd zipsearch
   ```

2. **Create an isolated environment** (recommended):
   ```bash
   python -m venv ml
   source ml/bin/activate  # On Windows: ml\Scripts\activate
   ```

3. **Install the required libraries**:
   ```bash
   pip install flwr tensorflow fastapi uvicorn pandas numpy
   ```

4. **Get the movie data**:
   - Download ml-100k.zip from [MovieLens](https://grouplens.org/datasets/movielens/100k/)
   - Unzip it into your project folder so you have `ml-100k/u.data` and `ml-100k/u.item`

## Running the System

**Start everything with one command**:
```bash
python run_app.py
```

This automatically:
1. Starts the coordination server
2. Creates two virtual users with private data
3. Trains the recommendation system using privacy-preserving learning
4. Starts a web service for getting recommendations

**Test it out**:
- Open http://127.0.0.1:8000/docs in your browser for an interactive interface
- Or test directly: `curl "http://127.0.0.1:8000/recommend?user_id=4&n=5"`

**Stop it**: Press Ctrl+C in your terminal

## What You'll See

The system will output logs showing:
- GPU setup (if you have one)
- Training progress from each virtual user
- The web service starting up
- A saved file called `global_model.h5` containing the final recommendation system

## Example Results

When you ask for recommendations for user #4, you might get:
```json
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
    }
  ]
}
```

## Why Each Technical Choice Was Made

**Why split the data between clients?**: This simulates real-world usage where different people have different viewing histories

**Why normalize the IDs?**: Movie ID 1500 isn't inherently "bigger" than movie ID 15 - we scale them so the AI doesn't get confused

**Why use a simple neural network?**: Complex models need more data and are harder to debug - this simple approach works well for demonstration

**Why filter ratings below 2.0?**: Nobody wants recommendations for movies predicted to be terrible

**Why round ratings to 1 decimal?**: Fake precision (4.23847 stars) looks silly - 4.2 stars is clear and honest

**Why use async/await throughout?**: The system runs multiple processes simultaneously (training, coordination, web service) - async makes this clean and efficient

## The Files Explained

**`app.py`**: The main application containing the AI model, privacy-preserving training, and web service

**`run_app.py`**: A helper script that starts all the pieces in the right order with proper timing

**`ml-100k/`**: The movie ratings dataset (you download this)

**`.gitignore`**: Tells git to ignore large files like datasets and trained models

**`global_model.h5`**: The final trained recommendation system (created when you run the app)

## What You Could Build Next

**More realistic simulation**: Add more virtual users with different preferences

**Better recommendations**: Include movie genres, release years, and user demographics

**Real deployment**: Package this for cloud deployment where real users could connect

**Enhanced privacy**: Add techniques like differential privacy for even stronger privacy guarantees

**Mobile app**: Build a phone app that connects to this privacy-preserving system

This project demonstrates that you can build useful AI systems without sacrificing privacy - something that's becoming increasingly important as data collection practices come under scrutiny.

