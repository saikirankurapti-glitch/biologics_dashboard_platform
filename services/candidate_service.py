"""
Candidate Service
Handles candidate intelligence metrics from real database fields
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
    
    def get_optimization_runs(self, optimizations_collection: str = "optimizations", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> int:
        """Get total optimization runs"""
        query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
        return self.db_ops.count_documents(optimizations_collection, query)
    
    def get_leads_generated(self, optimizations_collection: str = "optimizations", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> int:
        """Get total leads generated (Completed optimization runs count)"""
        try:
            query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
            query['status'] = {'$in': ['Completed', 'completed', 'success', 'Success']}
            return self.db_ops.count_documents(optimizations_collection, query)
        except Exception as e:
            logger.error(f"Error getting leads generated: {str(e)}")
            return 0
    
    def get_best_candidate_score(self, optimizations_collection: str = "optimizations", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> float:
        """Get best candidate score derived from optimized_affinity"""
        try:
            query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
            docs = self.db_ops.find(optimizations_collection, query)
            max_score = 0.0
            for d in docs:
                results = d.get('results') or {}
                opt_aff = results.get('optimized_affinity')
                if opt_aff is not None:
                    score = min(100.0, abs(opt_aff) * 10)
                    if score > max_score:
                        max_score = score
            return round(max_score, 2)
        except Exception as e:
            logger.error(f"Error getting best candidate score: {str(e)}")
            return 0
    
    def get_admet_success_percentage(self, admet_collection: str = "admet_jobs", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> float:
        """Get ADMET success percentage"""
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
            logger.error(f"Error getting ADMET success percentage: {str(e)}")
            return 0
    
    def get_candidate_ranking(self, limit: int = 20, optimizations_collection: str = "optimizations", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> List[Dict]:
        """Get top candidates ranked by score"""
        try:
            query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
            docs = self.db_ops.find(optimizations_collection, query)
            candidates = []
            for d in docs:
                results = d.get('results') or {}
                opt_aff = results.get('optimized_affinity', 0)
                score = min(100.0, abs(opt_aff) * 10)
                
                candidates.append({
                    'candidate_id': f"CAN-{str(d['_id'])[-6:].upper()}",
                    'target_id': d.get('target_id', 'N/A'),
                    'optimization_score': score,
                    'binding_energy': opt_aff,
                    'status': d.get('status', 'Completed')
                })
            # Sort by score descending
            candidates.sort(key=lambda x: x['optimization_score'], reverse=True)
            return candidates[:limit]
        except Exception as e:
            logger.error(f"Error getting candidate ranking: {str(e)}")
            return []
    
    def get_top_candidates(self, limit: int = 5, optimizations_collection: str = "optimizations", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> List[Dict]:
        """Get top candidates"""
        return self.get_candidate_ranking(limit=limit, optimizations_collection=optimizations_collection, start_date=start_date, end_date=end_date, user_email=user_email, target_id=target_id, status=status)
    
    def get_optimization_score_distribution(self, optimizations_collection: str = "optimizations", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> List[Dict]:
        """Get distribution of optimization scores"""
        try:
            query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
            docs = self.db_ops.find(optimizations_collection, query)
            
            buckets = {
                '0-20': 0,
                '20-40': 0,
                '40-60': 0,
                '60-80': 0,
                '80-100': 0
            }
            
            for d in docs:
                results = d.get('results') or {}
                opt_aff = results.get('optimized_affinity', 0)
                score = min(100.0, abs(opt_aff) * 10)
                
                if 0 <= score < 20:
                    buckets['0-20'] += 1
                elif 20 <= score < 40:
                    buckets['20-40'] += 1
                elif 40 <= score < 60:
                    buckets['40-60'] += 1
                elif 60 <= score < 80:
                    buckets['60-80'] += 1
                elif 80 <= score <= 100:
                    buckets['80-100'] += 1
            
            return [{'score_range': k, 'count': v} for k, v in buckets.items()]
        except Exception as e:
            logger.error(f"Error getting score distribution: {str(e)}")
            return []
    
    def get_admet_pass_rate(self, admet_collection: str = "admet_jobs", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> List[Dict]:
        """Get ADMET pass rate by category from real database properties"""
        try:
            query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
            docs = self.db_ops.find(admet_collection, query)
            
            properties = {
                'Lipinski Rule': {'passed': 0, 'total': 0},
                'Veber Rule': {'passed': 0, 'total': 0},
                'Lead Likeness': {'passed': 0, 'total': 0},
                'BBB Permeability': {'passed': 0, 'total': 0},
                'HERG Toxicity': {'passed': 0, 'total': 0},
                'Hepatotoxicity': {'passed': 0, 'total': 0}
            }
            
            for d in docs:
                results = d.get('results') or {}
                
                # Drug likeness
                dl = results.get('drug_likeness') or {}
                if 'Lipinski_Pass' in dl:
                    properties['Lipinski Rule']['total'] += 1
                    if dl['Lipinski_Pass']:
                        properties['Lipinski Rule']['passed'] += 1
                if 'Veber_Pass' in dl:
                    properties['Veber Rule']['total'] += 1
                    if dl['Veber_Pass']:
                        properties['Veber Rule']['passed'] += 1
                if 'Lead_Likeness' in dl:
                    properties['Lead Likeness']['total'] += 1
                    if dl['Lead_Likeness']:
                        properties['Lead Likeness']['passed'] += 1
                
                # ADMET metrics
                am = results.get('admet_metrics') or {}
                if 'BBB_Permeability' in am:
                    properties['BBB Permeability']['total'] += 1
                    if am['BBB_Permeability'] in ['High', 'Moderate']:
                        properties['BBB Permeability']['passed'] += 1
                if 'HERG_Toxicity' in am:
                    properties['HERG Toxicity']['total'] += 1
                    if am['HERG_Toxicity'] == 'Safe':
                        properties['HERG Toxicity']['passed'] += 1
                if 'Hepatotoxicity' in am:
                    properties['Hepatotoxicity']['total'] += 1
                    if am['Hepatotoxicity'] in ['Low Risk', 'Moderate Risk']:
                        properties['Hepatotoxicity']['passed'] += 1
            
            results_list = []
            for prop_name, data in properties.items():
                total = data['total']
                passed = data['passed']
                failed = total - passed
                pass_rate = round((passed / total) * 100, 2) if total > 0 else 0.0
                results_list.append({
                    'property': prop_name,
                    'passed': passed,
                    'failed': failed,
                    'total': total,
                    'pass_rate': pass_rate
                })
            
            return results_list
        except Exception as e:
            logger.error(f"Error getting ADMET pass rate: {str(e)}")
            return []
    
    def get_candidate_comparison(self, candidate_ids: List[str], optimizations_collection: str = "optimizations", start_date=None, end_date=None, user_email=None, target_id=None, status=None) -> List[Dict]:
        """Get comparison data for multiple candidates"""
        try:
            query = self._build_query('created_at', start_date, end_date, user_email, target_id, status)
            docs = self.db_ops.find(optimizations_collection, query)
            matched = []
            for d in docs:
                cid = f"CAN-{str(d['_id'])[-6:].upper()}"
                if cid in candidate_ids:
                    results = d.get('results') or {}
                    opt_aff = results.get('optimized_affinity', 0)
                    matched.append({
                        'candidate_id': cid,
                        'optimization_score': min(100.0, abs(opt_aff) * 10),
                        'binding_energy': opt_aff,
                        'target_id': d.get('target_id', 'N/A'),
                        'status': d.get('status', 'Completed')
                    })
            return matched
        except Exception as e:
            logger.error(f"Error getting candidate comparison: {str(e)}")
            return []
    
    def get_candidate_by_target(self, target_id: str, optimizations_collection: str = "optimizations") -> List[Dict]:
        """Get candidates for a specific target"""
        try:
            query = {'target_id': target_id}
            docs = self.db_ops.find(optimizations_collection, query)
            candidates = []
            for d in docs:
                results = d.get('results') or {}
                opt_aff = results.get('optimized_affinity', 0)
                candidates.append({
                    'candidate_id': f"CAN-{str(d['_id'])[-6:].upper()}",
                    'optimization_score': min(100.0, abs(opt_aff) * 10),
                    'binding_energy': opt_aff,
                    'status': d.get('status', 'Completed')
                })
            candidates.sort(key=lambda x: x['optimization_score'], reverse=True)
            return candidates
        except Exception as e:
            logger.error(f"Error getting candidates by target: {str(e)}")
            return []
    
    def calculate_candidate_quality_metrics(self, candidate_ids: List[str]) -> Dict:
        """Calculate quality metrics for candidates"""
        try:
            if not candidate_ids:
                return {}
            
            docs = self.db_ops.find("optimizations")
            scores = []
            for d in docs:
                cid = f"CAN-{str(d['_id'])[-6:].upper()}"
                if cid in candidate_ids:
                    results = d.get('results') or {}
                    opt_aff = results.get('optimized_affinity', 0)
                    scores.append(min(100.0, abs(opt_aff) * 10))
            
            if not scores:
                return {}
            
            return {
                'average_score': round(sum(scores) / len(scores), 2),
                'max_score': round(max(scores), 2),
                'min_score': round(min(scores), 2),
                'candidate_count': len(scores)
            }
        except Exception as e:
            logger.error(f"Error calculating quality metrics: {str(e)}")
            return {}
