# Job Scrapers API Reference

Base URL: `http://localhost:8000` (default for local development)

## Authentication

The API uses API Key authentication. To make authenticated requests, you must include the `X-API-Key` header with your valid API key.

```http
X-API-Key: your_api_key_here
```

Some endpoints might be configured to be public depending on the server settings (`REQUIRE_API_KEY` env var), but sending the key is the standard method for protected access.

## Endpoints

### Jobs

#### Get All Jobs
Retrieves a paginated list of job listings.

- **URL**: `/jobs/`
- **Method**: `GET`
- **Parameters**:
    - `job_classification` (query, optional): Filter by job classification.
    - `job_sub_classification` (query, optional): Filter by sub-classification.
    - `work_arrangements` (query, optional): Filter by work type (e.g., 'Full Time').
    - `skip` (query, default=0): Number of records to skip.
    - `limit` (query, default=100): Number of records to return (max 1000).
- **Success Response**: `200 OK`
    - Content: List of [JobListingResponse](#joblistingresponse)
    - **Note**: If `X-API-Key` is provided, `is_favorite` field will reflect user's favorite status.

#### Search Jobs
Search for jobs using a keyword.

- **URL**: `/jobs/search`
- **Method**: `GET`
- **Parameters**:
    - `keyword` (query, required): Search term (min 2 chars).
    - `skip` (query, default=0): Number of records to skip.
    - `limit` (query, default=100): Number of records to return.
- **Success Response**: `200 OK`
    - Content: List of [JobListingResponse](#joblistingresponse)

#### Get Job Details
Get full details for a specific job.

- **URL**: `/jobs/{job_id}`
- **Method**: `GET`
- **Parameters**:
    - `job_id` (path, required): The unique ID of the job.
- **Success Response**: `200 OK`
    - Content: [JobWithDetailsResponse](#jobwithdetailsresponse)
- **Error Responses**:
    - `404 Not Found`: If the job ID does not exist.

#### Get Job Statistics
Get overall system statistics.

- **URL**: `/jobs/stats`
- **Method**: `GET`
- **Success Response**: `200 OK`
    - Content: [JobStatsResponse](#jobstatsresponse)

#### Get Classifications
Get list of unique job classifications.

- **URL**: `/jobs/classifications`
- **Method**: `GET`
- **Success Response**: `200 OK`
    - Content: List of `string`

#### Get Sub-Classifications
Get list of unique job sub-classifications.

- **URL**: `/jobs/sub-classifications`
- **Method**: `GET`
- **Success Response**: `200 OK`
    - Content: List of `string`

#### Get Work Arrangements
Get list of unique work arrangements.

- **URL**: `/jobs/work-arrangements`
- **Method**: `GET`
- **Success Response**: `200 OK`
    - Content: List of `string`

### Favorites

#### Get Favorite Jobs
Get a paginated list of the authenticated user's favorite jobs.

- **URL**: `/favorites/`
- **Method**: `GET`
- **Parameters**:
    - `skip` (query, default=0)
    - `limit` (query, default=100)
- **Success Response**: `200 OK`
    - Content: List of [FavoriteJobResponse](#favoritejobresponse)

#### Add Favorite Job
Add a job to favorites.

- **URL**: `/favorites/{job_id}`
- **Method**: `POST`
- **Parameters**:
    - `job_id` (path, required)
- **Body**: [FavoriteJobCreate](#favoritejobcreate)
- **Success Response**: `201 Created`
    - Content: [FavoriteJobResponse](#favoritejobresponse)
- **Error Responses**:
    - `404 Not Found`: If job ID doesn't exist.

#### Remove Favorite Job
Remove a job from favorites.

- **URL**: `/favorites/{job_id}`
- **Method**: `DELETE`
- **Parameters**:
    - `job_id` (path, required)
- **Success Response**: `200 OK`
    - Content: `{"message": "Job '{job_id}' removed from favorites"}`
- **Error Responses**:
    - `404 Not Found`: If job is not in favorites.

#### Check Favorite Status
Check if a specific job is in the user's favorites.

- **URL**: `/favorites/{job_id}/status`
- **Method**: `GET`
- **Parameters**:
    - `job_id` (path, required)
- **Success Response**: `200 OK`
    - Content: [FavoriteStatusResponse](#favoritestatusresponse)

## Schemas

### JobListingResponse
```json
{
  "job_id": "string",
  "title": "string",
  "job_details_url": "string",
  "job_summary": "string",
  "company_name": "string",
  "location": "string",
  "country_code": "string",
  "listing_date": "datetime",
  "salary_label": "string | null",
  "work_type": "string | null",
  "job_classification": "string | null",
  "job_sub_classification": "string | null",
  "work_arrangements": "string | null",
  "is_favorite": "boolean (default: false)"
}
```

### JobWithDetailsResponse
Includes all fields from **JobListingResponse**, plus:
```json
{
  ...
  "status": "string | null",
  "is_expired": "boolean | null",
  "details": "string (HTML content) | null",
  "is_verified": "boolean | null",
  "expires_at": "datetime | null"
}
```

### JobStatsResponse
```json
{
  "total_jobs": "integer",
  "new_jobs": "integer"
}
```

### FavoriteJobResponse
```json
{
  "id": "integer",
  "job_id": "string",
  "created_at": "datetime",
  "notes": "string | null",
  "job": "JobListingResponse"
}
```

### FavoriteJobCreate
```json
{
  "notes": "string | null"
}
```

### FavoriteStatusResponse
```json
{
  "job_id": "string",
  "is_favorited": "boolean"
}
```

## Error Handling

Standard HTTP status codes are used:
- `400 Bad Request`: Invalid input (e.g., negative skip, limit too high).
- `401 Unauthorized`: Missing or invalid API key.
- `404 Not Found`: Resource not found.
- `422 Unprocessable Entity`: Validation error (body/parameters).
- `500 Internal Server Error`: Server/Database error.
