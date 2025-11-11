# Site Training Register API Documentation

## Overview
The Site Training Register module allows users to record training sessions conducted on-site with photo documentation, trainee tracking, and location-based activity management.

## Features

### ✅ Photo Upload
- **Click Photo**: Capture photo directly from camera
- **Upload Photo**: Upload existing photo from device
- **Auto Timestamp**: Training date/time automatically captured
- **Supported Formats**: JPG, JPEG, PNG, GIF
- **Max Size**: 10MB per photo

### ✅ Trainee Management
- **Multiple Trainees**: Add multiple trainee names in one session
- **JSON Array Format**: `["Name 1", "Name 2", "Name 3"]`
- **Trainee Count**: Auto-calculated per training

### ✅ Location & Activity Tracking
- **Building-wise**: Track which building/location training was conducted
- **Activity Types**: 
  - Blockwork
  - Gypsum installation
  - Plastering
  - Painting
  - Waterproofing
  - Safety training
  - Equipment operation
  - And more...

### ✅ Statistics Dashboard
- Total trainings conducted
- Total trainees trained
- Trainings by activity type
- Trainings by building/location
- Recent training sessions

---

## API Endpoints

### 1. Create Training Record
**POST** `/api/training-records`

Create a new training record with photo.

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: multipart/form-data
```

**Form Data:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| project_id | integer | Yes | Project ID |
| photo | file | Yes | Training photo (JPG/PNG, max 10MB) |
| trainee_names | JSON string | Yes | Array of trainee names `["Name1", "Name2"]` |
| building | string | Yes | Building/location name |
| activity | string | Yes | Activity type (Blockwork, Gypsum, etc.) |
| training_topic | string | Yes | Training topic/title |
| training_date | datetime | No | Training date (defaults to now) |
| duration_minutes | integer | No | Training duration in minutes |
| remarks | string | No | Additional remarks |

**Example (using curl):**
```bash
curl -X POST http://localhost:8001/api/training-records \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "project_id=1" \
  -F "photo=@/path/to/photo.jpg" \
  -F 'trainee_names=["John Doe", "Jane Smith", "Bob Johnson"]' \
  -F "building=Building A" \
  -F "activity=Blockwork" \
  -F "training_topic=Proper Block Laying Techniques" \
  -F "duration_minutes=90" \
  -F "remarks=Good participation from all trainees"
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Training record created successfully",
  "record": {
    "id": 1,
    "projectId": 1,
    "trainerId": 1,
    "trainingDate": "2025-11-10T12:30:00",
    "trainingTopic": "Proper Block Laying Techniques",
    "traineeNames": ["John Doe", "Jane Smith", "Bob Johnson"],
    "traineeCount": 3,
    "building": "Building A",
    "activity": "Blockwork",
    "durationMinutes": 90,
    "hasPhoto": true,
    "photoFilename": "photo.jpg",
    "remarks": "Good participation from all trainees",
    "trainer_name": "System Admin"
  }
}
```

---

### 2. List Training Records
**GET** `/api/training-records`

Get list of training records with filters.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| project_id | integer | Yes | Project ID |
| building | string | No | Filter by building |
| activity | string | No | Filter by activity type |
| trainer_id | integer | No | Filter by trainer |
| start_date | date | No | From date (YYYY-MM-DD) |
| end_date | date | No | Until date (YYYY-MM-DD) |

**Example:**
```bash
curl http://localhost:8001/api/training-records?project_id=1&activity=Blockwork \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (200 OK):**
```json
{
  "success": true,
  "count": 2,
  "records": [
    {
      "id": 1,
      "projectId": 1,
      "trainerId": 1,
      "trainer_name": "System Admin",
      "trainingDate": "2025-11-10T12:30:00",
      "trainingTopic": "Proper Block Laying Techniques",
      "traineeNames": ["John Doe", "Jane Smith"],
      "traineeCount": 2,
      "building": "Building A",
      "activity": "Blockwork",
      "hasPhoto": true
    }
  ]
}
```

---

### 3. Get Training Record Details
**GET** `/api/training-records/:id`

Get detailed information about a specific training record.

**Query Parameters:**
- `project_id` (required): Project ID

**Example:**
```bash
curl http://localhost:8001/api/training-records/1?project_id=1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 4. Get Training Photo
**GET** `/api/training-records/:id/photo`

View/download the training photo.

**Query Parameters:**
- `project_id` (required): Project ID

**Example:**
```bash
# View in browser
http://localhost:8001/api/training-records/1/photo?project_id=1

# Download via curl
curl http://localhost:8001/api/training-records/1/photo?project_id=1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o training_photo.jpg
```

---

### 5. Update Training Record
**PUT** `/api/training-records/:id`

Update training record details (cannot update photo).

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Request Body:**
```json
{
  "project_id": 1,
  "trainee_names": ["John Doe", "Jane Smith", "Bob Johnson", "Alice Brown"],
  "building": "Building A - Ground Floor",
  "activity": "Blockwork",
  "training_topic": "Advanced Block Laying Techniques",
  "duration_minutes": 120,
  "remarks": "Extended session with hands-on practice"
}
```

**Permissions:**
- Only the trainer who created the record OR Quality Manager can update

---

### 6. Delete Training Record
**DELETE** `/api/training-records/:id`

Soft delete a training record (Quality Manager only).

**Query Parameters:**
- `project_id` (required): Project ID

**Permissions:**
- Only Quality Manager can delete records

**Example:**
```bash
curl -X DELETE http://localhost:8001/api/training-records/1?project_id=1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 7. Get Training Statistics
**GET** `/api/training-records/stats`

Get comprehensive training statistics for a project.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| project_id | integer | Yes | Project ID |
| start_date | date | No | Stats from date (YYYY-MM-DD) |
| end_date | date | No | Stats until date (YYYY-MM-DD) |

**Example:**
```bash
curl "http://localhost:8001/api/training-records/stats?project_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (200 OK):**
```json
{
  "success": true,
  "stats": {
    "total_trainings": 15,
    "total_trainees": 47,
    "by_activity": {
      "Blockwork": 5,
      "Gypsum": 3,
      "Plastering": 4,
      "Safety Training": 3
    },
    "by_building": {
      "Building A": 8,
      "Building B": 5,
      "Building C": 2
    },
    "recent_trainings": [
      {
        "id": 15,
        "trainingDate": "2025-11-10T14:00:00",
        "trainingTopic": "Safety Protocols",
        "traineeCount": 8,
        "building": "Building A",
        "activity": "Safety Training",
        "trainer_name": "System Admin"
      }
    ]
  }
}
```

---

### 8. Health Check
**GET** `/api/training-records/health`

Check if the training register service is running.

**Example:**
```bash
curl http://localhost:8001/api/training-records/health
```

**Response (200 OK):**
```json
{
  "service": "training-register-api",
  "status": "healthy",
  "timestamp": "2025-11-10T12:00:00.000000"
}
```

---

## Activity Types

Commonly used activity types (you can use custom ones too):

- **Masonry**
  - Blockwork
  - Brickwork
  - Stone masonry

- **Finishing**
  - Gypsum installation
  - Plastering
  - Painting
  - Tiling
  - Flooring

- **Waterproofing**
  - Bathroom waterproofing
  - Terrace waterproofing
  - External wall treatment

- **Safety**
  - PPE usage
  - Scaffolding safety
  - Fall protection
  - First aid

- **Equipment**
  - Mixer operation
  - Power tools
  - Lifting equipment

- **Quality**
  - Quality standards
  - Inspection procedures
  - Testing methods

---

## Database Schema

**Table:** `training_records`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| project_id | INTEGER | Foreign key to projects |
| trainer_id | INTEGER | Foreign key to users (trainer) |
| training_date | DATETIME | Training date/time |
| training_topic | VARCHAR(255) | Training title |
| trainee_names_json | TEXT | JSON array of trainee names |
| building | VARCHAR(100) | Building/location |
| activity | VARCHAR(100) | Activity type |
| duration_minutes | INTEGER | Duration (optional) |
| photo_filename | VARCHAR(255) | Photo filename |
| photo_data | BLOB | Photo binary data |
| photo_mimetype | VARCHAR(50) | Photo MIME type |
| remarks | TEXT | Additional remarks |
| is_deleted | INTEGER | Soft delete flag |
| deleted_at | DATETIME | Deletion timestamp |
| deleted_by | INTEGER | User who deleted |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Last update timestamp |

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required fields: project_id, trainee_names, building, activity, training_topic"
}
```

### 401 Unauthorized
```json
{
  "error": "Authorization required",
  "message": "Request does not contain an access token"
}
```

### 403 Forbidden
```json
{
  "error": "Access denied. You are not a member of this project"
}
```

### 404 Not Found
```json
{
  "error": "Training record not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Failed to create training record: <error details>"
}
```

---

## Frontend Integration Examples

### Using Fetch API (JavaScript)
```javascript
// Create training record with photo
async function createTraining(photoFile, trainees, building, activity, topic) {
  const formData = new FormData();
  formData.append('project_id', projectId);
  formData.append('photo', photoFile);
  formData.append('trainee_names', JSON.stringify(trainees));
  formData.append('building', building);
  formData.append('activity', activity);
  formData.append('training_topic', topic);
  
  const response = await fetch('http://localhost:8001/api/training-records', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  
  return await response.json();
}

// Usage
const trainees = ['John Doe', 'Jane Smith'];
const photo = document.getElementById('photoInput').files[0];
const result = await createTraining(photo, trainees, 'Building A', 'Blockwork', 'Block Laying 101');
```

### Using React
```jsx
import { useState } from 'react';

function TrainingForm() {
  const [trainees, setTrainees] = useState(['']);
  const [photo, setPhoto] = useState(null);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('project_id', projectId);
    formData.append('photo', photo);
    formData.append('trainee_names', JSON.stringify(trainees.filter(n => n)));
    formData.append('building', e.target.building.value);
    formData.append('activity', e.target.activity.value);
    formData.append('training_topic', e.target.topic.value);
    
    const response = await fetch('/api/training-records', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    });
    
    const result = await response.json();
    console.log('Training created:', result);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="file"
        accept="image/*"
        capture="environment"
        onChange={(e) => setPhoto(e.target.files[0])}
        required
      />
      {/* More form fields... */}
    </form>
  );
}
```

---

## Testing

Run the test suite:
```bash
python test_api_complete.py
```

Test training register specifically:
```bash
curl http://localhost:8001/api/training-records/health
```

---

## Next Steps

1. **Frontend Development**: Create mobile-friendly UI for photo capture
2. **Reports**: Generate training attendance reports
3. **Certificates**: Auto-generate training certificates for trainees
4. **Notifications**: Send training reminders and confirmations
5. **Analytics**: Advanced analytics dashboard with charts

---

## Support

For issues or questions:
- Check server logs: `tail -f server.log`
- Test endpoint health: `curl http://localhost:8001/api/training-records/health`
- Review authentication: Ensure JWT token is valid

---

**Version**: 1.0  
**Last Updated**: November 10, 2025
