"""
MongoDB connection and operations module
Provides read-only operations for the Biologics Discovery Platform
"""

import logging
from typing import List, Dict, Any, Optional

try:
    import dns.resolver
    DNSPYTHON_AVAILABLE = True
except ImportError:
    dns = None
    DNSPYTHON_AVAILABLE = False

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import config

logger = logging.getLogger(__name__)


class MongoDBConnection:
    """Singleton MongoDB connection handler"""
    
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self):
        """Establish MongoDB connection"""
        if self._client is None:
            try:
                self._configure_custom_dns()
                self._client = MongoClient(
                    config.MONGODB_URL,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000,
                    socketTimeoutMS=None,
                    retryWrites=False
                )
                # Verify connection
                self._client.admin.command('ping')
                self._db = self._client[config.DATABASE_NAME]
                logger.info(f"Successfully connected to MongoDB database: {config.DATABASE_NAME}")
            except Exception as e:
                # Reset connection state so that next retry can attempt reconnecting
                self._client = None
                self._db = None
                msg = (
                    f"Failed to connect to MongoDB at {config.MONGODB_URL}. "
                    "Please verify your MONGODB_URL, network access, and DNS settings."
                )
                logger.error(f"{msg} Error: {e}")
                raise ConnectionFailure(msg) from e

    def _configure_custom_dns(self):
        """Configure custom DNS servers for SRV resolution if provided."""
        if not config.MONGODB_DNS_SERVERS:
            return

        if not config.MONGODB_URL.lower().startswith("mongodb+srv://"):
            return

        if not DNSPYTHON_AVAILABLE:
            logger.warning("Custom DNS servers were configured, but dnspython is not installed.")
            return

        try:
            resolver = dns.resolver.Resolver(configure=False)
            resolver.nameservers = config.MONGODB_DNS_SERVERS
            dns.resolver.default_resolver = resolver
            logger.info(f"Using custom DNS resolver nameservers: {config.MONGODB_DNS_SERVERS}")
        except Exception as e:
            logger.warning(f"Unable to configure custom DNS resolver: {e}")
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self._client is not None:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB connection closed")
    
    def get_db(self):
        """Get database instance"""
        if self._db is None:
            self.connect()
        return self._db
    
    def get_collection(self, collection_name: str):
        """Get collection from database"""
        db = self.get_db()
        return db[collection_name]


def get_mongo_connection():
    """Get singleton MongoDB connection"""
    return MongoDBConnection()


class MongoDBOperations:
    """READ-ONLY MongoDB operations"""
    
    def __init__(self):
        self.connection = get_mongo_connection()
        try:
            self.connection.connect()
        except Exception as e:
            logger.warning(f"Initial connection to MongoDB failed: {e}")
            
    @property
    def db(self):
        return self.connection.get_db()
    
    def find(self, collection_name: str, query: Dict = None, projection: Dict = None, limit: int = 0) -> List[Dict]:
        """
        Find documents in collection (READ-ONLY)
        
        Args:
            collection_name: Name of the collection
            query: MongoDB query filter
            projection: Fields to include/exclude
            limit: Maximum number of documents to return
        
        Returns:
            List of documents
        """
        try:
            collection = self.db[collection_name]
            query = query or {}
            cursor = collection.find(query, projection)
            if limit > 0:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Error finding documents in {collection_name}: {str(e)}")
            return []
    
    def find_one(self, collection_name: str, query: Dict = None, projection: Dict = None) -> Optional[Dict]:
        """
        Find single document (READ-ONLY)
        
        Args:
            collection_name: Name of the collection
            query: MongoDB query filter
            projection: Fields to include/exclude
        
        Returns:
            Single document or None
        """
        try:
            collection = self.db[collection_name]
            query = query or {}
            return collection.find_one(query, projection)
        except Exception as e:
            logger.error(f"Error finding document in {collection_name}: {str(e)}")
            return None
    
    def aggregate(self, collection_name: str, pipeline: List[Dict]) -> List[Dict]:
        """
        Aggregate documents using pipeline (READ-ONLY)
        
        Args:
            collection_name: Name of the collection
            pipeline: MongoDB aggregation pipeline
        
        Returns:
            List of aggregated results
        """
        try:
            collection = self.db[collection_name]
            return list(collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error aggregating in {collection_name}: {str(e)}")
            return []
    
    def count_documents(self, collection_name: str, query: Dict = None) -> int:
        """
        Count documents (READ-ONLY)
        
        Args:
            collection_name: Name of the collection
            query: MongoDB query filter
        
        Returns:
            Count of matching documents
        """
        try:
            collection = self.db[collection_name]
            query = query or {}
            return collection.count_documents(query)
        except Exception as e:
            logger.error(f"Error counting documents in {collection_name}: {str(e)}")
            return 0
    
    def get_collections(self) -> List[str]:
        """Get all collections in database"""
        try:
            return self.db.list_collection_names()
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            return []
    
    def get_collection_stats(self, collection_name: str) -> Dict:
        """Get statistics for a collection"""
        try:
            collection = self.db[collection_name]
            return {
                'count': collection.count_documents({}),
                'indexes': collection.list_indexes()
            }
        except Exception as e:
            logger.error(f"Error getting stats for {collection_name}: {str(e)}")
            return {}

    def insert_one(self, collection_name: str, document: Dict) -> Any:
        """
        Insert a single document (Write operation)
        
        Args:
            collection_name: Name of the collection
            document: Document to insert
            
        Returns:
            Inserted document ID or None
        """
        try:
            collection = self.db[collection_name]
            result = collection.insert_one(document)
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error inserting document into {collection_name}: {str(e)}")
            return None
