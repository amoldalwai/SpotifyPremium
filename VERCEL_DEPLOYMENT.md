# Vercel Deployment Guide

This guide will help you deploy your Music Player application to Vercel.

## Prerequisites

- A [Vercel account](https://vercel.com/signup) (free tier available)
- Your project code pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Deployment Steps

### Option 1: Deploy via Vercel CLI (Recommended for Quick Testing)

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy from your project directory:**
   ```bash
   vercel
   ```

4. **For production deployment:**
   ```bash
   vercel --prod
   ```

### Option 2: Deploy via Vercel Dashboard (Recommended for Production)

1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Vercel deployment"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Connect to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Import your GitHub repository
   - Vercel will auto-detect the Flask application

3. **Configure (if needed):**
   - Framework Preset: Other
   - Root Directory: ./
   - Build Command: (leave empty)
   - Output Directory: (leave empty)

4. **Deploy:**
   - Click "Deploy"
   - Wait for the deployment to complete
   - Your app will be live at `https://your-project-name.vercel.app`

## Important Notes

### Configuration Files

The following files have been created for Vercel deployment:

- **`vercel.json`**: Configures Vercel to use Python runtime and route all requests to `app.py`
- **`.vercelignore`**: Specifies files to exclude from deployment

### Limitations to Be Aware Of

1. **Serverless Function Timeout**: 
   - Free tier: 10 seconds max execution time
   - Pro tier: 60 seconds max execution time
   - If music streaming takes longer, consider upgrading or using a different hosting solution

2. **Cold Starts**: 
   - Serverless functions may have cold start delays (1-2 seconds)
   - First request after inactivity may be slower

3. **File Storage**: 
   - Vercel serverless functions are stateless
   - No persistent file storage (downloads are temporary)

4. **Memory Limits**:
   - Free tier: 1024 MB
   - May need adjustment for heavy processing

### Environment Variables

If you need to add environment variables (API keys, secrets, etc.):

1. Go to your project in Vercel Dashboard
2. Navigate to Settings → Environment Variables
3. Add your variables

### Custom Domain (Optional)

1. Go to your project settings in Vercel
2. Navigate to Domains
3. Add your custom domain
4. Follow the DNS configuration instructions

## Testing Your Deployment

Once deployed, test the following:

1. ✅ Homepage loads correctly
2. ✅ Search functionality works
3. ✅ Music playback functions properly
4. ✅ Provider selection works (JioSaavn, YouTube Music, All)

## Troubleshooting

### Deployment Fails

- Check the build logs in Vercel dashboard
- Ensure all dependencies in `requirements.txt` are compatible
- Verify `vercel.json` configuration is correct

### Application Errors

- Check Function Logs in Vercel dashboard
- Enable debug mode temporarily to see detailed errors
- Ensure all API endpoints are accessible from Vercel's servers

### Slow Performance

- Consider upgrading to Vercel Pro for better performance
- Optimize your code for serverless architecture
- Implement caching where possible

## Monitoring

- View real-time logs in Vercel Dashboard → Your Project → Logs
- Monitor function invocations and errors
- Set up integration with monitoring tools if needed

## Updating Your Deployment

### Via Git (Automatic)
- Push changes to your connected Git repository
- Vercel will automatically redeploy

### Via CLI
```bash
vercel --prod
```

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/runtimes#official-runtimes/python)
- [Vercel Community](https://github.com/vercel/community)
