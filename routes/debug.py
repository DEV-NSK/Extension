from flask import Blueprint, jsonify
from database.models import db, BrowserActivity, DailySession, User
from datetime import datetime
import logging

debug_bp = Blueprint('debug', __name__)
logger = logging.getLogger(__name__)

@debug_bp.route('/api/debug/db-status', methods=['GET'])
def db_status():
    """Check database status and data"""
    try:
        # Count total records
        total_users = User.query.count()
        total_activities = BrowserActivity.query.count()
        total_sessions = DailySession.query.count()
        
        # Get latest activities
        latest_activities = BrowserActivity.query.order_by(
            BrowserActivity.timestamp.desc()
        ).limit(5).all()
        
        activities_list = []
        for activity in latest_activities:
            activities_list.append({
                "id": activity.activity_id,
                "user_id": activity.user_id,
                "type": activity.activity_type,
                "url": activity.url[:50] if activity.url else "",
                "timestamp": activity.timestamp.isoformat() if activity.timestamp else None
            })
        
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        return jsonify({
            "success": True,
            "database_status": "connected",
            "tables": tables,
            "counts": {
                "users": total_users,
                "activities": total_activities,
                "sessions": total_sessions
            },
            "latest_activities": activities_list,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Database status error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "database_status": "error"
        }), 500

@debug_bp.route('/api/debug/user-data/<user_id>', methods=['GET'])
def user_data(user_id):
    """Get all data for a specific user"""
    try:
        # Get user
        user = User.query.filter_by(user_id=user_id).first()
        
        if not user:
            return jsonify({
                "success": False,
                "error": f"User {user_id} not found",
                "user_exists": False
            })
        
        # Get all activities for user
        all_activities = BrowserActivity.query.filter_by(
            user_id=user_id
        ).order_by(BrowserActivity.timestamp.desc()).all()
        
        # Get all sessions for user
        all_sessions = DailySession.query.filter_by(
            user_id=user_id
        ).order_by(DailySession.start_time.desc()).all()
        
        activities_list = []
        for activity in all_activities[:50]:  # Limit to 50 for response
            activities_list.append({
                "activity_id": activity.activity_id,
                "activity_type": activity.activity_type,
                "url": activity.url,
                "page_title": activity.page_title,
                "timestamp": activity.timestamp.isoformat() if activity.timestamp else None,
                "duration_seconds": activity.duration_seconds
            })
        
        sessions_list = []
        for session in all_sessions:
            sessions_list.append({
                "session_id": session.session_id,
                "start_time": session.start_time.isoformat() if session.start_time else None,
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "total_pages_visited": session.total_pages_visited,
                "total_interactions": session.total_interactions
            })
        
        return jsonify({
            "success": True,
            "user": {
                "user_id": user.user_id,
                "session_id": user.session_id,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_active": user.last_active.isoformat() if user.last_active else None
            },
            "activities_count": len(all_activities),
            "sessions_count": len(all_sessions),
            "activities": activities_list,
            "sessions": sessions_list
        })
        
    except Exception as e:
        logger.error(f"User data error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500