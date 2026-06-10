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

    def _build_query(self, date_field: str, start_date=None, end_date=None, user_email=None, email_field='user_email') -> dict:
        query = {}
        date_query = {}
        if start_date:
            date_query['$gte'] = start_date
        if end_date:
            date_query['$lte'] = end_date
        if date_query:
            query[date_field] = date_query
            
        if user_email:
            query[email_field] = user_email
        return query
    
    def get_total_users(self, users_collection: str = "users", start_date=None, end_date=None, user_email=None) -> int:
        """Get total user count"""
        query = self._build_query('created_at', start_date, end_date, user_email, 'email')
        return self.metrics.count_documents(users_collection, query)
    
    def get_active_users(self, days: int = 7, start_date=None, end_date=None, user_email=None) -> int:
        """Get active users in last N days"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=days)
            query = self._build_query('timestamp', start_date, end_date, user_email, 'user_email')
            
            pipeline = [
                {'$match': query},
                {
                    '$group': {
                        '_id': '$user_id'
                    }
                },
                {
                    '$count': 'active_users'
                }
            ]
            results = self.db_ops.aggregate("user_activities", pipeline)
            return results[0]['active_users'] if results else 0
        except Exception as e:
            logger.error(f"Error calculating active users: {str(e)}")
            return 0
    
    def get_new_users(self, days: int = 30, start_date=None, end_date=None, user_email=None) -> int:
        """Get new users in last N days"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=days)
        query = self._build_query('created_at', start_date, end_date, user_email, 'email')
        return self.db_ops.count_documents("users", query)
    
    def get_daily_active_users(self, days: int = 30, start_date=None, end_date=None, user_email=None) -> List[Dict]:
        """Get DAU trend"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=days)
            query = self._build_query('timestamp', start_date, end_date, user_email, 'user_email')
            
            pipeline = [
                {'$match': query},
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
            return self.db_ops.aggregate("user_activities", pipeline)
        except Exception as e:
            logger.error(f"Error calculating daily active users: {str(e)}")
            return []
    
    def get_monthly_active_users(self, months: int = 6, start_date=None, end_date=None, user_email=None) -> List[Dict]:
        """Get MAU trend"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=30*months)
            query = self._build_query('timestamp', start_date, end_date, user_email, 'user_email')
            
            pipeline = [
                {'$match': query},
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
    
    def get_session_count(self, days: int = 30, start_date=None, end_date=None, user_email=None) -> int:
        """Get session count"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=days)
            query = self._build_query('timestamp', start_date, end_date, user_email, 'user_email')
            return self.db_ops.count_documents("user_activities", query)
        except Exception as e:
            logger.error(f"Error getting session count: {str(e)}")
            return 0
    
    def get_top_active_users(self, limit: int = 10, start_date=None, end_date=None, user_email=None) -> List[Dict]:
        """Get top active users"""
        try:
            query = self._build_query('timestamp', start_date, end_date, user_email, 'user_email')
            pipeline = [
                {'$match': query},
                {
                    '$group': {
                        '_id': '$user_email',
                        'activity_count': {'$sum': 1}
                    }
                },
                {
                    '$sort': {'activity_count': -1}
                },
                {
                    '$limit': limit
                },
                {
                    '$project': {
                        'user_id': '$_id',
                        'activity_count': 1,
                        '_id': 0
                    }
                }
            ]
            return self.db_ops.aggregate("user_activities", pipeline)
        except Exception as e:
            logger.error(f"Error getting top active users: {str(e)}")
            return []
    
    def get_user_department_usage(self, limit: int = 10, start_date=None, end_date=None, user_email=None) -> List[Dict]:
        """Get department usage metrics mapping activity actions to departments dynamically"""
        try:
            query = self._build_query('timestamp', start_date, end_date, user_email, 'user_email')
            pipeline = [
                {'$match': query},
                {
                    '$project': {
                        'user_id': 1,
                        'department': {
                            '$switch': {
                                'branches': [
                                    {
                                        'case': {'$in': ['$action', ['POCKET_SCAN', 'SEARCH_TARGET']]},
                                        'then': 'Drug Discovery'
                                    },
                                    {
                                        'case': {'$in': ['$action', ['LOGIN', 'REGISTER']]},
                                        'then': 'User Management'
                                    },
                                    {
                                        'case': {'$in': ['$action', ['SYSTEM_CHECK']]},
                                        'then': 'IT Operations'
                                    }
                                ],
                                'default': 'General'
                            }
                        }
                    }
                },
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
    
    def get_activity_heatmap_data(self, days: int = 30, start_date=None, end_date=None, user_email=None) -> pd.DataFrame:
        """Get activity heatmap data (day of week vs hour)"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=days)
            query = self._build_query('timestamp', start_date, end_date, user_email, 'user_email')
            pipeline = [
                {'$match': query},
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
    
    def get_login_trend(self, days: int = 30, start_date=None, end_date=None, user_email=None) -> List[Dict]:
        """Get login trend over time"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=days)
            query = self._build_query('timestamp', start_date, end_date, user_email, 'user')
            pipeline = [
                {'$match': query},
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
        """Calculate engagement score for a user"""
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
