"""
Discovery Service
Handles database schema discovery and analysis
"""

import logging
import streamlit as st
from typing import Dict, List, Any
from utils.schema_analyzer import SchemaAnalyzer
import config

logger = logging.getLogger(__name__)


class DiscoveryService:
    """Service for database discovery and schema analysis"""
    
    def __init__(self):
        self.analyzer = SchemaAnalyzer()
        self.schemas = None
        self.data_dictionary = None
    
    @st.cache_resource
    def get_schema_analyzer(_self):
        """Get cached schema analyzer"""
        return SchemaAnalyzer()
    
    def discover_all_collections(self) -> Dict[str, Dict]:
        """
        Discover all collections and their schemas
        
        Returns:
            Dictionary of collection schemas
        """
        try:
            logger.info("Starting database discovery...")
            
            # Get analyzer
            analyzer = self.get_schema_analyzer()
            
            # Discover all collections
            collections = analyzer.db_ops.get_collections()
            logger.info(f"Found {len(collections)} collections: {collections}")
            
            # Analyze each collection
            schemas = {}
            for collection_name in collections:
                logger.info(f"Analyzing {collection_name}...")
                schema = analyzer.analyze_collection(collection_name)
                schemas[collection_name] = schema
            
            self.schemas = schemas
            
            # Generate data dictionary
            self.data_dictionary = analyzer.generate_data_dictionary(schemas)
            
            # Print summary
            analyzer.print_schema_summary(schemas)
            
            logger.info(f"Database discovery completed for {len(schemas)} collections")
            return schemas
        
        except Exception as e:
            logger.error(f"Error discovering collections: {str(e)}")
            raise
    
    def get_collection_schema(self, collection_name: str) -> Dict:
        """Get schema for a specific collection"""
        if self.schemas is None:
            self.discover_all_collections()
        
        return self.schemas.get(collection_name, {})
    
    def get_data_dictionary(self) -> Dict:
        """Get comprehensive data dictionary"""
        if self.data_dictionary is None:
            self.discover_all_collections()
        
        return self.data_dictionary or {}
    
    def get_available_collections(self) -> List[str]:
        """Get list of available collections"""
        if self.schemas is None:
            self.discover_all_collections()
        
        return list(self.schemas.keys()) if self.schemas else []
    
    def get_collection_field_names(self, collection_name: str) -> List[str]:
        """Get field names for a collection"""
        schema = self.get_collection_schema(collection_name)
        return list(schema.get('fields', {}).keys())
    
    def get_date_fields(self, collection_name: str) -> List[str]:
        """Get date fields for a collection"""
        schema = self.get_collection_schema(collection_name)
        return schema.get('date_fields', [])
    
    def get_status_fields(self, collection_name: str) -> List[str]:
        """Get status fields for a collection"""
        schema = self.get_collection_schema(collection_name)
        return schema.get('status_fields', [])
    
    def get_id_fields(self, collection_name: str) -> List[str]:
        """Get ID fields for a collection"""
        schema = self.get_collection_schema(collection_name)
        return schema.get('id_fields', [])
    
    def get_collection_count(self, collection_name: str) -> int:
        """Get document count for a collection"""
        schema = self.get_collection_schema(collection_name)
        return schema.get('document_count', 0)
    
    def print_discovery_report(self):
        """Print discovery report to log"""
        if self.data_dictionary is None:
            self.discover_all_collections()
        
        logger.info("\n" + "="*80)
        logger.info("DATABASE DISCOVERY REPORT")
        logger.info("="*80)
        logger.info(f"Generated at: {self.data_dictionary.get('generated_at')}")
        logger.info(f"Database: {self.data_dictionary.get('database')}")
        logger.info(f"\nCollections discovered: {len(self.data_dictionary.get('collections', {}))}")
        
        for coll_name, coll_info in self.data_dictionary.get('collections', {}).items():
            logger.info(f"\n  {coll_name}:")
            logger.info(f"    Row Count: {coll_info.get('row_count')}")
            logger.info(f"    Fields: {len(coll_info.get('fields', {}))}")
            logger.info(f"    Date Fields: {coll_info.get('date_fields')}")
            logger.info(f"    Status Fields: {coll_info.get('status_fields')}")
        
        logger.info("\n" + "="*80)
