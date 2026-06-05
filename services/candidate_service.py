"""
Candidate Service
Handles candidate intelligence metrics
"""

import logging
from typing import Dict, List
import pandas as pd
from utils.metrics import MetricsCalculator
from database.mongodb import MongoDBOperations

logger = logging.getLogger(__name__)


class CandidateService:
    """Service for candidate intelligence metrics"""
    
    def __init__(self):
        self.metrics = MetricsCalculator()
        self.db_ops = MongoDBOperations()
    
    def get_optimization_runs(self, optimizations_collection: str = "optimizations") -> int:
        """Get total optimization runs"""
        return self.metrics.count_documents(optimizations_collection)
    
    def get_leads_generated(self, optimizations_collection: str = "optimizations") -> int:
        """Get total leads generated"""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': None,
                        'total_leads': {'$sum': {'$cond': [{'$isNumber': '$leads_count'}, '$leads_count', 0]}}
                    }
                }
            ]
            results = self.db_ops.aggregate(optimizations_collection, pipeline)
            return results[0]['total_leads'] if results else 0
        except Exception as e:
            logger.error(f"Error getting leads generated: {str(e)}")
            return 0
    
    def get_best_candidate_score(self, optimizations_collection: str = "optimizations") -> float:
        """Get best candidate score"""
        try:
            pipeline = [
                {
                    '$match': {
                        'optimization_score': {'$exists': True}
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'max_score': {'$max': '$optimization_score'}
                    }
                }
            ]
            results = self.db_ops.aggregate(optimizations_collection, pipeline)
            return round(results[0]['max_score'], 2) if results else 0
        except Exception as e:
            logger.error(f"Error getting best candidate score: {str(e)}")
            return 0
    
    def get_admet_success_percentage(self, admet_collection: str = "admet_jobs") -> float:
        """Get ADMET success percentage"""
        try:
            total = self.db_ops.count_documents(admet_collection)
            if total == 0:
                return 0
            
            successful = self.db_ops.count_documents(
                admet_collection,
                {'status': 'success'}
            )
            
            return round((successful / total) * 100, 2)
        except Exception as e:
            logger.error(f"Error getting ADMET success percentage: {str(e)}")
            return 0
    
    def get_candidate_ranking(self, limit: int = 20, optimizations_collection: str = "optimizations") -> List[Dict]:
        """Get top candidates ranked by score"""
        try:
            pipeline = [
                {
                    '$match': {
                        'optimization_score': {'$exists': True}
                    }
                },
                {
                    '$sort': {'optimization_score': -1}
                },
                {
                    '$limit': limit
                },
                {
                    '$project': {
                        'candidate_id': 1,
                        'target_id': 1,
                        'optimization_score': 1,
                        'binding_energy': 1,
                        'status': 1
                    }
                }
            ]
            results = self.db_ops.aggregate(optimizations_collection, pipeline)
            return results
        except Exception as e:
            logger.error(f"Error getting candidate ranking: {str(e)}")
            return []
    
    def get_top_candidates(self, limit: int = 5, optimizations_collection: str = "optimizations") -> List[Dict]:
        """Get top candidates"""
        return self.get_candidate_ranking(limit=limit, optimizations_collection=optimizations_collection)
    
    def get_optimization_score_distribution(self, optimizations_collection: str = "optimizations") -> List[Dict]:
        """Get distribution of optimization scores"""
        try:
            pipeline = [
                {
                    '$match': {
                        'optimization_score': {'$exists': True}
                    }
                },
                {
                    '$bucket': {
                        'groupBy': '$optimization_score',
                        'boundaries': [0, 20, 40, 60, 80, 100],
                        'default': 'other',
                        'output': {
                            'count': {'$sum': 1}
                        }
                    }
                }
            ]
            results = self.db_ops.aggregate(optimizations_collection, pipeline)
            return [{'score_range': r['_id'], 'count': r['count']} for r in results]
        except Exception as e:
            logger.error(f"Error getting score distribution: {str(e)}")
            return []
    
    def get_admet_pass_rate(self, admet_collection: str = "admet_jobs") -> Dict:
        """Get ADMET pass rate by category"""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': '$admet_property',
                        'passed': {
                            '$sum': {'$cond': [{'$eq': ['$prediction', 'pass']}, 1, 0]}
                        },
                        'failed': {
                            '$sum': {'$cond': [{'$eq': ['$prediction', 'fail']}, 1, 0]}
                        },
                        'total': {'$sum': 1}
                    }
                },
                {
                    '$project': {
                        'property': '$_id',
                        'passed': 1,
                        'failed': 1,
                        'total': 1,
                        'pass_rate': {
                            '$cond': [
                                {'$eq': ['$total', 0]},
                                0,
                                {'$round': [{'$multiply': [{'$divide': ['$passed', '$total']}, 100]}, 2]}
                            ]
                        },
                        '_id': 0
                    }
                }
            ]
            return self.db_ops.aggregate(admet_collection, pipeline)
        except Exception as e:
            logger.error(f"Error getting ADMET pass rate: {str(e)}")
            return []
    
    def get_candidate_comparison(self, candidate_ids: List[str], optimizations_collection: str = "optimizations") -> List[Dict]:
        """Get comparison data for multiple candidates"""
        try:
            pipeline = [
                {
                    '$match': {
                        'candidate_id': {'$in': candidate_ids}
                    }
                },
                {
                    '$project': {
                        'candidate_id': 1,
                        'optimization_score': 1,
                        'binding_energy': 1,
                        'target_id': 1,
                        'status': 1
                    }
                }
            ]
            return self.db_ops.aggregate(optimizations_collection, pipeline)
        except Exception as e:
            logger.error(f"Error getting candidate comparison: {str(e)}")
            return []
    
    def get_candidate_by_target(self, target_id: str, optimizations_collection: str = "optimizations") -> List[Dict]:
        """Get candidates for a specific target"""
        try:
            pipeline = [
                {
                    '$match': {
                        'target_id': target_id,
                        'optimization_score': {'$exists': True}
                    }
                },
                {
                    '$sort': {'optimization_score': -1}
                },
                {
                    '$project': {
                        'candidate_id': 1,
                        'optimization_score': 1,
                        'binding_energy': 1,
                        'status': 1
                    }
                }
            ]
            return self.db_ops.aggregate(optimizations_collection, pipeline)
        except Exception as e:
            logger.error(f"Error getting candidates by target: {str(e)}")
            return []
    
    def calculate_candidate_quality_metrics(self, candidate_ids: List[str]) -> Dict:
        """Calculate quality metrics for candidates"""
        try:
            if not candidate_ids:
                return {}
            
            # Get optimization data
            opt_pipeline = [
                {
                    '$match': {
                        'candidate_id': {'$in': candidate_ids}
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'avg_score': {'$avg': '$optimization_score'},
                        'max_score': {'$max': '$optimization_score'},
                        'min_score': {'$min': '$optimization_score'}
                    }
                }
            ]
            
            opt_results = self.db_ops.aggregate("optimizations", opt_pipeline)
            
            if not opt_results:
                return {}
            
            return {
                'average_score': round(opt_results[0]['avg_score'], 2),
                'max_score': round(opt_results[0]['max_score'], 2),
                'min_score': round(opt_results[0]['min_score'], 2),
                'candidate_count': len(candidate_ids)
            }
        except Exception as e:
            logger.error(f"Error calculating quality metrics: {str(e)}")
            return {}
