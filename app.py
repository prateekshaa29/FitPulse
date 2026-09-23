import os
from datetime import datetime
from flask import Flask, render_template, session
from config import config_by_name
from models import db, User

def create_app(config_name='development'):
    """Application factory for the Fitness & Workout Tracker."""
    app = Flask(__name__)
    
    # Load configuration
    config_class = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_class)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.profile import profile_bp
    from routes.workout import workout_bp
    from routes.goal import goal_bp
    from routes.weight import weight_bp
    from routes.bmi import bmi_bp
    from routes.progress import progress_bp
    from routes.trainer import trainer_bp
    from routes.nutritionist import nutritionist_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(workout_bp)
    app.register_blueprint(goal_bp)
    app.register_blueprint(weight_bp)
    app.register_blueprint(bmi_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(trainer_bp)
    app.register_blueprint(nutritionist_bp)
    app.register_blueprint(admin_bp)

    # Context processors
    @app.context_processor
    def inject_globals():
        current_user = None
        user_id = session.get('user_id')
        if user_id:
            current_user = db.session.get(User, user_id)
        return {
            'current_user': current_user,
            'current_year': datetime.now().year
        }

    # Error handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # CLI commands
    @app.cli.command('init-db')
    def init_db_command():
        """Initialize the database tables."""
        db.create_all()
        print('Initialized the database tables.')

    return app

app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=5000, debug=True)
