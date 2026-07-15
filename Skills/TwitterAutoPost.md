# Skill: TwitterAutoPost

## Purpose
Automatically create and post tweets on Twitter/X with human-in-the-loop approval.

## When to Use
- Share company updates on Twitter
- Post about achievements, milestones, or news
- Engage with Twitter community
- Cross-post from other platforms

## Capabilities
- Draft tweets (max 280 characters)
- Add relevant hashtags
- Attach images (optional)
- Create approval files for human review
- Post approved tweets to Twitter

## Usage

### Basic Tweet
```
Use TwitterAutoPost to create and schedule a tweet about [topic]
```

### With Image
```
Use TwitterAutoPost to post this image with caption: [path/to/image.jpg]
```

### Process Queue
```
Use TwitterAutoPost to publish all approved tweets from Approved/ folder
```

## Workflow

1. **Draft Creation**
   - Create tweet content (≤280 characters)
   - Add 2-5 relevant hashtags
   - Save to `Pending_Approval/TWITTER_TWEET_*.md`

2. **Human Approval**
   - User reviews tweet
   - Moves file to `Approved/` to approve
   - Deletes file to reject

3. **Posting**
   - Run: `python watchers/twitter_poster.py --process-queue`
   - Browser opens, logs into Twitter
   - Uploads image (if any)
   - Enters tweet text
   - Waits for manual "Post" click

## Tweet Best Practices

### Character Limit
- Maximum: 280 characters
- Images count as 24 characters
- Leave margin for safety (aim for 250)

### Hashtags
- Use 2-5 relevant hashtags
- Mix popular and niche tags
- Examples: #AI #Automation #Tech #Startup

### Content Types
- Company updates
- Industry insights
- Tips and tricks
- Questions to engage audience
- Retweets with commentary

## Example Tweets

### Company Update
```
🚀 Excited to announce our AI Employee just hit 1000+ automated tasks!

From email triage to social media posting - working smarter, not harder.

#AI #Automation #Productivity
```

### Industry Insight
```
The future of work isn't human vs AI.

It's human + AI working together.

Our AI Employee handles routine tasks while we focus on strategy.

#FutureOfWork #AI #Leadership
```

## Files
- Script: `watchers/twitter_poster.py`
- Session: `.twitter_session/`
- Approved: `Approved/TWITTER_TWEET_*.md`
- Done: `Done/TWITTER_TWEET_*.md`

## Error Handling

### Tweet Too Long
- Skill should warn if >280 characters
- Suggest trimming or creating thread

### Login Failed
- Re-run: `python watchers/twitter_login.py`
- Check session validity

### Post Failed
- Check screenshot in `twitter_post_screenshot.png`
- Verify Twitter account status
- Try again with shorter content

## Related Skills
- LinkedInAutoPost
- FacebookAutoPost
- InstagramAutoPost
- SocialMediaSummary
