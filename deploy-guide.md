# 🚀 Deployment Guide for ZipSearch

Choose from these deployment options to put your movie recommendation system online:

## 🔥 Quick & Easy Options (Recommended for Demo)

### 1. Railway (Free Tier + Easy)
**Best for**: Quick demos, no credit card required initially

1. **Setup**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   # or
   curl -fsSL https://railway.app/install.sh | sh
   ```

2. **Deploy**:
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Access**: Railway will give you a public URL like `https://yourapp.railway.app`

### 2. Render (Free Tier)
**Best for**: Persistent free hosting

1. Go to [render.com](https://render.com)
2. Connect your GitHub repository
3. Choose "Web Service"
4. Set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run_app.py`
   - **Port**: `8000`
5. Deploy!

### 3. Heroku (Free Tier Ended, But Still Popular)
**Best for**: Production-ready apps

1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: python run_app.py
   ```
3. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

## 🏢 Production Options

### 4. DigitalOcean App Platform
**Cost**: ~$5/month
**Best for**: Scalable production apps

1. Go to [DigitalOcean Apps](https://cloud.digitalocean.com/apps)
2. Connect GitHub repo
3. Choose Python app
4. Auto-detects Dockerfile
5. Deploy with one click

### 5. Google Cloud Run
**Cost**: Pay per use (very cheap for demos)
**Best for**: Serverless, scales to zero

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/zipsearch
gcloud run deploy --image gcr.io/PROJECT-ID/zipsearch --platform managed
```

### 6. AWS (Advanced)
**Best for**: Enterprise production

Use AWS App Runner or ECS for container deployment.

## 📝 Pre-deployment Checklist

- [ ] Push your code to GitHub
- [ ] Ensure `requirements.txt` is up to date
- [ ] Test locally with `python run_app.py`
- [ ] Choose deployment platform
- [ ] Set environment variables if needed

## 🔧 Configuration Notes

### Environment Variables (Optional)
```bash
# For production
PORT=8000
HOST=0.0.0.0
```

### Domain Setup
After deployment, you can:
1. Use the provided subdomain (e.g., `yourapp.railway.app`)
2. Add a custom domain in your platform's settings
3. Set up SSL (usually automatic)

## 🎯 Recommended Flow

**For Quick Demo**: Railway → Takes 2 minutes
**For Serious Project**: Render or DigitalOcean → Professional URLs
**For Production**: Google Cloud Run or AWS → Enterprise-grade

## 📱 Access Your App

Once deployed, your app will be available at:
- **Main Interface**: `https://yourapp.com/static/index.html`
- **API Docs**: `https://yourapp.com/docs`
- **Direct API**: `https://yourapp.com/recommend?user_id=4&n=5`

## 🐛 Troubleshooting

**Port Issues**: Most platforms auto-detect port 8000
**Memory Issues**: TensorFlow needs ~512MB RAM minimum
**Startup Time**: First load might take 30-60 seconds (model loading)
**Dataset**: The MovieLens dataset downloads automatically in Docker

## 🌟 Next Steps

After deployment:
1. Share your live URL!
2. Monitor usage in platform dashboard
3. Set up custom domain
4. Add analytics if desired
5. Scale up if you get traffic

Choose Railway for the fastest deployment - you'll have a live URL in under 5 minutes! 🚀
