from flask import Blueprint, request, jsonify
from database.models import db, User, BrowserActivity, DailySession
import uuid
from datetime import datetime, timedelta
import logging
from urllib.parse import urlparse

tracking_bp = Blueprint('tracking', __name__)
logger = logging.getLogger(__name__)

@tracking_bp.route('/api/track/activity', methods=['POST'])
def track_activity():
    """Track browser activities"""
    try:
        data = request.json
        
        if not data or 'activity_type' not in data:
            return jsonify({"error": "Activity type is required"}), 400
        
        user_id = data.get('user_id', str(uuid.uuid4()))
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        # Create or get user
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            user = User(user_id=user_id, session_id=session_id)
            db.session.add(user)
        
        # Extract domain from URL
        url = data.get('url', '')
        domain = ''
        if url:
            try:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc
            except:
                pass
        
        # Create activity record
        activity = BrowserActivity(
            user_id=user_id,
            session_id=session_id,
            url=url,
            domain=domain,
            page_title=data.get('page_title', ''),
            activity_type=data['activity_type'],
            element_details=data.get('element_details', {}),
            duration_seconds=data.get('duration_seconds', 0)
        )
        
        db.session.add(activity)
        
        # Update daily session
        daily_session = DailySession.query.filter_by(session_id=session_id).first()
        if daily_session:
            if data['activity_type'] == 'page_visit':
                daily_session.total_pages_visited += 1
            daily_session.total_interactions += 1
            daily_session.end_time = datetime.utcnow()
        else:
            daily_session = DailySession(
                session_id=session_id,
                user_id=user_id,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                total_pages_visited=1 if data['activity_type'] == 'page_visit' else 0,
                total_interactions=1
            )
            db.session.add(daily_session)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "activity_id": activity.activity_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Tracking error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@tracking_bp.route('/api/track/summary/<user_id>', methods=['GET'])
def get_daily_summary(user_id):
    """Get daily summary for a user"""
    try:
        date_str = request.args.get('date')
        if date_str:
            target_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            target_date = datetime.utcnow()
        
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        # Get activities for the day
        activities = BrowserActivity.query.filter(
            BrowserActivity.user_id == user_id,
            BrowserActivity.timestamp >= start_of_day,
            BrowserActivity.timestamp < end_of_day
        ).all()
        
        # Get daily session
        daily_session = DailySession.query.filter_by(user_id=user_id).first()
        
        # Calculate statistics
        domains_visited = {}
        activity_types_count = {}
        
        for activity in activities:
            # Count domains
            if activity.domain:
                domains_visited[activity.domain] = domains_visited.get(activity.domain, 0) + 1
            
            # Count activity types
            activity_types_count[activity.activity_type] = activity_types_count.get(activity.activity_type, 0) + 1
        
        summary = {
            "date": target_date.date().isoformat(),
            "total_pages": sum(1 for a in activities if a.activity_type == 'page_visit'),
            "total_interactions": len(activities),
            "unique_domains": len(domains_visited),
            "domains_visited": domains_visited,
            "activity_breakdown": activity_types_count,
            "daily_session": {
                "start_time": daily_session.start_time.isoformat() if daily_session else None,
                "end_time": daily_session.end_time.isoformat() if daily_session else None,
                "chat_messages": daily_session.chat_messages_count if daily_session else 0
            } if daily_session else None
        }
        
        return jsonify({
            "success": True,
            "summary": summary
        })
        
    except Exception as e:
        logger.error(f"Summary error: {str(e)}")
        return jsonify({"error": str(e)}), 500