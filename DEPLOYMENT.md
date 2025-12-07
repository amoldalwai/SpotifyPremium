# Firebase Deployment Guide - Music Player

## Prerequisites
1. Install Firebase CLI: `npm install -g firebase-tools`
2. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install
3. Docker Desktop (for local testing)

## Setup Steps

### 1. Login to Firebase and Google Cloud
```powershell
firebase login
gcloud auth login
gcloud config set project spotify-premium-amol
```

### 2. Enable Required APIs
Go to Google Cloud Console and enable:
- Cloud Run API
- Cloud Build API
- Container Registry API

Or run:
```powershell
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 3. Deploy to Cloud Run

#### Option A: Using Cloud Build (Automated)
```powershell
gcloud builds submit --config cloudbuild.yaml
```

#### Option B: Manual Deployment
```powershell
# Build the Docker image
docker build -t gcr.io/spotify-premium-amol/music-player .

# Push to Google Container Registry
docker push gcr.io/spotify-premium-amol/music-player

# Deploy to Cloud Run
gcloud run deploy music-player `
  --image gcr.io/spotify-premium-amol/music-player `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --memory 512Mi `
  --cpu 1 `
  --timeout 300
```

### 4. Setup Firebase Hosting (Optional - for custom domain)
```powershell
firebase init hosting
firebase deploy --only hosting
```

## Local Testing

### Test with Docker
```powershell
# Build the image
docker build -t music-player .

# Run locally
docker run -p 8080:8080 music-player

# Access at http://localhost:8080
```

### Test without Docker
```powershell
pip install -r requirements.txt
python app.py
```

## Deployment Commands (Quick Reference)

### Deploy Everything
```powershell
gcloud builds submit --config cloudbuild.yaml
```

### View Logs
```powershell
gcloud run services logs read music-player --region us-central1
```

### Update Service
```powershell
gcloud run services update music-player --region us-central1
```

### Get Service URL
```powershell
gcloud run services describe music-player --region us-central1 --format 'value(status.url)'
```

## Expected URL
After deployment, your app will be available at:
- Cloud Run: `https://music-player-[hash]-uc.a.run.app`
- Custom Domain (if configured): `https://your-domain.web.app`

## Troubleshooting

### Build Fails
- Check Docker is installed and running
- Verify all files are present
- Check requirements.txt for compatibility

### Deployment Fails
- Ensure billing is enabled on Google Cloud
- Check API permissions
- Verify project ID is correct

### App Doesn't Start
- Check logs: `gcloud run services logs read music-player`
- Verify PORT environment variable
- Check dependencies in requirements.txt

## Cost Estimation
- Cloud Run: Free tier includes 2 million requests/month
- First 180,000 vCPU-seconds free
- First 360,000 GiB-seconds free
- Small apps typically stay within free tier

## Security Notes
- App is set to `--allow-unauthenticated` for public access
- For private access, remove this flag
- Consider adding authentication for production use
