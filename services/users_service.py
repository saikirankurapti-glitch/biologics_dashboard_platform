"""
Users Service
Handles user-related metrics and analytics
"""

import logging
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import pandas as pd
from utils.metrics import MetricsCalculator
from database.mongodb import MongoDBOperations

logger = logging.getLogger(__name__)


class UsersService:
    """Service for user analytics metrics"""
    
    def __init__(self):
        self.metrics = MetricsCalculator()
        self.db_ops = MongoDBOperations()
    
    def get_total_users(self, users_collection: str = "users") -> int:
        """Get total user count"""
        return self.metrics.count_documents(users_collection)
    
    def get_active_users(self, days: int = 7) -> int:
        """Get active users in last N days"""
        return self.metrics.get_active_users(days=days)
    
    def get_new_users(self, days: int = 30) -> int:
        """Get new users in last N days"""
        return self.metrics.get_new_users(days=days)
    
    def get_daily_active_users(self, days: int = 30) -> List[Dict]:
        """Get DAU trend"""
        return self.metrics.get_daily_active_users(days=days)
    
    def get_monthly_active_users(self, months: int = 6) -> List[Dict]:
        """Get MAU trend"""
        try:
            cutoff_date = datetime.now() - timedelta(days=30*months)
            pipeline = [
                {
                    '$match': {
                        'timestamp': {'$gte': cutoff_date}
                    }
                },
                {
                    '$group': {
                        '_id': {
                            'year': {'$year': '$timestamp'},
                            'month': {'$month': '$timestamp'}
                        },
                        'active_users': {'$addToSet': '$user_id'}
                    }
                },
                {
                    '$project': {
                        '_id': 0,
                        'year_month': {
                            '$concat': [
                                {'$toString': '$_id.year'},
                                '-',
                                {'$toString': '$_id.month'}
                            ]
                        },
                        'user_count': {'$size': '$active_users'}
                    }
                },
                {
                    '$sort': {'year_month': 1}
                }
            ]
            results = self.db_ops.aggregate("user_activities", pipeline)
            return [{'month': r['year_month'], 'user_count': r['user_count']} for r in results]
        except Exception as e:
            logger.error(f"Error calculating MAU: {str(e)}")
            return []
    
    def get_session_count(self, days: int = 30) -> int:
        """Get session count"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            return self.db_ops.count_documents(
                "user_activities",
                {'timestamp': {'$gte': cutoff_date}}
            )
        except Exception as e:
            logger.error(f"Error getting session count: {str(e)}")
            return 0
    
    def get_top_active_users(self, limit: int = 10) -> List[Dict]:
        """Get top active users"""
        return self.metrics.get_top_users(limit=limit)
    
    def get_user_department_usage(self, limit: int = 10) -> List[Dict]:
        """Get department usage metrics"""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': '$department',
                        'user_count': {'$addToSet': '$user_id'},
                        'total_activities': {'$sum': 1}
                    }
                },
                {
                    '$project': {
                        '_id': 0,
                        'department': '$_id',
                        'user_count': {'$size': '$user_count'},
                        'activity_count': '$total_activities'
                    }
                },
                {
                    '$sort': {'activity_count': -1}
                },
                {
                    '$limit': limit
                }
            ]
            return self.db_ops.aggregate("user_activities", pipeline)
        except Exception as e:
            logger.error(f"Error getting department usage: {str(e)}")
            return []
    
    def get_activity_heatmap_data(self, days: int = 30) -> pd.DataFrame:
        """Get activity heatmap data (day of week vs hour)"""
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
                            'day_of_week': {'$dayOfWeek': '$timestamp'},
                            'hour': {'$hour': '$timestamp'}
                        },
                        'count': {'$sum': 1}
                    }
                }
            ]
            
            results = self.db_ops.aggregate("user_activities", pipeline)
            
            # Convert to heatmap format
            heatmap_data = {}
            day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            
            for result in results:
                day = day_names[result['_id']['day_of_week'] - 1]
                hour = result['_id']['hour']
                if day not in heatmap_data:
                    heatmap_data[day] = {}
                heatmap_data[day][hour] = result['count']
            
            # Convert to DataFrame
            df = pd.DataFrame(heatmap_data).fillna(0)
            return df
        except Exception as e:
            logger.error(f"Error getting activity heatmap: {str(e)}")
            return pd.DataFrame()
    
    def get_login_trend(self, days: int = 30) -> List[Dict]:
        """Get login trend over time"""
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
                        'login_count': {'$sum': 1}
                    }
                },
                {
                    '$sort': {'_id': 1}
                }
            ]
            
            results = self.db_ops.aggregate("access_logs", pipeline)
            return [{'date': r['_id'], 'logins': r['login_count']} for r in results]
        except Exception as e:
            logger.error(f"Error getting login trend: {str(e)}")
            return []
    
    def get_user_engagement_score(self, user_id: str) -> Dict:
        """
        Calculate engagement score for a user
        
        Returns:
            {
                'user_id': str,
                'activity_count': int,
                'last_active': datetime,
                'engagement_score': float
            }
        """
        try:
            pipeline = [
                {
                    '$match': {'user_id': user_id}
                },
                {
                    '$group': {
                        '_id': '$user_id',
                        'activity_count': {'$sum': 1},
                        'last_active': {'$max': '$timestamp'}
                    }
                }
            ]
            
            results = self.db_ops.aggregate("user_activities", pipeline)
            if not results:
                return {'user_id': user_id, 'activity_count': 0, 'engagement_score': 0}
            
            result = results[0]
            activity_count = result['activity_count']
            
            # Simple engagement score based on activity count
            engagement_score = min(100, activity_count / 10)
            
            return {
                'user_id': result['_id'],
                'activity_count': activity_count,
                'last_active': result['last_active'],
                'engagement_score': round(engagement_score, 2)
            }
        except Exception as e:
            logger.error(f"Error calculating engagement score: {str(e)}")
            return {'user_id': user_id, 'activity_count': 0, 'engagement_score': 0}
