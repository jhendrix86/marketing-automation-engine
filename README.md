# Marketing Automation Engine

Automated marketing campaign system for the Autonomous Company OS. This engine handles email campaigns, social media automation, lead nurturing, campaign management, and marketing analytics.

## Features

- **Email Campaigns** - Automated email sequences and drip campaigns
- **Social Media Automation** - Scheduled posting across platforms
- **Lead Scoring** - Intelligent lead qualification and scoring
- **Lead Nurturing** - Automated lead nurturing workflows
- **Campaign Management** - End-to-end campaign lifecycle management
- **A/B Testing** - Campaign variant testing and optimization
- **Segmentation** - Advanced audience segmentation
- **Analytics Dashboard** - Marketing performance metrics and ROI tracking

## Architecture

```
┌─────────────┐    Leads     ┌──────────────┐
│   All       │ ────────────> │  Lead        │
│  Sources    │               │  Ingestion   │
└─────────────┘               └──────┬───────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
            ┌───────▼──────┐ ┌────▼────┐ ┌────▼──────┐
            │   Lead       │ │ Scoring │ │ Nurturing  │
            │   Manager    │ │ Engine  │ │  Engine    │
            └──────────────┘ └─────────┘ └───────────┘
                    │                │                │
                    └────────────────┼────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │      Campaign Manager          │
                    │  (Email, Social, Multi-channel) │
                    └─────────────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
            ┌───────▼──────┐ ┌────▼────┐ ┌────▼──────┐
            │   A/B        │ │ Segment │ │ Analytics  │
            │   Testing    │ │ Engine  │ │  Engine    │
            └──────────────┘ └─────────┘ └───────────┘
```

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL (for campaign data)
- Redis (for caching and queues)
- SendGrid (for email)
- Social media API keys (Twitter, LinkedIn, etc.)

### Local Development

```bash
# Clone repository
git clone https://github.com/autonomous-company/marketing-automation-engine.git
cd marketing-automation-engine

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the service
uvicorn app.main:app --reload --port 8039
```

### Docker Deployment

```bash
# Build and start all services
cd docker
docker-compose up -d

# View logs
docker-compose logs -f marketing-engine

# Stop services
docker-compose down
```

## Configuration

Configuration is managed via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://localhost/marketing` | PostgreSQL connection URL |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `SENDGRID_API_KEY` | - | SendGrid API key |
| `TWITTER_API_KEY` | - | Twitter API key |
| `LINKEDIN_API_KEY` | - | LinkedIn API key |
| `DEFAULT_SENDER_EMAIL` | `marketing@company.com` | Default sender email |

## API Endpoints

### Health & Info
- `GET /health` - Health check
- `GET /` - Service information

### Campaign Management
- `POST /campaigns/create` - Create campaign
- `POST /campaigns/{campaign_id}/launch` - Launch campaign
- `POST /campaigns/{campaign_id}/pause` - Pause campaign
- `POST /campaigns/{campaign_id}/stop` - Stop campaign
- `GET /campaigns/{campaign_id}` - Get campaign details
- `GET /campaigns` - List campaigns

### Email Campaigns
- `POST /email/create` - Create email campaign
- `POST /email/{campaign_id}/send` - Send email campaign
- `POST /email/drip/create` - Create drip campaign
- `GET /email/{campaign_id}/stats` - Get email stats

### Social Media
- `POST /social/schedule` - Schedule social post
- `POST /social/batch` - Batch schedule posts
- `GET /social/posts/{post_id}` - Get post details
- `GET /social/calendar` - Get posting calendar

### Lead Scoring
- `POST /leads/score` - Score lead
- `GET /leads/{lead_id}/score` - Get lead score
- `POST /leads/batch-score` - Batch score leads
- `GET /leads/scores` - List lead scores

### Segmentation
- `POST /segments/create` - Create segment
- `POST /segments/{segment_id}/update` - Update segment
- `GET /segments/{segment_id}` - Get segment details
- `GET /segments` - List segments

### Analytics
- `GET /analytics/campaigns` - Get campaign analytics
- `GET /analytics/leads` - Get lead analytics
- `GET /analytics/roi` - Get ROI metrics
- `GET /analytics/performance` - Get performance metrics

## Usage Examples

### Create Email Campaign

```python
import httpx

async def create_email_campaign():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8039/email/create",
            json={
                "name": "Welcome Series",
                "subject": "Welcome to our platform",
                "segment_id": "seg_123",
                "template_id": "tmpl_123",
                "schedule": "immediate"
            }
        )
        return response.json()
```

### Schedule Social Post

```python
async def schedule_social_post():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8039/social/schedule",
            json={
                "platform": "twitter",
                "content": "Check out our new feature!",
                "scheduled_at": "2024-01-20T10:00:00",
                "media_urls": []
            }
        )
        return response.json()
```

### Score Lead

```python
async def score_lead():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8039/leads/score",
            json={
                "lead_id": "lead_123",
                "email": "prospect@example.com",
                "behavior": {
                    "page_visits": 5,
                    "email_opens": 3,
                    "link_clicks": 2
                }
            }
        )
        return response.json()
```

## Campaign Types

- **Email Campaigns** - One-time and drip email campaigns
- **Social Campaigns** - Multi-platform social media campaigns
- **Multi-channel** - Coordinated campaigns across channels
- **Retargeting** - Retargeting campaigns for engaged users
- **Nurture Campaigns** - Automated lead nurturing sequences

## Lead Scoring Model

- **Demographic Score** - Based on job title, company size, industry
- **Behavior Score** - Based on website engagement, email interactions
- **Engagement Score** - Based on content consumption, event attendance
- **Custom Score** - Custom scoring rules and weights

## Integration with Other Engines

### Funnel Automation
- Receives lead events from funnels
- Triggers nurture campaigns based on funnel stage
- Updates lead scores based on funnel behavior

### Content Engine
- Uses content for campaigns
- Tracks content performance
- Optimizes content based on engagement

### Analytics Engine
- Provides marketing analytics
- Tracks campaign ROI
- Generates marketing reports

## Monitoring

### Metrics
- Campaign open rates
- Click-through rates
- Conversion rates
- Lead scores
- Campaign ROI
- Social engagement metrics

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request
