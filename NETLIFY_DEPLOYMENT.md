# Netlify Deployment Guide

This guide will help you deploy your Music Player application to Netlify.

## Prerequisites

- A [Netlify account](https://app.netlify.com/signup) (free tier available)
- Your project code pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Deployment Steps

### Option 1: Deploy via Netlify CLI

1. **Install Netlify CLI:**
   ```bash
   npm install -g netlify-cli
   ```

2. **Login to Netlify:**
   ```bash
   netlify login
   ```

3. **Deploy from your project directory:**
   ```bash
   netlify deploy
   ```

4. **For production deployment:**
   ```bash
   netlify deploy --prod
   ```

### Option 2: Deploy via Netlify Dashboard (Recommended)

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Add Netlify configuration"
   git push origin main
   ```

2. **Connect to Netlify:**
   - Go to [app.netlify.com](https://app.netlify.com)
   - Click "Add new site" → "Import an existing project"
   - Choose your Git provider (GitHub)
   - Select your repository: `SpotifyPremium`

3. **Configure build settings:**
   - Build command: `pip install -r requirements.txt`
   - Publish directory: `.`
   - Functions directory: `netlify/functions`
   
   (These are pre-configured in `netlify.toml`, so you can leave them as detected)

4. **Deploy:**
   - Click "Deploy site"
   - Wait for the deployment to complete
   - Your app will be live at `https://your-site-name.netlify.app`

## Configuration Files

The following files have been created/configured for Netlify:

- **`netlify.toml`**: Main configuration file for Netlify builds and redirects
- **`netlify/functions/app.py`**: Serverless function wrapper for your Flask app
- **`requirements.txt`**: Python dependencies (already configured)

## Important Notes

### Python Version
- Netlify uses Python 3.9 (configured in `netlify.toml`)
- All dependencies in `requirements.txt` are compatible

### Serverless Functions
- Your Flask app runs as a Netlify serverless function
- All routes are handled by the function at `netlify/functions/app.py`
- Function timeout: 10 seconds (free tier), 26 seconds (Pro tier)

### Static Assets
- CSS, JS, and other static files are served directly
- Flask's template rendering works as expected

### Environment Variables

If you need to add environment variables (API keys, secrets):

1. Go to Site settings → Environment variables
2. Add your variables
3. Redeploy the site

### Custom Domain (Optional)

1. Go to Site settings → Domain management
2. Add your custom domain
3. Follow the DNS configuration instructions

## Testing Your Deployment

Once deployed, verify:

1. ✅ Homepage loads correctly
2. ✅ Search functionality works
3. ✅ Music playback functions (JioSaavn)
4. ✅ YouTube Music search works
5. ✅ All providers selection works

## Troubleshooting

### Build Fails

- Check the deploy log in Netlify dashboard
- Ensure all dependencies in `requirements.txt` are valid
- Verify Python version compatibility (3.9)

### Function Errors

- Check Function logs in Netlify dashboard
- Functions have a 10-second timeout on free tier
- Upgrade to Pro for 26-second timeout if needed

### 404 Errors

- Verify `netlify.toml` redirects are configured correctly
- Check that the function name matches the path

### Static Files Not Loading

- Ensure file paths are correct in templates
- Check that static files are in the `static/` directory
- Verify MIME types are correct

## Monitoring

- View real-time logs: Site settings → Functions
- Monitor build history: Deploys tab
- Analytics: Site analytics (available on Pro plan)

## Updating Your Deployment

### Automatic Deployment (Git Integration)
- Push changes to your connected Git repository
- Netlify automatically rebuilds and redeploys

### Manual Deployment (CLI)
```bash
netlify deploy --prod
```

## Performance Tips

1. **Enable caching** for static assets
2. **Use environment variables** for sensitive data
3. **Optimize images** and static resources
4. **Monitor function execution time** to stay within limits

## Limitations

- **Function timeout**: 10s (free), 26s (Pro)
- **Build minutes**: 300/month (free)
- **Bandwidth**: 100 GB/month (free)
- **Concurrent builds**: 1 (free), 3 (Pro)

## Support

- [Netlify Documentation](https://docs.netlify.com/)
- [Netlify Functions](https://docs.netlify.com/functions/overview/)
- [Netlify Community](https://answers.netlify.com/)

## Next Steps

After successful deployment:

1. Test all features thoroughly
2. Set up custom domain (optional)
3. Configure environment variables if needed
4. Monitor performance and logs
5. Share your deployed app! 🎵
