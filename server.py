from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import logging
from datetime import datetime
from database import get_db_connection

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

# Default user_id for all queries
USER_ID = 1


@app.before_request
def log_request_info():
    """Log information about each incoming request"""
    logger.info('=' * 80)
    logger.info(f'📥 Incoming Request: {request.method} {request.path}')
    logger.info(f'   Origin: {request.headers.get("Origin", "No origin header")}')
    logger.info(f'   User-Agent: {request.headers.get("User-Agent", "Unknown")}')
    if request.args:
        logger.info(f'   Query Params: {dict(request.args)}')


@app.after_request
def log_response_info(response):
    """Log information about each outgoing response"""
    logger.info(f'📤 Response Status: {response.status_code}')
    logger.info(f'   CORS Headers: Access-Control-Allow-Origin = {response.headers.get("Access-Control-Allow-Origin", "NOT SET")}')
    logger.info('=' * 80)
    return response


@app.route('/api/v1/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """
    Returns aggregate statistics from test results.
    """
    logger.info(f'🔍 Fetching dashboard stats for user_id: {USER_ID}')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(id) as tests_taken,
            AVG(score) as average_score,
            MAX(score) as highest_score,
            SUM(questions_answered) as questions_answered
        FROM test_results
        WHERE user_id = ?
    ''', (USER_ID,))
    
    result = cursor.fetchone()
    logger.info(f'   DB Result: tests_taken={result["tests_taken"]}, avg_score={result["average_score"]}, high_score={result["highest_score"]}, questions={result["questions_answered"]}')
    conn.close()
    
    # Handle case where there are no test results
    if result['tests_taken'] == 0:
        logger.warning('   ⚠️  No test results found, returning N/A values')
        return jsonify({
            "testsTaken": "N/A",
            "averageScore": "N/A",
            "highestScore": "N/A",
            "questionsAnswered": "N/A"
        })
    
    response_data = {
        "testsTaken": result['tests_taken'],
        "averageScore": int(result['average_score']),
        "highestScore": result['highest_score'],
        "questionsAnswered": result['questions_answered']
    }
    logger.info(f'   ✅ Returning stats: {response_data}')
    return jsonify(response_data)


@app.route('/api/v1/dashboard/recommendations', methods=['GET'])
def get_recommendations():
    """
    Returns a list of recommended topics for the user.
    """
    logger.info(f'🔍 Fetching recommendations for user_id: {USER_ID}')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, summary
        FROM recommended_topics
        WHERE user_id = ?
    ''', (USER_ID,))
    
    topics = cursor.fetchall()
    logger.info(f'   DB Result: Found {len(topics)} recommended topics')
    conn.close()
    
    # Format response with id as string
    recommendations = [
        {
            "id": str(topic['id']),
            "title": topic['title'],
            "summary": topic['summary']
        }
        for topic in topics
    ]
    
    logger.info(f'   ✅ Returning {len(recommendations)} recommendations')
    return jsonify(recommendations)


@app.route('/api/v1/topics/<string:topic_id>/details', methods=['GET'])
def get_topic_details(topic_id):
    """
    Returns detailed information about a specific topic.
    """
    logger.info(f'🔍 Fetching topic details for topic_id: {topic_id}, user_id: {USER_ID}')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT *
        FROM recommended_topics
        WHERE id = ? AND user_id = ?
    ''', (topic_id, USER_ID))
    
    topic = cursor.fetchone()
    conn.close()
    
    if not topic:
        logger.warning(f'   ⚠️  Topic {topic_id} not found')
        return jsonify({"error": "Topic not found"}), 404
    
    logger.info(f'   DB Result: Found topic "{topic["title"]}"')
    
    # Deserialize JSON strings
    key_concepts = json.loads(topic['key_concepts'])
    common_pitfalls = json.loads(topic['common_pitfalls'])
    
    # Build example object
    example = {
        "title": topic['example_title'],
        "code": topic['example_code'],
        "explanation": topic['example_explanation']
    }
    
    response_data = {
        "id": str(topic['id']),
        "title": topic['title'],
        "summary": topic['summary'],
        "keyConcepts": key_concepts,
        "commonPitfalls": common_pitfalls,
        "example": example
    }
    logger.info(f'   ✅ Returning topic details with {len(key_concepts)} concepts and {len(common_pitfalls)} pitfalls')
    return jsonify(response_data)


@app.route('/api/v1/flashcards', methods=['GET'])
def get_flashcards():
    """
    Returns all flashcards for the user.
    """
    logger.info(f'🔍 Fetching flashcards for user_id: {USER_ID}')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, front_content, back_content
        FROM flashcards
        WHERE user_id = ?
    ''', (USER_ID,))
    
    flashcards = cursor.fetchall()
    logger.info(f'   DB Result: Found {len(flashcards)} flashcards')
    conn.close()
    
    # Format response with id as string
    flashcards_list = [
        {
            "id": str(card['id']),
            "front": card['front_content'],
            "back": card['back_content']
        }
        for card in flashcards
    ]
    
    logger.info(f'   ✅ Returning {len(flashcards_list)} flashcards')
    return jsonify(flashcards_list)


@app.route('/api/v1/profile/stats', methods=['GET'])
def get_profile_stats():
    """
    Returns profile statistics including study time and test completion.
    """
    logger.info(f'🔍 Fetching profile stats for user_id: {USER_ID}')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            SUM(duration_seconds) as total_study_time,
            COUNT(id) as tests_completed,
            MAX(score) as highest_score
        FROM test_results
        WHERE user_id = ?
    ''', (USER_ID,))
    
    result = cursor.fetchone()
    logger.info(f'   DB Result: total_seconds={result["total_study_time"]}, tests={result["tests_completed"]}, high_score={result["highest_score"]}')
    conn.close()
    
    # Format study time as "Xh Ym"
    total_seconds = result['total_study_time'] or 0
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    study_time_formatted = f"{hours}h {minutes}m"
    
    response_data = {
        "totalStudyTime": study_time_formatted,
        "testsCompleted": result['tests_completed'],
        "highestScore": result['highest_score'] or 0,
        "achievementsUnlocked": 6,
        "totalAchievements": 9
    }
    logger.info(f'   ✅ Returning profile stats: {response_data}')
    return jsonify(response_data)


@app.route('/api/v1/profile/mastery', methods=['GET'])
def get_profile_mastery():
    """
    Returns topic mastery data for the user's profile.
    """
    logger.info(f'🔍 Fetching mastery data for user_id: {USER_ID}')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT topic_name, mastery_score
        FROM topic_mastery
        WHERE user_id = ?
    ''', (USER_ID,))
    
    mastery_data = cursor.fetchall()
    logger.info(f'   DB Result: Found {len(mastery_data)} mastery records')
    conn.close()
    
    # Rename fields for frontend
    mastery_list = [
        {
            "topic": row['topic_name'],
            "mastery": row['mastery_score']
        }
        for row in mastery_data
    ]
    
    logger.info(f'   ✅ Returning {len(mastery_list)} mastery records')
    return jsonify(mastery_list)


@app.route('/api/v1/presets', methods=['GET'])
def get_presets():
    """
    Returns hardcoded preset test options.
    """
    logger.info('🔍 Fetching presets (hardcoded data)')
    presets = [
        {
            "id": "GRE",
            "name": "GRE",
            "description": "Graduate Record Examinations"
        },
        {
            "id": "SAT",
            "name": "SAT",
            "description": "Scholastic Assessment Test"
        },
        {
            "id": "ACT",
            "name": "ACT",
            "description": "American College Testing"
        }
    ]
    
    logger.info(f'   ✅ Returning {len(presets)} presets')
    return jsonify(presets)


@app.route('/', methods=['GET'])
def home():
    """
    Health check endpoint.
    """
    logger.info('🏠 Health check endpoint called')
    return jsonify({
        "message": "MindCraftr API is running!",
        "version": "1.0.0"
    })


@app.errorhandler(Exception)
def handle_error(error):
    """
    Global error handler for unexpected errors.
    """
    logger.error(f'❌ Unexpected error: {str(error)}', exc_info=True)
    return jsonify({
        "error": "Internal server error",
        "message": str(error)
    }), 500


if __name__ == '__main__':
    logger.info('🚀 Starting MindCraftr API server...')
    logger.info('📍 Server will run on http://localhost:5001')
    logger.info('🔓 CORS is enabled for all origins')
    app.run(debug=True, port=5002, host='0.0.0.0')

