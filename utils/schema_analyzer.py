"""
MongoDB Schema Analyzer
Discovers schema, infers data types, and generates data dictionary
"""

import logging
from typing import Dict, List, Any, Set, Tuple
from datetime import datetime
from bson import ObjectId
from database.mongodb import MongoDBOperations
import config
import json

logger = logging.getLogger(__name__)


class SchemaAnalyzer:
    """Analyzes MongoDB collections and generates schema information"""
    
    def __init__(self):
        self.db_ops = MongoDBOperations()
        self.schema_cache = {}
    
    def infer_field_type(self, value: Any) -> str:
        """Infer data type from value"""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, datetime):
            return "datetime"
        elif isinstance(value, ObjectId):
            return "objectId"
        elif isinstance(value, dict):
            return "object"
        elif isinstance(value, list):
            return "array"
        else:
            return "unknown"
    
    def analyze_collection(self, collection_name: str, sample_size: int = 100) -> Dict[str, Any]:
        """
        Analyze collection schema
        
        Returns:
            {
                'collection_name': str,
                'document_count': int,
                'fields': {
                    'field_name': {
                        'types': [str],
                        'null_count': int,
                        'unique_count': int,
                        'sample_values': [Any]
                    }
                },
                'date_fields': [str],
                'status_fields': [str],
                'id_fields': [str]
            }
        """
        try:
            collection = self.db_ops.db[collection_name]
            
            # Get document count
            doc_count = collection.count_documents({})
            
            # Sample documents
            documents = list(collection.find().limit(sample_size))
            
            if not documents:
                return {
                    'collection_name': collection_name,
                    'document_count': 0,
                    'fields': {},
                    'date_fields': [],
                    'status_fields': [],
                    'id_fields': []
                }
            
            # Analyze fields
            field_info = {}
            all_field_names = set()
            
            for doc in documents:
                for field_name, value in doc.items():
                    all_field_names.add(field_name)
                    
                    if field_name not in field_info:
                        field_info[field_name] = {
                            'types': set(),
                            'null_count': 0,
                            'values': set(),
                            'sample_values': []
                        }
                    
                    field_data = field_info[field_name]
                    
                    if value is None:
                        field_data['null_count'] += 1
                    else:
                        field_type = self.infer_field_type(value)
                        field_data['types'].add(field_type)
                        
                        # Collect sample values for non-object/array types
                        if field_type not in ['object', 'array'] and len(field_data['sample_values']) < 5:
                            field_data['sample_values'].append(value)
                        
                        # For strings, try to count unique values
                        if field_type == 'string' and len(field_data['values']) < 1000:
                            field_data['values'].add(str(value))
            
            # Identify date and status fields
            date_fields = []
            status_fields = []
            id_fields = []
            
            for field_name in all_field_names:
                if field_info[field_name]['types']:
                    types = list(field_info[field_name]['types'])
                    
                    # Date field detection
                    if 'datetime' in types or field_name.lower() in ['date', 'created_at', 'updated_at', 'timestamp', 'created_date', 'updated_date']:
                        date_fields.append(field_name)
                    
                    # Status field detection
                    if field_name.lower() in ['status', 'state', 'stage', 'phase', 'state_name']:
                        status_fields.append(field_name)
                    
                    # ID field detection
                    if field_name.lower() in ['_id', 'id', 'user_id', 'job_id', 'target_id', 'screening_id']:
                        id_fields.append(field_name)
            
            # Build final schema
            schema = {
                'collection_name': collection_name,
                'document_count': doc_count,
                'sample_count': len(documents),
                'fields': {}
            }
            
            for field_name, field_data in field_info.items():
                schema['fields'][field_name] = {
                    'types': sorted(list(field_data['types'])),
                    'null_count': field_data['null_count'],
                    'null_percentage': round((field_data['null_count'] / len(documents)) * 100, 2),
                    'unique_count': len(field_data['values']) if field_data['values'] else 'unknown',
                    'sample_values': field_data['sample_values']
                }
            
            schema['date_fields'] = date_fields
            schema['status_fields'] = status_fields
            schema['id_fields'] = id_fields
            
            self.schema_cache[collection_name] = schema
            return schema
        
        except Exception as e:
            logger.error(f"Error analyzing collection {collection_name}: {str(e)}")
            return {
                'collection_name': collection_name,
                'document_count': 0,
                'fields': {},
                'error': str(e)
            }
    
    def analyze_all_collections(self, collection_names: List[str] = None) -> Dict[str, Dict]:
        """
        Analyze all collections and return comprehensive schema
        """
        if collection_names is None:
            collection_names = self.db_ops.get_collections()
        
        all_schemas = {}
        for collection_name in collection_names:
            logger.info(f"Analyzing collection: {collection_name}")
            all_schemas[collection_name] = self.analyze_collection(collection_name)
        
        return all_schemas
    
    def detect_relationships(self, schemas: Dict[str, Dict]) -> Dict[str, List[Dict]]:
        """
        Detect relationships between collections based on field names and types
        
        Returns:
            {
                'potential_relationships': [
                    {
                        'from_collection': str,
                        'to_collection': str,
                        'from_field': str,
                        'to_field': str,
                        'confidence': float
                    }
                ]
            }
        """
        relationships = []
        
        try:
            # Build field mapping
            field_map = {}  # field_name -> [(collection, field), ...]
            
            for coll_name, schema in schemas.items():
                for field_name in schema.get('fields', {}).keys():
                    if field_name not in field_map:
                        field_map[field_name] = []
                    field_map[field_name].append((coll_name, field_name))
            
            # Find potential relationships
            for field_name, occurrences in field_map.items():
                if len(occurrences) > 1:
                    # Field appears in multiple collections
                    for i, (coll1, field1) in enumerate(occurrences):
                        for coll2, field2 in occurrences[i+1:]:
                            # Check for ID-like naming patterns
                            if '_id' in field_name or 'id' in field_name:
                                relationships.append({
                                    'from_collection': coll1,
                                    'to_collection': coll2,
                                    'from_field': field1,
                                    'to_field': field2,
                                    'confidence': 0.8,
                                    'type': 'potential_foreign_key'
                                })
        
        except Exception as e:
            logger.error(f"Error detecting relationships: {str(e)}")
        
        return {'potential_relationships': relationships}
    
    def generate_data_dictionary(self, schemas: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Generate comprehensive data dictionary
        """
        # Use the connected database name when available, otherwise fall back to configured name
        db_name = getattr(self.db_ops.db, 'name', None) if hasattr(self, 'db_ops') else None
        if not db_name:
            db_name = getattr(config, 'DATABASE_NAME', 'unknown')

        data_dictionary = {
            'generated_at': datetime.now().isoformat(),
            'database': db_name,
            'collections': {}
        }
        
        for collection_name, schema in schemas.items():
            data_dictionary['collections'][collection_name] = {
                'row_count': schema.get('document_count', 0),
                'sample_count': schema.get('sample_count', 0),
                'fields': schema.get('fields', {}),
                'date_fields': schema.get('date_fields', []),
                'status_fields': schema.get('status_fields', []),
                'id_fields': schema.get('id_fields', [])
            }
        
        # Add relationships
        data_dictionary['relationships'] = self.detect_relationships(schemas)
        
        return data_dictionary
    
    def get_cached_schema(self, collection_name: str) -> Dict:
        """Get schema from cache"""
        return self.schema_cache.get(collection_name, {})
    
    def print_schema_summary(self, schemas: Dict[str, Dict]):
        """Print readable schema summary"""
        logger.info("\n" + "="*80)
        logger.info("MONGODB SCHEMA ANALYSIS SUMMARY")
        logger.info("="*80)
        
        for collection_name, schema in schemas.items():
            logger.info(f"\nCollection: {collection_name}")
            logger.info(f"  Document Count: {schema.get('document_count', 0)}")
            logger.info(f"  Sample Count: {schema.get('sample_count', 0)}")
            
            if schema.get('fields'):
                logger.info("  Fields:")
                for field_name, field_info in schema['fields'].items():
                    types_str = ", ".join(field_info.get('types', []))
                    null_pct = field_info.get('null_percentage', 0)
                    logger.info(f"    - {field_name}: {types_str} (null: {null_pct}%)")
