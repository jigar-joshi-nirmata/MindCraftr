from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import logging
import uuid
from datetime import datetime
from database import get_db_connection
from opus_service import OpusClient, OpusAPIError

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


def generate_mock_questions(exam_name, num_questions, question_format, difficulty):
    """
    Generates mock questions for a test.
    """
    questions = []
    
    # Sample question templates based on difficulty
    sample_topics = [
        "React Hooks", "State Management", "Component Lifecycle", 
        "Props and Events", "API Integration", "Performance Optimization",
        "Testing", "Routing", "Error Handling", "Context API"
    ]
    
    for i in range(num_questions):
        question_id = str(uuid.uuid4())
        topic = sample_topics[i % len(sample_topics)]
        
        # Determine question type based on format
        if question_format == 'subjective':
            question_type = 'sa'  # Short Answer
            question = {
                "id": question_id,
                "type": question_type,
                "text": f"Explain the concept of {topic} and provide an example of its usage.",
                "correctAnswer": f"Sample answer for {topic}",
                "explanation": f"This question tests understanding of {topic} at {difficulty} level."
            }
        else:
            # Mix of MCQ and MSQ for objective
            options = [
                    {"id": "a", "text": f"Option A about {topic}"},
                    {"id": "b", "text": f"Option B about {topic}"},
                    {"id": "c", "text": f"Option C about {topic}"},
                    {"id": "d", "text": f"Option D about {topic}"}
                ]
            question = {
                "id": question_id,
                "type": "mcq",
                "text": f"What is the primary use case for {topic}?",
                "options": options,
                "correctAnswer": "b",
                "explanation": f"Option B is correct because {topic} is primarily used for this purpose."
            }
                
        
        questions.append(question)
    
    return questions


def map_to_opus(payload):
    """Map frontend format to Opus format"""
    exam_type = payload.get('examType', 'custom')
    
    if exam_type == 'custom':
        exam_name = payload.get('examName', 'Custom Test')
        num_questions = payload.get('numQuestions', 10)
        question_format = payload.get('questionFormat', 'objective')
        syllabus_content = payload.get('syllabusContent', '')
        preset_duration = 'Standard'
    else:
        exam_name = f"{exam_type} Practice Test"
        preset_duration_raw = payload.get('presetDuration', 'standard')
        question_format = 'objective'
        syllabus_content = f"Standard {exam_type} syllabus"
        duration_map = {'quick': ('Quick', 5), 'standard': ('Standard', 10), 'endurance': ('Endurance', 20)}
        preset_duration, num_questions = duration_map.get(preset_duration_raw, ('Standard', 10))
    
    diff_map = {'easy': 'Easy', 'standard': 'Standard', 'difficult': 'Difficult', 'medium': 'Standard'}
    difficulty = diff_map.get(payload.get('difficulty', 'standard').lower(), 'Standard')
    
    return {
        "EXAM_TYPE": question_format,
        "EXAM_DURATION": preset_duration,
        "EXAM_NAME": exam_name,
        "SYLLABUS_CONTENT": syllabus_content,
        "EXAM_DIFFICULTY": difficulty,
        "NUMBER_OF_QUESTIONS": num_questions
    }, exam_name, num_questions


def map_from_opus(opus_questions):
    """Map Opus format to frontend format"""
    frontend_questions = []
    option_ids = ['a', 'b', 'c', 'd', 'e', 'f']
    
    for q in opus_questions:
        question_id = str(uuid.uuid4())
        
        if q.get('type') == 'mcq' and isinstance(q.get('options'), list):
            options = []
            correct_id = 'a'
            
            for idx, opt in enumerate(q['options']):
                opt_id = option_ids[idx] if idx < len(option_ids) else str(idx)
                options.append({"id": opt_id, "text": opt})
                if opt == q.get('correctAnswer'):
                    correct_id = opt_id
            
            frontend_questions.append({
                "id": question_id,
                "type": "mcq",
                "text": q.get('text', ''),
                "options": options,
                "correctAnswer": correct_id,
                "explanation": q.get('explanation', '')
            })
        else:
            frontend_questions.append({
                "id": question_id,
                "type": q.get('type', 'sa'),
                "text": q.get('text', ''),
                "correctAnswer": q.get('correctAnswer', ''),
                "explanation": q.get('explanation', '')
            })
    
    return frontend_questions


@app.route('/api/v1/tests/generate', methods=['POST'])
def generate_test():
    """Generate test using Opus AI"""
    logger.info('🎯 Generate Test endpoint called')
    
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({"error": "No payload provided"}), 400
        
        # Map to Opus format
        opus_inputs, exam_name, num_questions = map_to_opus(payload)
        logger.info(f'📤 Opus inputs: {opus_inputs}')
        
        # Call Opus
        try:
            opus = OpusClient()
            opus_result = opus.run_workflow(opus_inputs)
            logger.info(f'✅ Opus completed')
            logger.info(f'Opus result structure: {list(opus_result.keys()) if isinstance(opus_result, dict) else type(opus_result)}')
            
            # Extract questions from jobResultsPayloadSchema
            if isinstance(opus_result, dict):
                schema = opus_result.get('jobResultsPayloadSchema', {})
                # Find the questions field (could be 'quiz_questions' or similar)
                opus_questions = []
                for key, value in schema.items():
                    if isinstance(value, dict) and 'value' in value:
                        opus_questions = value['value']
                        break
                
                if not opus_questions:
                    opus_questions = opus_result.get('questions', [])
            else:
                opus_questions = []
            
            logger.info(f'📝 Extracted {len(opus_questions)} questions from Opus')
            
            # Map from Opus
            questions = map_from_opus(opus_questions)
            logger.info(f'✅ Mapped {len(questions)} questions')
            
        except Exception as e:
            logger.error(f'❌ Opus failed: {e}, using mock')
            questions = generate_mock_questions(exam_name, num_questions, 'objective', 'standard')
        
        # Create response
        test_id = str(uuid.uuid4())
        test_data = {
            "id": test_id,
            "name": exam_name,
            "subject": exam_name,
            "duration": num_questions * 2,
            "questions": questions
        }
        
        # Save to DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO generated_tests 
            (user_id, test_id, exam_type, exam_name, num_questions, question_format, 
             difficulty, preset_duration, syllabus_content, test_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            USER_ID, test_id, payload.get('examType', 'custom'), exam_name,
            num_questions, 'objective', payload.get('difficulty', 'standard'),
            None, opus_inputs.get('SYLLABUS_CONTENT', ''), json.dumps(test_data)
        ))
        conn.commit()
        conn.close()
        
        logger.info(f'✅ Test saved: {test_id}')
        return jsonify(test_data), 201
        
    except Exception as e:
        logger.error(f'❌ Error: {e}', exc_info=True)
        return jsonify({"error": "Failed to generate test", "message": str(e)}), 500


@app.route('/api/v1/tests/submit', methods=['POST'])
def submit_test():
    """
    Submit test for grading using Opus AI
    
    Request body:
    {
      "answers": {"question_id": "answer", ...},
      "durationSeconds": 850,
      "fullTestContext": {
        "id": "test_id",
        "name": "Test name",
        "questions": [...]
      }
    }
    
    Response:
    {
      "score": 85,
      "aiSummary": "...",
      "strengths": [...],
      "weaknesses": [...],
      "correctAnswers": 17,
      "totalQuestions": 20
    }
    """
    logger.info('📝 Submit Test endpoint called')
    
    try:
        submission = request.get_json()
        if not submission:
            return jsonify({"error": "No submission data"}), 400
        
        logger.info(f'📤 Processing test submission')
        
        # Extract syllabus from stored test data if available
        syllabus_text = ""
        test_id = submission.get('fullTestContext', {}).get('id')
        
        if test_id:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT syllabus_content FROM generated_tests WHERE test_id = ?', (test_id,))
                row = cursor.fetchone()
                if row and row[0]:
                    syllabus_text = row[0]
                conn.close()
            except:
                pass
        
        # Call Opus grading
        try:
            opus = OpusClient()
            opus_result = opus.grade_test(submission, syllabus_text)
            logger.info(f'✅ Opus grading completed')
            logger.info(f'Opus result keys: {list(opus_result.keys()) if isinstance(opus_result, dict) else type(opus_result)}')
            
            # Extract grading results from jobResultsPayloadSchema
            grading_data = {}
            if isinstance(opus_result, dict):
                schema = opus_result.get('jobResultsPayloadSchema', {})
                
                logger.info(f'📊 Extracting from {len(schema)} output fields')
                
                # Extract by display_name
                for var_name, info in schema.items():
                    if isinstance(info, dict) and 'value' in info:
                        display_name = info.get('display_name', '').lower()
                        field_value = info['value']
                        
                        logger.info(f'  ✓ {info.get("display_name")}: {field_value}')
                        
                        # Map by exact display_name matching
                        if display_name == 'strength':
                            grading_data['strengths'] = field_value if isinstance(field_value, list) else [field_value]
                        elif display_name == 'weakness':
                            grading_data['weaknesses'] = field_value if isinstance(field_value, list) else [field_value]
                        elif 'ai summary' in display_name:
                            grading_data['aiSummary'] = field_value
                        elif display_name == 'score':
                            grading_data['score'] = int(field_value)
                        elif 'total questions' in display_name:
                            grading_data['totalQuestions'] = int(field_value)
                        elif 'correctly answered' in display_name:
                            grading_data['correctAnswers'] = int(field_value)
            
            # Build response
            total_questions = len(submission.get('fullTestContext', {}).get('questions', []))
            response = {
                "score": grading_data.get('score', 0),
                "aiSummary": grading_data.get('aiSummary', 'Test completed'),
                "strengths": grading_data.get('strengths', []),
                "weaknesses": grading_data.get('weaknesses', []),
                "correctAnswers": grading_data.get('correctAnswers', 0),
                "totalQuestions": grading_data.get('totalQuestions', total_questions)
            }
            
            logger.info(f'✅ Grading: {response["correctAnswers"]}/{response["totalQuestions"]} - Score: {response["score"]}%')
            
            # Save grading results to database
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Check if test_results has strengths/weaknesses columns, add if not
                cursor.execute("PRAGMA table_info(test_results)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'strengths' not in columns:
                    cursor.execute('ALTER TABLE test_results ADD COLUMN strengths TEXT')
                if 'weaknesses' not in columns:
                    cursor.execute('ALTER TABLE test_results ADD COLUMN weaknesses TEXT')
                if 'ai_summary' not in columns:
                    cursor.execute('ALTER TABLE test_results ADD COLUMN ai_summary TEXT')
                if 'test_id' not in columns:
                    cursor.execute('ALTER TABLE test_results ADD COLUMN test_id TEXT')
                
                # Insert result
                cursor.execute('''
                    INSERT INTO test_results 
                    (user_id, test_id, test_name, score, duration_seconds, questions_answered, 
                     total_questions, strengths, weaknesses, ai_summary)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    USER_ID,
                    test_id,
                    submission.get('fullTestContext', {}).get('name', 'Test'),
                    response['score'],
                    submission.get('durationSeconds', 0),
                    response['correctAnswers'],
                    response['totalQuestions'],
                    json.dumps(response['strengths']),
                    json.dumps(response['weaknesses']),
                    response['aiSummary']
                ))
                
                conn.commit()
                conn.close()
                logger.info(f'💾 Grading results saved to database')
            except Exception as e:
                logger.error(f'⚠️ Failed to save results: {e}')
            
            return jsonify(response), 200
            
        except Exception as e:
            logger.error(f'❌ Opus grading failed: {e}', exc_info=True)
            
            # Fallback: Manual grading
            answers = submission.get('answers', {})
            questions = submission.get('fullTestContext', {}).get('questions', [])
            
            correct = 0
            for q in questions:
                user_answer = answers.get(q['id'])
                if user_answer == q.get('correctAnswer'):
                    correct += 1
            
            total = len(questions)
            score = int((correct / total * 100)) if total > 0 else 0
            
            response = {
                "score": score,
                "aiSummary": f"You scored {correct} out of {total} questions correctly.",
                "strengths": [],
                "weaknesses": [],
                "correctAnswers": correct,
                "totalQuestions": total
            }
            
            # Save fallback results to database
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute("PRAGMA table_info(test_results)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'strengths' not in columns:
                    cursor.execute('ALTER TABLE test_results ADD COLUMN strengths TEXT')
                if 'weaknesses' not in columns:
                    cursor.execute('ALTER TABLE test_results ADD COLUMN weaknesses TEXT')
                if 'ai_summary' not in columns:
                    cursor.execute('ALTER TABLE test_results ADD COLUMN ai_summary TEXT')
                if 'test_id' not in columns:
                    cursor.execute('ALTER TABLE test_results ADD COLUMN test_id TEXT')
                
                cursor.execute('''
                    INSERT INTO test_results 
                    (user_id, test_id, test_name, score, duration_seconds, questions_answered, 
                     total_questions, strengths, weaknesses, ai_summary)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    USER_ID,
                    test_id,
                    submission.get('fullTestContext', {}).get('name', 'Test'),
                    score,
                    submission.get('durationSeconds', 0),
                    correct,
                    total,
                    json.dumps([]),
                    json.dumps([]),
                    response['aiSummary']
                ))
                
                conn.commit()
                conn.close()
                logger.info(f'💾 Fallback results saved')
            except Exception as db_error:
                logger.error(f'⚠️ Failed to save fallback results: {db_error}')
            
            return jsonify(response), 200
        
    except Exception as e:
        logger.error(f'❌ Error: {e}', exc_info=True)
        return jsonify({"error": "Failed to grade test", "message": str(e)}), 500


@app.route('/api/v1/tests/<test_id>/results', methods=['GET'])
def get_test_results(test_id):
    """
    Get grading results for a specific test
    
    Returns:
    {
      "score": 85,
      "aiSummary": "...",
      "strengths": [...],
      "weaknesses": [...],
      "correctAnswers": 17,
      "totalQuestions": 20,
      "testName": "...",
      "completedAt": "..."
    }
    """
    logger.info(f'📊 Get test results: {test_id}')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT test_name, score, duration_seconds, questions_answered, 
                   total_questions, strengths, weaknesses, ai_summary, completed_at
            FROM test_results 
            WHERE test_id = ? AND user_id = ?
            ORDER BY completed_at DESC
            LIMIT 1
        ''', (test_id, USER_ID))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({"error": "Test results not found"}), 404
        
        response = {
            "score": row[1],
            "aiSummary": row[7] if row[7] else "Test completed",
            "strengths": json.loads(row[5]) if row[5] else [],
            "weaknesses": json.loads(row[6]) if row[6] else [],
            "correctAnswers": row[3],
            "totalQuestions": row[4],
            "testName": row[0],
            "durationSeconds": row[2],
            "completedAt": row[8]
        }
        
        logger.info(f'✅ Results found: {response["score"]}%')
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f'❌ Error: {e}', exc_info=True)
        return jsonify({"error": "Failed to get results", "message": str(e)}), 500


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

