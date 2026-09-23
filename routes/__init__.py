from functools import wraps
from flask import session, redirect, url_for, flash
from models import db, User

def get_current_user():
    """Retrieve currently logged in User from DB."""
    user_id = session.get('user_id')
    if user_id:
        return db.session.get(User, user_id)
    return None

def login_required(f):
    """Decorator to enforce authenticated session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """Decorator to enforce role-based access control (RBAC)."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            user_role = session.get('user_role')
            if user_role not in allowed_roles and user_role != 'admin':
                flash('You do not have permission to access this resource.', 'danger')
                # Redirect to appropriate dashboard based on user's actual role
                if user_role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif user_role == 'trainer':
                    return redirect(url_for('trainer.dashboard'))
                elif user_role == 'nutritionist':
                    return redirect(url_for('nutritionist.dashboard'))
                else:
                    return redirect(url_for('dashboard.user_dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_role_dashboard(role):
    """Return dashboard route name based on role."""
    if role == 'admin':
        return 'admin.dashboard'
    elif role == 'trainer':
        return 'trainer.dashboard'
    elif role == 'nutritionist':
        return 'nutritionist.dashboard'
    return 'dashboard.user_dashboard'
