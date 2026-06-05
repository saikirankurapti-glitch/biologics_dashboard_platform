"""
Metrics calculation utilities
Provides common KPI and metric calculations
"""

import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
from database.mongodb import MongoDBOperations

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculate various metrics from MongoDB data"""
    
    def __init__(self):
        self.db_ops = MongoDBOperations()
    
    def count_documents(self, collection_name: str, query: Dict = None) -> int:
        """Count documents in collection"""
        return self.db_ops.count_documents(collection_name, query)
    
    def get_active_users(self, days: int = 7, activity_collection: str = "user_activities") -> int:
        """Get count of active users in last N days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            pipeline = [
                {
                    '$match': {
                        'timestamp': {'$gte': cutoff_date}
                    }
                },
                {
                    '$group': {
                        '_id': '$user_id'
                    }
                },
                {
                    '$count': 'active_users'
                }
            ]
            results = self.db_ops.aggregate(activity_collection, pipeline)
            return results[0]['active_users'] if results else 0
        except Exception as e:
            logger.error(f"Error calculating active users: {str(e)}")
            return 0
    
    def get_daily_active_users(self, days: int = 30, activity_collection: str = "user_activities") -> List[Dict]:
        """Get daily active users for trend"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            pipeline = [
                {
                    '$match': {
                        'timestamp': {'$gte': cutoff_date}
                    }
                },
                {
                    '$group': {
                        '_id': {
                            '$dateToString': {
                                'format': '%Y-%m-%d',
                                'date': '$timestamp'
                            }
                        },
                        'active_users': {'$addToSet': '$user_id'},
                        'activity_count': {'$sum': 1}
                    }
                },
                {
                    '$project': {
                        'date': '$_id',
                        'user_count': {'$size': '$active_users'},
                        'activity_count': 1,
                        '_id': 0
                    }
                },
                {
                    '$sort': {'date': 1}
                }
            ]
            return self.db_ops.aggregate(activity_collection, pipeline)
        except Exception as e:
            logger.error(f"Error calculating daily active users: {str(e)}")
            return []
    
    def get_new_users(self, days: int = 30, users_collection: str = "users") -> int:
        """Get count of new users in last N days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            return self.db_ops.count_documents(
                users_collection,
                {'created_at': {'$gte': cutoff_date}} if cutoff_date else {}
            )
        except Exception as e:
            logger.error(f"Error calculating new users: {str(e)}")
            return 0
    
    def get_collection_trend(self, collection_name: str, date_field: str, days: int = 30) -> List[Dict]:
        """Get trend data for a collection by date"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            pipeline = [
                {
                    '$match': {
                        date_field: {'$gte': cutoff_date}
                    }
                },
                {
                    '$group': {
                        '_id': {
                            '$dateToString': {
                                'format': '%Y-%m-%d',
                                'date': f'${date_field}'
                            }
                        },
                        'count': {'$sum': 1}
                    }
                },
                {
                    '$project': {
                        'date': '$_id',
                        'count': 1,
                        '_id': 0
                    }
                },
                {
                    '$sort': {'date': 1}
                }
            ]
            return self.db_ops.aggregate(collection_name, pipeline)
        except Exception as e:
            logger.error(f"Error calculating trend for {collection_name}: {str(e)}")
            return []
    
    def get_field_value_counts(self, collection_name: str, field_name: str, limit: int = 10) -> List[Dict]:
        """Get value counts for a field"""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': f'${field_name}',
                        'count': {'$sum': 1}
                    }
                },
                {
                    '$sort': {'count': -1}
                },
                {
                    '$limit': limit
                }
            ]
            results = self.db_ops.aggregate(collection_name, pipeline)
            return [{'value': r['_id'], 'count': r['count']} for r in results]
        except Exception as e:
            logger.error(f"Error getting value counts for {field_name}: {str(e)}")
            return []
    
    def get_funnel_metrics(self, metrics_dict: Dict[str, int]) -> List[Dict]:
        """
        Convert metric counts to funnel format
        
        Args:
            metrics_dict: {'stage_name': count, ...}
        
        Returns:
            List of funnel stages with conversion rates
        """
        try:
            if not metrics_dict:
                return []
            
            stages = []
            prev_count = None
            
            for stage_name, count in metrics_dict.items():
                stage = {
                    'stage': stage_name,
                    'count': count,
                    'conversion_rate': None
                }
                
                if prev_count is not None and prev_count > 0:
                    stage['conversion_rate'] = round((count / prev_count) * 100, 2)
                
                stages.append(stage)
                prev_count = count
            
            return stages
        except Exception as e:
            logger.error(f"Error calculating funnel metrics: {str(e)}")
            return []
    
    def get_field_average(self, collection_name: str, field_name: str, query: Dict = None) -> float:
        """Get average of a numeric field"""
        try:
            pipeline = [
                {'$match': query or {}},
                {
                    '$group': {
                        '_id': None,
                        'average': {'$avg': f'${field_name}'}
                    }
                }
            ]
            results = self.db_ops.aggregate(collection_name, pipeline)
            return results[0]['average'] if results else 0
        except Exception as e:
            logger.error(f"Error calculating average for {field_name}: {str(e)}")
            return 0
    
    def get_field_max(self, collection_name: str, field_name: str, query: Dict = None) -> Any:
        """Get maximum of a field"""
        try:
            pipeline = [
                {'$match': query or {}},
                {
                    '$group': {
                        '_id': None,
                        'max_value': {'$max': f'${field_name}'}
                    }
                }
            ]
            results = self.db_ops.aggregate(collection_name, pipeline)
            return results[0]['max_value'] if results else None
        except Exception as e:
            logger.error(f"Error calculating max for {field_name}: {str(e)}")
            return None
    
    def get_status_distribution(self, collection_name: str, status_field: str = "status") -> List[Dict]:
        """Get distribution of status values"""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': f'${status_field}',
                        'count': {'$sum': 1}
                    }
                },
                {
                    '$sort': {'count': -1}
                }
            ]
            results = self.db_ops.aggregate(collection_name, pipeline)
            return [{'status': r['_id'], 'count': r['count']} for r in results]
        except Exception as e:
            logger.error(f"Error getting status distribution: {str(e)}")
            return []
    
    def get_top_users(self, activity_collection: str = "user_activities", limit: int = 10) -> List[Dict]:
        """Get top active users"""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': '$user_id',
                        'activity_count': {'$sum': 1}
                    }
                },
                {
                    '$sort': {'activity_count': -1}
                },
                {
                    '$limit': limit
                }
            ]
            results = self.db_ops.aggregate(activity_collection, pipeline)
            return [{'user_id': r['_id'], 'activity_count': r['activity_count']} for r in results]
        except Exception as e:
            logger.error(f"Error getting top users: {str(e)}")
            return []
    
    def convert_to_dataframe(self, data: List[Dict]) -> pd.DataFrame:
        """Convert list of dicts to pandas DataFrame"""
        try:
            return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"Error converting to DataFrame: {str(e)}")
            return pd.DataFrame()
    
    def get_success_rate(self, collection_name: str, total_field: str, success_field: str = None, success_value: Any = "success") -> float:
        """
        Calculate success rate for a collection
        
        Args:
            collection_name: Collection to analyze
            total_field: Field that determines if record exists
            success_field: Field that indicates success (if None, uses total)
            success_value: Value indicating success
        
        Returns:
            Success rate percentage
        """
        try:
            total = self.db_ops.count_documents(collection_name)
            if total == 0:
                return 0
            
            if success_field:
                success_count = self.db_ops.count_documents(
                    collection_name,
                    {success_field: success_value}
                )
            else:
                success_count = total
            
            return round((success_count / total) * 100, 2)
        except Exception as e:
            logger.error(f"Error calculating success rate: {str(e)}")
            return 0
