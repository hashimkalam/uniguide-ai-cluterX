# UniGuide AI

An intelligent platform that helps UK high school students predict their chances of getting into their dream universities based on real admission trends, course competitiveness, and grade history.

## Architecture Overview

### System Design

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │ -> │   Data Ingestion│ -> │   PostgreSQL    │ -> │   FastAPI       │
│                 │    │   Service       │    │   Database      │    │   REST API      │
│ • Discover Uni  │    │                 │    │                 │    │                 │
│ • UCAS          │    │ • CSV Parsing   │    │ • Universities  │    │ • Course Search │
│ • HESA          │    │ • Data Cleaning │    │ • Courses       │    │ • Entry Req.    │
└─────────────────┘    │ • Validation    │    │ • Entry Req.    │    └─────────────────┘
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Background Jobs │
                       │                 │
                       │ • Daily Refresh │
                       │ • Data Sync     │
                       └─────────────────┘
```

### Database Schema

#### Universities Table
- `pubukprn`: Primary identifier (UKPRN)
- `legal_name`: Official university name
- `first_trading_name`: Trading name
- `website`: University website
- `country`: Location

#### Courses Table
- `kiscourseid`: Course identifier
- `pubukprn`: Foreign key to university
- `title`: Course title
- `kis_mode`: Full-time/part-time
- `kis_level`: Course level
- `hecos_code`: Subject classification

#### Entry Requirements Table
- `kiscourseid`: Foreign key to course
- `tariff_agg`: Aggregate tariff score
- `tariff_agg_year`: Year of tariff data
- Tariff ranges (T001-T240): Entry requirement bands

## Tech Stack

- **Backend**: Python 3.11, FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0 (async)
- **Scheduling**: APScheduler
- **Containerization**: Docker & Docker Compose
- **Data Processing**: pandas

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Using Docker (Recommended)

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd uniguide-ai
   ```

2. **Configure environment**:
   - Copy `.env` and ensure `DATABASE_URL` points to your local PostgreSQL database

3. **Start the API**:
   ```bash
   docker-compose up --build
   ```

4. **Initialize database** (first time only):
   ```bash
   # Run locally
   python scripts/init_db.py
   ```

5. **Ingest data**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/admin/refresh-data
   ```

### Local Development

1. **Setup virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   - Ensure `.env` has the correct `DATABASE_URL` for your local PostgreSQL

3. **Initialize database**:
   ```bash
   python scripts/init_db.py
   ```

4. **Run data ingestion**:
   ```bash
   python -c "import asyncio; from app.services.ingest import run_data_ingestion; asyncio.run(run_data_ingestion())"
   ```

5. **Start the API**:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

### Course Search

**GET** `/api/v1/courses`

Search for university courses with filters.

**Query Parameters**:
- `university` (string): Filter by university name
- `subject` (string): Filter by subject or course title
- `course_name` (string): Exact match on course title
- `year` (integer): Filter by academic year
- `limit` (integer): Max results (default: 50, max: 100)
- `offset` (integer): Pagination offset (default: 0)

**Example**:
```bash
curl "http://localhost:8000/api/v1/courses?university=oxford&subject=engineering&limit=10"
```

**Response**:
```json
{
  "count": 150,
  "results": [
    {
      "id": 1,
      "kiscourseid": "BSRDIF-B821",
      "title": "Engineering Science",
      "university": {
        "legal_name": "University of Oxford",
        "website": "https://www.ox.ac.uk"
      },
      "entry_requirements": [
        {
          "tariff_agg": 144.0,
          "tariff_agg_year": 2023
        }
      ]
    }
  ]
}
```

### Course Details

**GET** `/api/v1/courses/{course_id}`

Get detailed information about a specific course.

**Example**:
```bash
curl http://localhost:8000/api/v1/courses/BSRDIF-B821
```

### Manual Data Refresh

**POST** `/api/v1/admin/refresh-data`

Trigger manual data refresh from sources.

## Data Sources

The system ingests data from Discover Uni dataset containing:

- **30,829 courses** from UK universities
- **511 institutions** (universities/colleges)
- **Entry requirements** with tariff scores
- **Course classifications** (HECoS codes)
- **Student outcomes** and employment data

### Data Refresh

- **Automatic**: Daily background job
- **Manual**: Via API endpoint
- **Source**: Local CSV files (can be extended to fetch from APIs)

## Development

### Project Structure

```
uniguide-ai/
├── app/
│   ├── config.py          # Application configuration
│   ├── logging_config.py  # Logging setup
│   ├── main.py           # FastAPI application
│   ├── schemas.py        # Pydantic models
│   ├── db/
│   │   ├── base.py       # Database connection
│   │   ├── models.py     # SQLAlchemy models
│   │   └── crud.py       # Database operations
│   ├── routes/
│   │   ├── courses.py    # Course API endpoints
│   │   └── admin.py      # Admin endpoints
│   ├── services/
│   │   └── ingest.py     # Data ingestion service
│   └── jobs/
│       └── scheduler.py  # Background job scheduler
├── scripts/              # Utility scripts
│   ├── init_db.py       # Database initialization
│   ├── inspect_db.py    # Database inspection
│   └── test_db.py       # Database testing
├── data/                 # Discover Uni dataset
├── init_db.py           # Database initialization
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker image
├── docker-compose.yml  # Multi-container setup
└── README.md
```

### Key Components

#### Data Ingestion Service
- Loads CSV files with automatic encoding detection
- Handles data validation and cleaning
- Supports incremental updates
- Comprehensive error handling

#### API Layer
- RESTful endpoints with OpenAPI documentation
- Pydantic validation for all inputs/outputs
- Pagination support
- Comprehensive error responses

#### Background Jobs
- APScheduler for automated tasks
- Daily data refresh
- Configurable intervals
- Error logging and recovery

## Deployment

### Production Considerations

1. **Database**: Use managed PostgreSQL (RDS, Cloud SQL, etc.)
2. **Container Registry**: Push Docker images to registry
3. **Orchestration**: Kubernetes or cloud container services
4. **Monitoring**: Add application metrics and logging
5. **Security**: API authentication, rate limiting
6. **Scaling**: Load balancer, read replicas

### Environment Variables

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
APP_NAME=UniGuide AI
DEBUG=false
DATA_DIRECTORY=/app/data
API_HOST=0.0.0.0
API_PORT=8000
REFRESH_INTERVAL_HOURS=24
```

## Testing

### API Testing

```bash
# Health check
curl http://localhost:8000/health

# Search courses
curl "http://localhost:8000/api/v1/courses?university=cambridge"

# Get specific course
curl http://localhost:8000/api/v1/courses/BSRDIF-B821
```

### Data Validation

```bash
# Check data inspector
python data/inspect/data_inspector.py
```

## Future Enhancements

- **Real-time Data**: Connect to live APIs (UCAS, Discover Uni)
- **Caching**: Redis for API response caching
- **Authentication**: User accounts and API keys
- **Analytics**: Course popularity and trends
- **Machine Learning**: Admission prediction models
- **Frontend**: React/Vue.js dashboard
- **Mobile App**: React Native companion

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

This project is part of the UniGuide AI assessment and is provided as-is for educational purposes.
