# Skill: FacebookAutoPost

## Purpose
Automatically create and post content on Facebook with human-in-the-loop approval.

## When to Use
- Share business updates on Facebook
- Post to Facebook Page
- Cross-post from other platforms
- Engage with Facebook audience

## Capabilities
- Draft Facebook posts
- Attach images
- Add hashtags and links
- Create approval files
- Post to Facebook Page or Profile

## Usage

### Basic Post
```
Use FacebookAutoPost to create and post about [topic]
```

### With Image
```
Use FacebookAutoPost to post this image with caption: [path/to/image.jpg]
```

### Process Queue
```
Use FacebookAutoPost to publish all approved posts from Approved/ folder
```

## Workflow

1. **Draft Creation**
   - Create post content
   - Add relevant hashtags
   - Save to `Pending_Approval/FACEBOOK_POST_*.md`

2. **Human Approval**
   - User reviews post
   - Moves file to `Approved/` to approve

3. **Posting**
   - Run: `python watchers/facebook_poster.py --process-queue`
   - Browser opens Facebook
   - Uploads image (if any)
   - Enters post content
   - Waits for manual "Post" click

## Best Practices

### Content Length
- No strict character limit
- Optimal: 100-250 characters
- Long-form: Up to 1000 characters

### Images
- Recommended size: 1200x630 pixels
- Supported: JPG, PNG, GIF
- Max size: 15MB

### Hashtags
- Use 3-5 relevant hashtags
- Less is more on Facebook
- Examples: #Business #Technology #AI

### Posting Times
- Best: Tue-Thu, 9 AM - 1 PM
- Avoid: Weekends (lower engagement)

## Files
- Script: `watchers/facebook_poster.py`
- Session: `.facebook_session/`
- Approved: `Approved/FACEBOOK_POST_*.md`
- Done: `Done/FACEBOOK_POST_*.md`

## Related Skills
- LinkedInAutoPost
- InstagramAutoPost
- TwitterAutoPost
- SocialMediaSummary
