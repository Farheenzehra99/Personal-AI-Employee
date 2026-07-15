# Skill: InstagramAutoPost

## Purpose
Automatically create and post content on Instagram with human-in-the-loop approval.

## When to Use
- Share visual content on Instagram
- Post to Instagram Feed
- Share business updates with images
- Engage with Instagram audience

## Capabilities
- Draft Instagram captions
- Upload images (required)
- Add hashtags (up to 30)
- Create approval files
- Post to Instagram

## Usage

### Basic Post
```
Use InstagramAutoPost to create a post with this image: [path/to/image.jpg]
```

### With Caption
```
Use InstagramAutoPost to post this image with caption about [topic]
```

### Process Queue
```
Use InstagramAutoPost to publish all approved posts from Approved/ folder
```

## Workflow

1. **Draft Creation**
   - Create caption (up to 2200 characters)
   - Add 5-15 hashtags
   - Specify image path
   - Save to `Pending_Approval/INSTAGRAM_POST_*.md`

2. **Human Approval**
   - User reviews post
   - Moves file to `Approved/` to approve

3. **Posting**
   - Run: `python watchers/instagram_poster.py --process-queue`
   - Browser opens Instagram
   - Uploads image
   - Enters caption
   - Waits for manual "Share" click

## Best Practices

### Images
- Size: 1080x1080 (square) or 1080x1350 (portrait)
- Format: JPG or PNG
- High quality required

### Captions
- Max: 2200 characters
- Optimal: 150-200 characters
- First 125 characters are preview

### Hashtags
- Max: 30 hashtags
- Optimal: 5-15 hashtags
- Mix popular and niche

### Posting Times
- Best: Mon-Fri, 10 AM - 3 PM
- Consistency matters more than timing

## Example Caption

```
🚀 Just launched our AI Employee system!

From automating emails to posting on social media - it handles it all while I focus on strategy.

The future of work is here. 💡

#AI #Automation #Business #Technology #Innovation #Startup #Productivity #FutureOfWork #Tech #DigitalTransformation
```

## Files
- Script: `watchers/instagram_poster.py`
- Session: `.instagram_session/`
- Approved: `Approved/INSTAGRAM_POST_*.md`
- Done: `Done/INSTAGRAM_POST_*.md`
- Images: `linkedin_images/` or custom folder

## Related Skills
- LinkedInAutoPost
- FacebookAutoPost
- TwitterAutoPost
- SocialMediaSummary
