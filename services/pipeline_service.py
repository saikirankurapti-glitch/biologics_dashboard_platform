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
    
    # ============ Target Metrics ============
    def get_targets_loaded(self, targets_collection: str = "targets") -> int:
        """Get total targets loaded"""
        return self.metrics.count_documents(targets_collection)
    
    def get_unique_proteins(self, targets_collection: str = "targets") -> int:
        """Get count of unique proteins (estimate based on targets)"""
        try:
            pipeline = [
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
    def get_screening_runs(self, screenings_collection: str = "screenings") -> int:
        """Get total screening runs"""
        return self.metrics.count_documents(screenings_collection)
    
    def get_molecules_screened(self, screenings_collection: str = "screenings") -> int:
        """Get total molecules screened"""
        try:
            pipeline = [
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
    
    def get_hits_identified(self, screenings_collection: str = "screenings") -> int:
        """Get total hits identified"""
        try:
            pipeline = [
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
    
    def get_hit_rate(self, screenings_collection: str = "screenings") -> float:
        """Calculate hit rate percentage"""
        try:
            molecules = self.get_molecules_screened(screenings_collection)
            hits = self.get_hits_identified(screenings_collection)
            
            if molecules == 0:
                return 0
            
            return round((hits / molecules) * 100, 2)
        except Exception as e:
            logger.error(f"Error calculating hit rate: {str(e)}")
            return 0
    
    def get_screening_trend(self, days: int = 30, screenings_collection: str = "screenings") -> List[Dict]:
        """Get screening trend over time"""
        return self.metrics.get_collection_trend(screenings_collection, 'created_at', days)
    
    # ============ Docking Metrics ============
    def get_docking_jobs(self, docking_collection: str = "docking_jobs") -> int:
        """Get total docking jobs"""
        return self.metrics.count_documents(docking_collection)
    
    def get_docking_success_rate(self, docking_collection: str = "docking_jobs") -> float:
        """Calculate docking success rate"""
        try:
            total = self.db_ops.count_documents(docking_collection)
            if total == 0:
                return 0
            
            successful = self.db_ops.count_documents(
                docking_collection,
                {'status': 'completed'}
            )
            
            return round((successful / total) * 100, 2)
        except Exception as e:
            logger.error(f"Error calculating docking success rate: {str(e)}")
            return 0
    
    def get_average_binding_energy(self, docking_collection: str = "docking_jobs") -> float:
        """Get average binding energy"""
        try:
            pipeline = [
                {
                    '$match': {
                        'binding_energy': {'$exists': True}
                    }
                },
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
    
    def get_docking_trend(self, days: int = 30, docking_collection: str = "docking_jobs") -> List[Dict]:
        """Get docking trend over time"""
        return self.metrics.get_collection_trend(docking_collection, 'created_at', days)
    
    # ============ Optimization Metrics ============
    def get_optimization_runs(self, optimizations_collection: str = "optimizations") -> int:
        """Get total optimization runs"""
        return self.metrics.count_documents(optimizations_collection)
    
    def get_leads_generated(self, optimizations_collection: str = "optimizations") -> int:
        """Get count of leads generated"""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': None,
                        'leads': {'$sum': {'$cond': [{'$isNumber': '$leads_count'}, '$leads_count', 0]}}
                    }
                }
            ]
            results = self.db_ops.aggregate(optimizations_collection, pipeline)
            return results[0]['leads'] if results else 0
        except Exception as e:
            logger.error(f"Error getting leads generated: {str(e)}")
            return 0
    
    def get_optimization_trend(self, days: int = 30, optimizations_collection: str = "optimizations") -> List[Dict]:
        """Get optimization trend over time"""
        return self.metrics.get_collection_trend(optimizations_collection, 'created_at', days)
    
    # ============ ADMET Metrics ============
    def get_admet_runs(self, admet_collection: str = "admet_jobs") -> int:
        """Get total ADMET predictions"""
        return self.metrics.count_documents(admet_collection)
    
    def get_admet_success_rate(self, admet_collection: str = "admet_jobs") -> float:
        """Calculate ADMET success rate"""
        try:
            total = self.db_ops.count_documents(admet_collection)
            if total == 0:
                return 0
            
            successful = self.db_ops.count_documents(
                admet_collection,
                {'status': 'completed'}
            )
            
            return round((successful / total) * 100, 2)
        except Exception as e:
            logger.error(f"Error calculating ADMET success rate: {str(e)}")
            return 0
    
    def get_admet_trend(self, days: int = 30, admet_collection: str = "admet_jobs") -> List[Dict]:
        """Get ADMET trend over time"""
        return self.metrics.get_collection_trend(admet_collection, 'created_at', days)
    
    # ============ Pipeline Funnel ============
    def get_discovery_funnel(self) -> List[Dict]:
        """Get discovery funnel metrics"""
        funnel_data = {
            'Targets': self.get_targets_loaded(),
            'Screening': self.get_screening_runs(),
            'Docking': self.get_docking_jobs(),
            'Optimization': self.get_optimization_runs(),
            'ADMET': self.get_admet_runs()
        }
        
        return self.metrics.get_funnel_metrics(funnel_data)
    
    # ============ Target Analysis ============
    def get_target_analysis_trend(self, days: int = 30) -> List[Dict]:
        """Get target analysis trend"""
        return self.metrics.get_collection_trend("targets", 'created_at', days)
