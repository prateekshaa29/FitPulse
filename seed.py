from datetime import date, timedelta
import random
from app import create_app
from models import db, User, Workout, Goal, WeightRecord, Recommendation

def seed_database():
    """Populate database with sample development and test data."""
    app = create_app('development')
    
    with app.app_context():
        # Drop and recreate all tables for a clean seed
        db.drop_all()
        db.create_all()
        print("Dropped and recreated database tables.")

        # 1. Create Core Users
        users_data = [
            {
                'name': 'Alex Johnson',
                'email': 'user@fitness.com',
                'password': 'User@123',
                'role': 'user',
                'age': 28,
                'gender': 'Male',
                'height': 178.0,
                'weight': 74.5
            },
            {
                'name': 'Sarah Miller',
                'email': 'sarah@fitness.com',
                'password': 'Sarah@123',
                'role': 'user',
                'age': 26,
                'gender': 'Female',
                'height': 165.0,
                'weight': 62.0
            },
            {
                'name': 'David Kim',
                'email': 'david@fitness.com',
                'password': 'David@123',
                'role': 'user',
                'age': 31,
                'gender': 'Male',
                'height': 180.0,
                'weight': 82.0
            },
            {
                'name': 'Marcus Vance (CPT)',
                'email': 'trainer@fitness.com',
                'password': 'Trainer@123',
                'role': 'trainer',
                'age': 34,
                'gender': 'Male',
                'height': 185.0,
                'weight': 86.0
            },
            {
                'name': 'Dr. Elena Rostova (RD)',
                'email': 'nutritionist@fitness.com',
                'password': 'Nutritionist@123',
                'role': 'nutritionist',
                'age': 32,
                'gender': 'Female',
                'height': 168.0,
                'weight': 59.0
            },
            {
                'name': 'System Administrator',
                'email': 'admin@fitness.com',
                'password': 'Admin@123',
                'role': 'admin',
                'age': 40,
                'gender': 'Other',
                'height': 175.0,
                'weight': 75.0
            }
        ]

        created_users = {}
        for u in users_data:
            user = User(
                name=u['name'],
                email=u['email'],
                role=u['role'],
                age=u['age'],
                gender=u['gender'],
                height=u['height'],
                weight=u['weight']
            )
            user.set_password(u['password'])
            db.session.add(user)
            db.session.flush()
            created_users[u['email']] = user
            print(f"Created user: {u['name']} ({u['email']}) as [{u['role']}]")

        alex = created_users['user@fitness.com']
        sarah = created_users['sarah@fitness.com']
        trainer = created_users['trainer@fitness.com']
        nutritionist = created_users['nutritionist@fitness.com']

        # 2. Seed Weight Logs for Alex (Showing gradual progression)
        today = date.today()
        base_weight = 77.8
        for i in range(30, -1, -3):
            log_date = today - timedelta(days=i)
            # Gradual weight loss curve with minor natural fluctuations
            wt = round(base_weight - ((30 - i) * 0.11) + random.uniform(-0.2, 0.2), 1)
            weight_entry = WeightRecord(
                user_id=alex.id,
                weight=wt,
                date=log_date,
                notes='Morning fasted weight measurement' if i % 6 == 0 else None
            )
            db.session.add(weight_entry)

        # 3. Seed Workouts for Alex (Across past 30 days)
        sample_workouts = [
            {'type': 'Running', 'name': 'Morning 5K Pace Run', 'duration': 28, 'sets': 1, 'reps': 5, 'cals': 310, 'notes': 'Targeted 5:36 min/km pace, felt strong.'},
            {'type': 'Strength Training', 'name': 'Upper Body Push (Chest & Shoulders)', 'duration': 55, 'sets': 16, 'reps': 12, 'cals': 420, 'notes': 'Bench Press 75kg 4x8, Overhead Press 45kg.'},
            {'type': 'Cycling', 'name': 'Outdoor Tempo Ride', 'duration': 45, 'sets': 1, 'reps': 18, 'cals': 480, 'notes': 'Good elevation, high cadence training.'},
            {'type': 'Yoga', 'name': 'Vinyasa Flow & Hip Mobility', 'duration': 35, 'sets': 1, 'reps': 1, 'cals': 160, 'notes': 'Focus on recovery and hamstrings.'},
            {'type': 'HIIT', 'name': 'Full Body Tabata Intervals', 'duration': 30, 'sets': 8, 'reps': 20, 'cals': 380, 'notes': 'Burpees, kettlebell swings, box jumps.'},
            {'type': 'Strength Training', 'name': 'Leg Day (Squats & Deadlifts)', 'duration': 60, 'sets': 18, 'reps': 10, 'cals': 510, 'notes': 'Squats 95kg 5x5, Romanian Deadlifts 80kg.'},
            {'type': 'Swimming', 'name': 'Freestyle Lap Intervals', 'duration': 40, 'sets': 12, 'reps': 50, 'cals': 390, 'notes': '1000m total distance.'},
            {'type': 'Walking', 'name': 'Evening Recovery Walk', 'duration': 45, 'sets': 1, 'reps': 4, 'cals': 180, 'notes': 'Active recovery session.'}
        ]

        for day_offset in [28, 26, 24, 21, 19, 17, 14, 12, 10, 8, 6, 4, 2, 0]:
            w_template = random.choice(sample_workouts)
            w_date = today - timedelta(days=day_offset)
            workout = Workout(
                user_id=alex.id,
                workout_type=w_template['type'],
                exercise_name=w_template['name'],
                duration=w_template['duration'],
                sets=w_template['sets'],
                repetitions=w_template['reps'],
                calories_burned=w_template['cals'],
                workout_date=w_date,
                notes=w_template['notes']
            )
            db.session.add(workout)

        # 4. Seed Goals for Alex
        goals_data = [
            {
                'goal_type': 'Lose Weight',
                'target_value': '72.0 kg',
                'current_value': '74.5 kg',
                'start_date': today - timedelta(days=20),
                'target_date': today + timedelta(days=30),
                'status': 'ACTIVE',
                'description': 'Target healthy sustainable fat loss with consistent caloric deficit.'
            },
            {
                'goal_type': 'Run Distance',
                'target_value': '10.0 km',
                'current_value': '6.5 km',
                'start_date': today - timedelta(days=15),
                'target_date': today + timedelta(days=45),
                'status': 'ACTIVE',
                'description': 'Train for upcoming community 10K road race.'
            },
            {
                'goal_type': 'Workout Frequency',
                'target_value': '16 Workouts / Month',
                'current_value': '16 Workouts',
                'start_date': today - timedelta(days=30),
                'target_date': today,
                'status': 'COMPLETED',
                'description': 'Maintain 4 workouts per week consistency.'
            },
            {
                'goal_type': 'Improve Strength',
                'target_value': '100 kg Bench Press',
                'current_value': '80 kg',
                'start_date': today - timedelta(days=10),
                'target_date': today + timedelta(days=60),
                'status': 'ACTIVE',
                'description': 'Progressive overload on barbell flat bench press.'
            }
        ]

        for g in goals_data:
            goal = Goal(
                user_id=alex.id,
                goal_type=g['goal_type'],
                target_value=g['target_value'],
                current_value=g['current_value'],
                start_date=g['start_date'],
                target_date=g['target_date'],
                status=g['status'],
                description=g['description']
            )
            db.session.add(goal)

        # 5. Seed Trainer Guidance Notes
        rec_trainer = Recommendation(
            user_id=alex.id,
            author_id=trainer.id,
            note_type='WORKOUT',
            title='Strength Progression & Rest Intervals',
            content='Great cadence on your upper body push workouts! Ensure you take a full 90-120 seconds of rest between your 5x5 compound sets to maximize central nervous system recovery.'
        )
        db.session.add(rec_trainer)

        # 6. Seed Nutritionist Dietary Notes
        rec_nutrition = Recommendation(
            user_id=alex.id,
            author_id=nutritionist.id,
            note_type='NUTRITION',
            title='Post-Workout Protein & Hydration Timing',
            content='Your weight trajectory is trending steadily downwards at a safe rate of 0.4kg/week. Aim for 25-30g of fast-absorbing protein within 45 minutes after strength sessions and drink at least 3 liters of water daily.'
        )
        db.session.add(rec_nutrition)

        db.session.commit()
        print("Successfully seeded all realistic test data!")

if __name__ == '__main__':
    seed_database()
