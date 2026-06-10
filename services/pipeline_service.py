"""
Pipeline Service
Handles discovery pipeline metrics
"""

import logging
from typing import Dict, List
from datetime import datetime, timedelta
from utils.metrics import MetricsCalculator
from database.mongodb import MongoDBOperations

logger = logging.getLogger(__name__)


class PipelineService:
    """Service for discovery pipeline metrics"""
    
    def __init__(self):
        self.metrics = MetricsCalculator()
        self.db_ops = MongoDBOperations()

    def _build_query(self, date_field: str = 'created_at', start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> dict:
        query = {}
        date_query = {}
        if start_date:
            date_query['$gte'] = start_date
        if end_date:
            date_query['$lte'] = end_date
        if date_query:
            query[date_field] = date_query
            
        if user_email:
            query['created_by'] = user_email
            
        if target_id and target_id != "All Targets" and target_id != "All Projects":
            query['target_id'] = target_id
            
        if status and status != "All Status":
            if status == "Active":
                query['status'] = {'$in': ['active', 'running', 'Planned', 'planned']}
            elif status == "Completed":
                query['status'] = {'$in': ['completed', 'Completed', 'success', 'Success']}
            elif status == "In Progress":
                query['status'] = {'$in': ['in progress', 'In Progress', 'running', 'Running']}
            else:
                query['status'] = status
        return query
    
    # ============ Target Metrics ============
    def get_targets_loaded(self, targets_collection: str = "targets", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> int:
        """Get total targets loaded"""
        query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
        return self.metrics.count_documents(targets_collection, query)
    
    def get_unique_proteins(self, targets_collection: str = "targets", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> int:
        """Get count of unique proteins (estimate based on targets)"""
        try:
            query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
            pipeline = [
                {'$match': query},
                {
                    '$group': {
                        '_id': '$protein_id'
                    }
                },
                {
                    '$count': 'unique_proteins'
                }
            ]
            results = self.db_ops.aggregate(targets_collection, pipeline)
            return results[0]['unique_proteins'] if results else 0
        except Exception as e:
            logger.error(f"Error getting unique proteins: {str(e)}")
            return 0
    
    # ============ Screening Metrics ============
    def get_screening_runs(self, screenings_collection: str = "screenings", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> int:
        """Get total screening runs"""
        query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
        return self.metrics.count_documents(screenings_collection, query)
    
    def get_molecules_screened(self, screenings_collection: str = "screenings", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> int:
        """Get total molecules screened"""
        try:
            query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
            pipeline = [
                {'$match': query},
                {
                    '$group': {
                        '_id': None,
                        'total_molecules': {'$sum': {'$cond': [{'$isNumber': '$molecule_count'}, '$molecule_count', 0]}}
                    }
                }
            ]
            results = self.db_ops.aggregate(screenings_collection, pipeline)
            return results[0]['total_molecules'] if results else 0
        except Exception as e:
            logger.error(f"Error getting molecules screened: {str(e)}")
            return 0
    
    def get_hits_identified(self, screenings_collection: str = "screenings", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> int:
        """Get total hits identified"""
        try:
            query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
            pipeline = [
                {'$match': query},
                {
                    '$group': {
                        '_id': None,
                        'total_hits': {'$sum': {'$cond': [{'$isNumber': '$hits_count'}, '$hits_count', 0]}}
                    }
                }
            ]
            results = self.db_ops.aggregate(screenings_collection, pipeline)
            return results[0]['total_hits'] if results else 0
        except Exception as e:
            logger.error(f"Error getting hits identified: {str(e)}")
            return 0
    
    def get_hit_rate(self, screenings_collection: str = "screenings", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> float:
        """Calculate hit rate percentage"""
        try:
            molecules = self.get_molecules_screened(screenings_collection, start_date, end_date, user_email, target_id, status)
            hits = self.get_hits_identified(screenings_collection, start_date, end_date, user_email, target_id, status)
            
            if molecules == 0:
                return 0
            
            return round((hits / molecules) * 100, 2)
        except Exception as e:
            logger.error(f"Error calculating hit rate: {str(e)}")
            return 0
    
    def get_screening_trend(self, days: int = 30, screenings_collection: str = "screenings", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> List[Dict]:
        """Get screening trend over time"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=days)
            query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
            pipeline = [
                {'$match': query},
                {
                    '$group': {
                        '_id': {
                            '$dateToString': {
                                'format': '%Y-%m-%d',
                                'date': '$created_at'
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
            return self.db_ops.aggregate(screenings_collection, pipeline)
        except Exception as e:
            logger.error(f"Error screening trend: {str(e)}")
            return []
    
    # ============ Docking Metrics ============
    def get_docking_jobs(self, docking_collection: str = "docking_jobs", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> int:
        """Get total docking jobs"""
        query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
        return self.metrics.count_documents(docking_collection, query)
    
    def get_docking_success_rate(self, docking_collection: str = "docking_jobs", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> float:
        """Calculate docking success rate"""
        try:
            query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
            total = self.db_ops.count_documents(docking_collection, query)
            if total == 0:
                return 0
            
            success_query = query.copy()
            success_query['status'] = {'$in': ['completed', 'Completed', 'success', 'Success']}
            successful = self.db_ops.count_documents(docking_collection, success_query)
            
            return round((successful / total) * 100, 2)
        except Exception as e:
            logger.error(f"Error calculating docking success rate: {str(e)}")
            return 0
    
    def get_average_binding_energy(self, docking_collection: str = "docking_jobs", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> float:
        """Get average binding energy"""
        try:
            query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
            query['binding_energy'] = {'$exists': True}
            
            pipeline = [
                {'$match': query},
                {
                    '$group': {
                        '_id': None,
                        'avg_energy': {'$avg': '$binding_energy'}
                    }
                }
            ]
            results = self.db_ops.aggregate(docking_collection, pipeline)
            return round(results[0]['avg_energy'], 3) if results else 0
        except Exception as e:
            logger.error(f"Error getting average binding energy: {str(e)}")
            return 0
    
    def get_docking_trend(self, days: int = 30, docking_collection: str = "docking_jobs", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> List[Dict]:
        """Get docking trend over time"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=days)
            query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
            pipeline = [
                {'$match': query},
                {
                    '$group': {
                        '_id': {
                            '$dateToString': {
                                'format': '%Y-%m-%d',
                                'date': '$created_at'
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
            return self.db_ops.aggregate(docking_collection, pipeline)
        except Exception as e:
            logger.error(f"Error getting docking trend: {str(e)}")
            return []
    
    # ============ Optimization Metrics ============
    def get_optimization_runs(self, optimizations_collection: str = "optimizations", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> int:
        """Get total optimization runs"""
        query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
        return self.metrics.count_documents(optimizations_collection, query)
    
    def get_leads_generated(self, optimizations_collection: str = "optimizations", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> int:
        """Get count of leads generated (Completed runs count)"""
        try:
            query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
            query['status'] = {'$in': ['Completed', 'completed', 'success', 'Success']}
            return self.db_ops.count_documents(optimizations_collection, query)
        except Exception as e:
            logger.error(f"Error getting leads generated: {str(e)}")
            return 0
    
    def get_optimization_trend(self, days: int = 30, optimizations_collection: str = "optimizations", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> List[Dict]:
        """Get optimization trend over time"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=days)
            query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
            pipeline = [
                {'$match': query},
                {
                    '$group': {
                        '_id': {
                            '$dateToString': {
                                'format': '%Y-%m-%d',
                                'date': '$created_at'
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
            return self.db_ops.aggregate(optimizations_collection, pipeline)
        except Exception as e:
            logger.error(f"Error getting optimization trend: {str(e)}")
            return []
    
    # ============ ADMET Metrics ============
    def get_admet_runs(self, admet_collection: str = "admet_jobs", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> int:
        """Get total ADMET predictions"""
        query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
        return self.metrics.count_documents(admet_collection, query)
    
    def get_admet_success_rate(self, admet_collection: str = "admet_jobs", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> float:
        """Calculate ADMET success rate"""
        try:
            query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
            total = self.db_ops.count_documents(admet_collection, query)
            if total == 0:
                return 0
            
            success_query = query.copy()
            success_query['status'] = {'$in': ['Completed', 'completed', 'success', 'Success']}
            successful = self.db_ops.count_documents(admet_collection, success_query)
            
            return round((successful / total) * 100, 2)
        except Exception as e:
            logger.error(f"Error calculating ADMET success rate: {str(e)}")
            return 0
    
    def get_admet_trend(self, days: int = 30, admet_collection: str = "admet_jobs", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> List[Dict]:
        """Get ADMET trend over time"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=days)
            query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
            pipeline = [
                {'$match': query},
                {
                    '$group': {
                        '_id': {
                            '$dateToString': {
                                'format': '%Y-%m-%d',
                                'date': '$created_at'
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
            return self.db_ops.aggregate(admet_collection, pipeline)
        except Exception as e:
            logger.error(f"Error getting ADMET trend: {str(e)}")
            return []
    
    # ============ Pipeline Funnel ============
    def get_discovery_funnel(self, start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> List[Dict]:
        """Get discovery funnel metrics"""
        funnel_data = {
            'Targets': self.get_targets_loaded(start_date=start_date, end_date=end_date, user_email=user_email, target_id=target_id, status=status),
            'Screening': self.get_screening_runs(start_date=start_date, end_date=end_date, user_email=user_email, target_id=target_id, status=status),
            'Docking': self.get_docking_jobs(start_date=start_date, end_date=end_date, user_email=user_email, target_id=target_id, status=status),
            'Optimization': self.get_optimization_runs(start_date=start_date, end_date=end_date, user_email=user_email, target_id=target_id, status=status),
            'ADMET': self.get_admet_runs(start_date=start_date, end_date=end_date, user_email=user_email, target_id=target_id, status=status)
        }
        
        return self.metrics.get_funnel_metrics(funnel_data)
    
    # ============ Target Analysis ============
    def get_target_analysis_trend(self, days: int = 30, start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> List[Dict]:
        """Get target analysis trend"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=days)
            query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
            pipeline = [
                {'$match': query},
                {
                    '$group': {
                        '_id': {
                            '$dateToString': {
                                'format': '%Y-%m-%d',
                                'date': '$created_at'
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
            return self.db_ops.aggregate("targets", pipeline)
        except Exception as e:
            logger.error(f"Error target analysis trend: {str(e)}")
            return []
