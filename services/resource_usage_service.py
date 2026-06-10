"""
Resource Usage & Engagement Service
Handles database logging of navigation/actions and builds aggregation metrics.
"""

import logging
import uuid
import random
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from database.mongodb import MongoDBOperations

logger = logging.getLogger(__name__)


class ResourceUsageService:
    """Service for resource usage tracking and analytics queries"""
    
    def __init__(self):
        self.db_ops = MongoDBOperations()
        self.seed_initial_data()
        
    def seed_initial_data(self):
        """Seed the resource_usage collection with mock data if it is empty"""
        try:
            count = self.db_ops.count_documents("resource_usage")
            if count > 0:
                logger.info("resource_usage collection already contains data.")
                return
        except Exception:
            # Collection might not exist or connection failed, we will attempt to seed
            pass
            
        logger.info("resource_usage collection is empty. Seeding mock usage data...")
        
        # Determine users
        users_list = []
        try:
            db_users = self.db_ops.find("users")
            users_list = [u.get("email") for u in db_users if u.get("email")]
        except Exception as e:
            logger.warning(f"Could not load users for seeding: {e}")
            
        if not users_list:
            users_list = [
                "saikirankurapti@gmail.com",
                "sarah.chen@biotech.org",
                "james.wilson@pharma-corp.net",
                "elena.rostova@discovery-labs.com",
                "marcus.vance@therapeutics.io"
            ]
            
        modules = [
            "Target Explorer",
            "AI Screening",
            "Molecular Docking",
            "Lead Optimization",
            "ADMET Prediction",
            "Preformulation Analysis",
            "Formulation Design",
            "Experiments",
            "Report Generation",
            "Executive Dashboard",
            "User Analytics"
        ]
        
        resources = {
            "Target Explorer": ["T-1002 (Oncology)", "T-3042 (Immunology)", "T-4091 (Neurology)", "T-1102 (Cardio)"],
            "AI Screening": ["Virtual Screen Run #12", "Virtual Screen Run #13", "High-Throughput Model v4.1"],
            "Molecular Docking": ["Autodock Vina: Target-A", "Glide Docking: Spike Protein", "ColabFold Structure #3"],
            "Lead Optimization": ["SMILES Generative Run #5", "R-group Scaffold Search", "Binding Affinity Optimization"],
            "ADMET Prediction": ["Aqueous Solubility Predictor", "hERG Toxicity Run", "BBB Permeability Analysis"],
            "Preformulation Analysis": ["Preformulation Report PDF", "Solubility Curve Graph", "pKa/LogP Profiler"],
            "Formulation Design": ["Excipient Compatibility Matrix", "Liquid Dosage Design", "Solid Dispersion Model"],
            "Experiments": ["Exp-843: Cell Assay", "Exp-844: PCR Run", "Exp-845: Western Blot"],
            "Report Generation": ["Executive Monthly Report", "Candidate Brief PDF", "Pipeline Export CSV"],
            "Executive Dashboard": ["Command Center Main View", "KPI Export Module"],
            "User Analytics": ["User Analytics Summary", "Departmental Metrics Graph"]
        }
        
        browsers = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        ips = ["192.168.1.45", "10.0.2.15", "172.16.5.120", "192.168.10.88", "10.200.12.3", "184.22.109.5"]
        
        now = datetime.now()
        records = []
        
        # We generate ~40 sessions spanning the last 30 days
        for i in range(40):
            session_id = str(uuid.uuid4())
            user = random.choice(users_list)
            browser = random.choice(browsers)
            ip = random.choice(ips)
            
            # Distribute sessions across the last 30 days
            session_date = now - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Each session visits between 3 and 8 pages/modules sequentially
            num_actions = random.randint(3, 8)
            action_time = session_date
            
            for _ in range(num_actions):
                module = random.choice(modules)
                resource = random.choice(resources[module])
                duration = round(random.uniform(0.5, 30.0), 2)
                
                access_time = action_time
                exit_time = access_time + timedelta(minutes=duration)
                
                # Next action in the session occurs shortly after
                action_time = exit_time + timedelta(seconds=random.randint(10, 120))
                
                records.append({
                    "user_email": user,
                    "module_name": module,
                    "resource_name": resource,
                    "access_time": access_time,
                    "exit_time": exit_time,
                    "duration_minutes": duration,
                    "session_id": session_id,
                    "browser": browser,
                    "ip_address": ip
                })
                
        try:
            col = self.db_ops.connection.get_collection("resource_usage")
            col.insert_many(records)
            logger.info(f"Successfully seeded {len(records)} resource usage records.")
        except Exception as e:
            logger.error(f"Failed to write seed records into resource_usage: {e}")

    def track_page_navigation(self, page_name: str):
        """
        Calculates time spent on current page and registers exit/access events
        Called from the main page script.
        """
        # Ensure session id exists
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
            
        # Ensure current user email is set
        if 'current_user_email' not in st.session_state:
            st.session_state.current_user_email = "saikirankurapti@gmail.com"
            
        # Track initial entry
        if 'tracked_page' not in st.session_state:
            st.session_state.tracked_page = page_name
            st.session_state.tracked_page_entry = datetime.now()
            return
            
        # If the page changed, compute elapsed time and log exit of previous page
        if st.session_state.tracked_page != page_name:
            entry_time = st.session_state.tracked_page_entry
            exit_time = datetime.now()
            duration_minutes = (exit_time - entry_time).total_seconds() / 60.0
            
            # Clip outlier or negative values
            if duration_minutes < 0:
                duration_minutes = 0.1
            elif duration_minutes > 120:
                duration_minutes = 120.0
                
            browser = "Chrome/120.0"
            ip_address = "127.0.0.1"
            
            try:
                if hasattr(st, "context") and hasattr(st.context, "headers"):
                    headers = st.context.headers
                else:
                    from streamlit.web.server.websocket_headers import _get_websocket_headers
                    headers = _get_websocket_headers()
                if headers:
                    user_agent = headers.get("User-Agent") or headers.get("user-agent")
                    if user_agent:
                        browser = user_agent
                    
                    forwarded_for = headers.get("X-Forwarded-For") or headers.get("x-forwarded-for")
                    if forwarded_for:
                        ip_address = forwarded_for.split(",")[0]
            except Exception:
                pass
                
            doc = {
                "user_email": st.session_state.current_user_email,
                "module_name": st.session_state.tracked_page,
                "resource_name": f"{st.session_state.tracked_page} View",
                "access_time": entry_time,
                "exit_time": exit_time,
                "duration_minutes": round(duration_minutes, 2),
                "session_id": st.session_state.session_id,
                "browser": browser,
                "ip_address": ip_address
            }
            
            try:
                self.db_ops.insert_one("resource_usage", doc)
            except Exception as e:
                logger.error(f"Error logging page navigation: {e}")
                
            st.session_state.tracked_page = page_name
            st.session_state.tracked_page_entry = datetime.now()

    def track_resource_access(self, module_name: str, resource_name: str):
        """Logs access to a specific resource (e.g. looking at a candidate profile)"""
        # Generate a tracking document immediately
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
            
        if 'current_user_email' not in st.session_state:
            st.session_state.current_user_email = "saikirankurapti@gmail.com"
            
        browser = "Chrome/120.0"
        ip_address = "127.0.0.1"
        try:
            if hasattr(st, "context") and hasattr(st.context, "headers"):
                headers = st.context.headers
            else:
                from streamlit.web.server.websocket_headers import _get_websocket_headers
                headers = _get_websocket_headers()
            if headers:
                user_agent = headers.get("User-Agent") or headers.get("user-agent")
                if user_agent:
                    browser = user_agent
                
                forwarded_for = headers.get("X-Forwarded-For") or headers.get("x-forwarded-for")
                if forwarded_for:
                    ip_address = forwarded_for.split(",")[0]
        except Exception:
            pass
            
        access_time = datetime.now()
        # Immediate actions have small nominal duration (e.g. 0.5 mins)
        doc = {
            "user_email": st.session_state.current_user_email,
            "module_name": module_name,
            "resource_name": resource_name,
            "access_time": access_time,
            "exit_time": access_time + timedelta(seconds=30),
            "duration_minutes": 0.5,
            "session_id": st.session_state.session_id,
            "browser": browser,
            "ip_address": ip_address
        }
        
        try:
            self.db_ops.insert_one("resource_usage", doc)
        except Exception as e:
            logger.error(f"Error logging resource action: {e}")

    def _build_query(self, start_date=None, end_date=None, user_email=None) -> Dict:
        query = {}
        date_query = {}
        if start_date:
            date_query['$gte'] = start_date
        if end_date:
            date_query['$lte'] = end_date
        if date_query:
            query['access_time'] = date_query
        if user_email:
            query['user_email'] = user_email
        return query

    def get_kpis(self, start_date=None, end_date=None, user_email=None) -> Dict[str, Any]:
        """Fetch general resource usage KPIs"""
        query = self._build_query(start_date, end_date, user_email)
        
        # 1. Total Active Users
        pipeline_users = [
            {'$match': query},
            {'$group': {'_id': '$user_email'}},
            {'$count': 'count'}
        ]
        res_users = self.db_ops.aggregate("resource_usage", pipeline_users)
        active_users = res_users[0]['count'] if res_users else 0
        
        # 2. Total Sessions
        pipeline_sessions = [
            {'$match': query},
            {'$group': {'_id': '$session_id'}},
            {'$count': 'count'}
        ]
        res_sessions = self.db_ops.aggregate("resource_usage", pipeline_sessions)
        sessions = res_sessions[0]['count'] if res_sessions else 0
        
        # 3. Time spent metrics & Avg session duration
        pipeline_time = [
            {'$match': query},
            {
                '$group': {
                    '_id': None,
                    'total_duration': {'$sum': '$duration_minutes'},
                    'avg_duration': {'$avg': '$duration_minutes'}
                }
            }
        ]
        res_time = self.db_ops.aggregate("resource_usage", pipeline_time)
        total_time = res_time[0]['total_duration'] if res_time else 0.0
        avg_duration = res_time[0]['avg_duration'] if res_time else 0.0
        
        # 4. Most & Least Used Module
        pipeline_modules = [
            {'$match': query},
            {'$group': {'_id': '$module_name', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        res_modules = self.db_ops.aggregate("resource_usage", pipeline_modules)
        
        most_used = res_modules[0]['_id'] if res_modules else "N/A"
        least_used = res_modules[-1]['_id'] if len(res_modules) > 1 else ("N/A" if not res_modules else res_modules[0]['_id'])
        
        # 5. Reports generated (from report_registry)
        report_query = {}
        if start_date and end_date:
            report_query['created_at'] = {'$gte': start_date, '$lte': end_date}
        if user_email:
            report_query['created_by'] = user_email
        reports = self.db_ops.count_documents("report_registry", report_query)
        
        # 6. Experiments executed (from experiments)
        exp_query = {}
        if start_date and end_date:
            exp_query['created_at'] = {'$gte': start_date, '$lte': end_date}
        if user_email:
            exp_query['created_by'] = user_email
        experiments = self.db_ops.count_documents("experiments", exp_query)
        
        return {
            "active_users": active_users,
            "sessions": sessions,
            "avg_duration": round(avg_duration, 2),
            "most_used": most_used,
            "least_used": least_used,
            "total_time": round(total_time, 2),
            "reports": reports,
            "experiments": experiments
        }

    def get_module_usage_metrics(self, start_date=None, end_date=None, user_email=None) -> List[Dict]:
        """Get visit count, unique users, and time spent per module"""
        query = self._build_query(start_date, end_date, user_email)
        pipeline = [
            {'$match': query},
            {
                '$group': {
                    '_id': '$module_name',
                    'views': {'$sum': 1},
                    'unique_users': {'$addToSet': '$user_email'},
                    'time_spent': {'$sum': '$duration_minutes'}
                }
            },
            {
                '$project': {
                    'module': '$_id',
                    'views': 1,
                    'unique_users_count': {'$size': '$unique_users'},
                    'time_spent': {'$round': ['$time_spent', 2]},
                    '_id': 0
                }
            },
            {'$sort': {'views': -1}}
        ]
        return self.db_ops.aggregate("resource_usage", pipeline)

    def get_user_activity_analysis(self, start_date=None, end_date=None, user_email=None) -> List[Dict]:
        """Aggregate activities grouped by user"""
        query = self._build_query(start_date, end_date, user_email)
        pipeline = [
            {'$match': query},
            {
                '$group': {
                    '_id': '$user_email',
                    'sessions': {'$addToSet': '$session_id'},
                    'views': {'$sum': 1},
                    'total_time': {'$sum': '$duration_minutes'}
                }
            },
            {
                '$project': {
                    'user_email': '$_id',
                    'sessions_count': {'$size': '$sessions'},
                    'views': 1,
                    'total_time': {'$round': ['$total_time', 2]},
                    '_id': 0
                }
            },
            {'$sort': {'views': -1}}
        ]
        return self.db_ops.aggregate("resource_usage", pipeline)

    def get_user_drilldown(self, user_email: str) -> Dict[str, Any]:
        """Get activity overview for a single user"""
        if not user_email:
            return {}
            
        query = {'user_email': user_email}
        
        # Modules accessed
        pipeline_modules = [
            {'$match': query},
            {
                '$group': {
                    '_id': '$module_name',
                    'views': {'$sum': 1},
                    'total_time': {'$sum': '$duration_minutes'},
                    'last_access': {'$max': '$access_time'}
                }
            },
            {
                '$project': {
                    'module': '$_id',
                    'views': 1,
                    'total_time': {'$round': ['$total_time', 2]},
                    'last_access': 1,
                    '_id': 0
                }
            },
            {'$sort': {'views': -1}}
        ]
        modules_accessed = self.db_ops.aggregate("resource_usage", pipeline_modules)
        
        # Resources used
        pipeline_resources = [
            {'$match': query},
            {
                '$group': {
                    '_id': '$resource_name',
                    'views': {'$sum': 1},
                    'last_access': {'$max': '$access_time'}
                }
            },
            {
                '$project': {
                    'resource': '$_id',
                    'views': 1,
                    'last_access': 1,
                    '_id': 0
                }
            },
            {'$sort': {'views': -1}},
            {'$limit': 15}
        ]
        resources_used = self.db_ops.aggregate("resource_usage", pipeline_resources)
        
        # General summary
        pipeline_summary = [
            {'$match': query},
            {
                '$group': {
                    '_id': None,
                    'total_time': {'$sum': '$duration_minutes'},
                    'last_active': {'$max': '$access_time'}
                }
            }
        ]
        res_summary = self.db_ops.aggregate("resource_usage", pipeline_summary)
        
        total_time = res_summary[0]['total_time'] if res_summary else 0.0
        last_active = res_summary[0]['last_active'] if res_summary else None
        
        return {
            "modules": modules_accessed,
            "resources": resources_used,
            "total_time": round(total_time, 2),
            "last_active": last_active
        }

    def get_resource_drilldown(self, resource_name: str) -> Dict[str, Any]:
        """Get statistics for a specific resource"""
        if not resource_name:
            return {}
            
        query = {'resource_name': resource_name}
        
        # Users accessing
        pipeline_users = [
            {'$match': query},
            {
                '$group': {
                    '_id': '$user_email',
                    'views': {'$sum': 1},
                    'total_time': {'$sum': '$duration_minutes'},
                    'last_access': {'$max': '$access_time'}
                }
            },
            {
                '$project': {
                    'user': '$_id',
                    'views': 1,
                    'total_time': {'$round': ['$total_time', 2]},
                    'last_access': 1,
                    '_id': 0
                }
            },
            {'$sort': {'views': -1}}
        ]
        users = self.db_ops.aggregate("resource_usage", pipeline_users)
        
        # General Summary
        pipeline_summary = [
            {'$match': query},
            {
                '$group': {
                    '_id': None,
                    'total_views': {'$sum': 1},
                    'avg_duration': {'$avg': '$duration_minutes'}
                }
            }
        ]
        res_summary = self.db_ops.aggregate("resource_usage", pipeline_summary)
        
        total_views = res_summary[0]['total_views'] if res_summary else 0
        avg_duration = res_summary[0]['avg_duration'] if res_summary else 0.0
        
        return {
            "users": users,
            "total_views": total_views,
            "avg_duration": round(avg_duration, 2)
        }

    def get_usage_trends(self, frequency: str = "daily", start_date=None, end_date=None, user_email=None) -> List[Dict]:
        """Aggregate trends by daily, weekly, or monthly intervals"""
        query = self._build_query(start_date, end_date, user_email)
        
        if frequency == "weekly":
            date_format = "%Y-W%V"
        elif frequency == "monthly":
            date_format = "%Y-%m"
        else:  # default to daily
            date_format = "%Y-%m-%d"
            
        pipeline = [
            {'$match': query},
            {
                '$group': {
                    '_id': {
                        '$dateToString': {
                            'format': date_format,
                            'date': '$access_time'
                        }
                    },
                    'views': {'$sum': 1},
                    'time_spent': {'$sum': '$duration_minutes'}
                }
            },
            {
                '$project': {
                    'period': '$_id',
                    'views': 1,
                    'time_spent': {'$round': ['$time_spent', 2]},
                    '_id': 0
                }
            },
            {'$sort': {'period': 1}}
        ]
        return self.db_ops.aggregate("resource_usage", pipeline)

    def get_heatmap_data(self, start_date=None, end_date=None, user_email=None) -> pd.DataFrame:
        """Create a matrix representing activities by Day of Week and Hour of Day"""
        query = self._build_query(start_date, end_date, user_email)
        pipeline = [
            {'$match': query},
            {
                '$group': {
                    '_id': {
                        'day_of_week': {'$dayOfWeek': '$access_time'},
                        'hour': {'$hour': '$access_time'}
                    },
                    'count': {'$sum': 1}
                }
            }
        ]
        
        results = self.db_ops.aggregate("resource_usage", pipeline)
        
        # Pivot values
        heatmap_dict = {}
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        
        for result in results:
            day_idx = result['_id']['day_of_week']
            if day_idx is None or day_idx < 1 or day_idx > 7:
                continue
            day = day_names[day_idx - 1]
            hour = result['_id']['hour']
            if day not in heatmap_dict:
                heatmap_dict[day] = {}
            heatmap_dict[day][hour] = result['count']
            
        # Re-index standard 24 hours
        df = pd.DataFrame(heatmap_dict).reindex(range(24)).fillna(0)
        # Reorder columns to standard Monday-Sunday format
        sorted_cols = [d for d in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'] if d in df.columns]
        df = df[sorted_cols]
        
        return df
