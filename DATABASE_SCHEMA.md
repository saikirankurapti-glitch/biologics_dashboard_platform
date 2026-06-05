# Database Schema Documentation

This document describes the expected MongoDB collections and schema for the Biologics Discovery Platform.

## Overview

The database (`biologics_platform`) contains 12 collections organized by function:

- **User Management**: users, user_activities, access_logs
- **Target Management**: targets
- **Drug Discovery**: screenings, docking_jobs, optimizations, admet_jobs
- **Formulation**: preformulation_reports, formulation_designs
- **Research**: experiments, report_registry

**Note**: The dashboard dynamically discovers schema. If your collections have different field names, the metrics will adapt or return zero values.

---

## Collection Schemas

### 1. users

Stores user profile and metadata.

```javascript
{
  "_id": ObjectId,
  "user_id": String,           // Unique identifier
  "email": String,
  "name": String,
  "department": String,        // e.g., "Drug Discovery", "Formulation"
  "role": String,              // e.g., "Scientist", "Manager", "Admin"
  "active": Boolean,
  "created_at": DateTime,      // Registration date
  "updated_at": DateTime,
  "last_login": DateTime,
  "metadata": {
    "institution": String,
    "expertise": Array
  }
}
```

**Key Fields for Dashboard**:
- `user_id`: Used for user filtering and tracking
- `department`: Used for departmental usage analytics
- `created_at`: Used for new user calculations
- `last_login`: Used for activity analysis

---

### 2. user_activities

Tracks all user actions in the system.

```javascript
{
  "_id": ObjectId,
  "user_id": String,           // Reference to users collection
  "activity_type": String,     // e.g., "login", "data_access", "analysis_run"
  "module": String,            // e.g., "screening", "docking", "optimization"
  "action": String,
  "timestamp": DateTime,       // When activity occurred
  "details": {
    "ip_address": String,
    "session_id": String,
    "duration_seconds": Number
  }
}
```

**Key Fields for Dashboard**:
- `user_id`: For DAU/MAU calculations
- `timestamp`: For trend analysis and heatmaps
- `activity_type`: For filtering activities
- `module`: For module-specific metrics

**Indexed Fields** (recommended):
- `timestamp` (for date range queries)
- `user_id` (for grouping)

---

### 3. access_logs

Records system login and access events.

```javascript
{
  "_id": ObjectId,
  "user_id": String,
  "login_time": DateTime,
  "logout_time": DateTime,
  "ip_address": String,
  "session_id": String,
  "success": Boolean,
  "timestamp": DateTime
}
```

**Key Fields for Dashboard**:
- `timestamp`: For login trend analysis
- `user_id`: For user tracking

---

### 4. targets

Stores drug target information.

```javascript
{
  "_id": ObjectId,
  "target_id": String,          // Unique identifier
  "protein_id": String,
  "target_name": String,
  "description": String,
  "organism": String,           // e.g., "human", "murine"
  "sequence": String,           // Protein sequence
  "molecular_weight": Number,   // in Da
  "created_at": DateTime,
  "updated_at": DateTime,
  "status": String,             // "active", "inactive", "archived"
  "metadata": {
    "go_terms": Array,
    "pathways": Array,
    "therapeutic_area": String
  }
}
```

**Key Fields for Dashboard**:
- `target_id`: For tracking
- `created_at`: For target analysis trend
- `status`: For status distribution
- `protein_id`: For unique protein counts

---

### 5. screenings

Virtual screening run data.

```javascript
{
  "_id": ObjectId,
  "screening_id": String,
  "target_id": String,          // Reference to targets
  "molecule_count": Number,     // Total molecules screened
  "hits_count": Number,         // Number of hits identified
  "hit_threshold": Number,      // Score threshold for hit
  "status": String,             // "completed", "running", "failed"
  "created_at": DateTime,
  "updated_at": DateTime,
  "results": {
    "top_hits": Array,
    "average_score": Number,
    "duration_hours": Number
  }
}
```

**Key Fields for Dashboard**:
- `molecule_count`: For total molecules metric
- `hits_count`: For hits identified metric
- `created_at`: For screening trend
- `status`: For success rate calculation

---

### 6. docking_jobs

Molecular docking simulation results.

```javascript
{
  "_id": ObjectId,
  "job_id": String,
  "screening_id": String,       // Reference to screenings
  "target_id": String,
  "molecule_id": String,
  "binding_energy": Number,     // kcal/mol
  "rmsd": Number,               // Root mean square deviation
  "poses": Array,               // Docking poses
  "status": String,             // "completed", "running", "failed"
  "created_at": DateTime,
  "completed_at": DateTime,
  "metadata": {
    "software": String,
    "scoring_function": String,
    "num_poses": Number
  }
}
```

**Key Fields for Dashboard**:
- `binding_energy`: For average binding energy metric
- `status`: For success rate calculation
- `created_at`: For docking trend

---

### 7. optimizations

Lead optimization and refinement.

```javascript
{
  "_id": ObjectId,
  "optimization_id": String,
  "candidate_id": String,
  "target_id": String,
  "docking_job_id": String,
  "optimization_score": Number, // 0-100 score
  "binding_energy": Number,
  "leads_count": Number,        // Number of lead candidates generated
  "status": String,             // "completed", "running", "failed"
  "created_at": DateTime,
  "updated_at": DateTime,
  "properties": {
    "molecular_weight": Number,
    "logp": Number,
    "hbd": Number,              // Hydrogen bond donors
    "hba": Number               // Hydrogen bond acceptors
  }
}
```

**Key Fields for Dashboard**:
- `optimization_score`: For candidate ranking
- `candidate_id`: For candidate tracking
- `leads_count`: For leads generated metric
- `created_at`: For optimization trend

---

### 8. admet_jobs

ADMET prediction and toxicity assessment.

```javascript
{
  "_id": ObjectId,
  "admet_id": String,
  "candidate_id": String,
  "optimization_id": String,
  "admet_property": String,     // e.g., "absorption", "distribution", "metabolism"
  "prediction": String,         // "pass", "fail", "uncertain"
  "confidence": Number,         // 0-1 confidence score
  "value": Number,              // Predicted value
  "unit": String,               // Unit of measurement
  "status": String,             // "completed", "running", "failed"
  "created_at": DateTime,
  "details": {
    "method": String,
    "model": String,
    "version": String
  }
}
```

**Key Fields for Dashboard**:
- `prediction`: For ADMET success rate
- `admet_property`: For ADMET pass rate by property
- `created_at`: For ADMET trend
- `status`: For success calculation

---

### 9. preformulation_reports

Formulation development reports.

```javascript
{
  "_id": ObjectId,
  "report_id": String,
  "candidate_id": String,
  "solubility": Number,
  "stability": String,
  "appearance": String,
  "created_at": DateTime,
  "updated_at": DateTime,
  "recommendations": Array
}
```

---

### 10. formulation_designs

Formulation composition and parameters.

```javascript
{
  "_id": ObjectId,
  "design_id": String,
  "candidate_id": String,
  "formulation_type": String,   // "tablet", "capsule", "solution"
  "excipients": Array,
  "dose_strength": Number,
  "created_at": DateTime,
  "status": String
}
```

---

### 11. experiments

Experimental records and lab data.

```javascript
{
  "_id": ObjectId,
  "experiment_id": String,
  "project_id": String,
  "researcher_id": String,
  "experiment_type": String,
  "description": String,
  "start_date": DateTime,
  "end_date": DateTime,
  "results": Object,
  "status": String,
  "created_at": DateTime
}
```

---

### 12. report_registry

Catalog of generated reports and exports.

```javascript
{
  "_id": ObjectId,
  "report_id": String,
  "title": String,
  "type": String,               // "summary", "detailed", "export"
  "generated_by": String,       // user_id
  "created_at": DateTime,
  "updated_at": DateTime,
  "file_path": String,
  "status": String,             // "ready", "generating", "archived"
  "content": {
    "sections": Array,
    "metrics": Object
  }
}
```

---

## Field Type Mapping

| Field Type | MongoDB Type | Dashboard Display |
|------------|-------------|------------------|
| String | String | Text |
| Number | Int32/Int64/Double | Formatted with K/M/B |
| DateTime | Date | ISO format or relative |
| Boolean | Boolean | Yes/No or ✓/✗ |
| Array | Array | Count or expanded |
| ObjectId | ObjectID | Hex string (truncated) |
| Object | Document | Details on expand |

---

## Recommended Indexes

For optimal dashboard performance, create these indexes:

```javascript
// user_activities
db.user_activities.createIndex({ "timestamp": 1 })
db.user_activities.createIndex({ "user_id": 1, "timestamp": -1 })

// screenings
db.screenings.createIndex({ "created_at": 1 })
db.screenings.createIndex({ "target_id": 1 })

// docking_jobs
db.docking_jobs.createIndex({ "created_at": 1 })
db.docking_jobs.createIndex({ "status": 1 })

// optimizations
db.optimizations.createIndex({ "optimization_score": -1 })
db.optimizations.createIndex({ "target_id": 1 })
db.optimizations.createIndex({ "created_at": 1 })

// admet_jobs
db.admet_jobs.createIndex({ "candidate_id": 1 })
db.admet_jobs.createIndex({ "created_at": 1 })
db.admet_jobs.createIndex({ "prediction": 1 })

// access_logs
db.access_logs.createIndex({ "timestamp": 1 })
db.access_logs.createIndex({ "user_id": 1 })
```

---

## Data Type Considerations

### Numeric Fields
- Large numbers are formatted (1000000 → "1M")
- Averages rounded to 2-3 decimal places
- Percentages shown with % symbol

### Date Fields
- Must be stored as MongoDB Date type
- Timezone: UTC recommended
- Format: ISO 8601 (2024-06-04T10:30:00Z)

### String Fields
- IDs should be consistent (user_id, target_id, etc.)
- Status values should be lowercase
- Category fields should have limited set of values

### Status Fields
Common values (not exhaustive):
- "active", "inactive"
- "pending", "running", "completed", "failed"
- "draft", "published", "archived"
- "pass", "fail", "uncertain"

---

## Schema Flexibility

The dashboard is **schema-flexible**:

1. **Missing Collections**: Simply don't appear in metrics
2. **Missing Fields**: Metrics using those fields return 0 or "N/A"
3. **Extra Fields**: Ignored by the dashboard
4. **Field Name Variants**: Dashboard looks for common field names
   - `created_at`, `createdAt`, `created_date`, `creation_time`
   - `updated_at`, `updatedAt`, `modified_date`
   - `status`, `state`, `stage`, `phase`

---

## Data Quality Guidelines

### For Accurate Metrics

1. **Populate Key Fields**:
   - Always include `created_at` and `status`
   - Include `user_id` for activity tracking
   - Include `*_id` fields for relationships

2. **Use Consistent Data Types**:
   - Dates: Always DateTime, not String
   - Numbers: Use Int or Double, not String
   - IDs: Use String or ObjectId, be consistent

3. **Maintain Referential Integrity**:
   - `target_id` in screenings should match target documents
   - `user_id` in activities should match user documents
   - `candidate_id` in optimizations should match candidates

4. **Status Values**:
   - Use lowercase
   - Use consistent naming across collections
   - Document valid values

---

## Schema Discovery Output

When the dashboard starts, it generates a detailed schema analysis in logs:

```
=== MONGODB SCHEMA ANALYSIS SUMMARY ===

Collection: users
  Document Count: 150
  Sample Count: 100
  Fields:
    - _id: objectId
    - user_id: string (null: 0%)
    - email: string (null: 0%)
    - name: string (null: 0%)
    - department: string (null: 5%)
    - created_at: datetime (null: 0%)
    ...
```

Check these logs to verify schema detection.

---

## Troubleshooting Schema Issues

### "No data available" for specific metric

**Possible Causes**:
1. Collection doesn't exist
2. Collection has documents but field names don't match
3. Field contains null or wrong data type
4. Date range filter excludes all data

**Solution**:
1. Verify collection exists: `db.collection_names()`
2. Check field names: `db.collection.findOne()`
3. Ensure created_at is DateTime type
4. Expand date range

### Metrics are zero

1. Check if collection has documents
2. Verify field names match expected schema
3. Check data types of fields
4. Review schema in sidebar

### Wrong metric values

1. Verify date fields are stored as DateTime (not String)
2. Check status field values (case-sensitive)
3. Ensure numeric fields are Number type
4. Review data in MongoDB directly

---

## Future Schema Considerations

As your platform evolves:

1. **Add New Collections**: Dashboard will auto-discover on next run
2. **Add Fields**: Include `created_at` and `status` when possible
3. **Rename Fields**: Update field name mapping in services
4. **Migrate Data**: Ensure backward compatibility during migration
5. **Archive Collections**: Remove from expected list in config.py

---

## Related Documentation

- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [config.py](config.py) - Configuration reference
- [utils/schema_analyzer.py](utils/schema_analyzer.py) - Schema analysis code

---

**Last Updated**: June 2024

For questions about schema, review the code in `utils/schema_analyzer.py` which performs the dynamic schema discovery.
