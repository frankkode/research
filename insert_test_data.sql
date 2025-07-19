-- SQL script to insert 4 test users directly into SQLite database
-- Run this with: sqlite3 db.sqlite3 < insert_test_data.sql

-- Insert test users
INSERT INTO core_user (
    username, email, password, study_group, consent_completed, 
    pre_quiz_completed, interaction_completed, post_quiz_completed, 
    study_completed, participant_id, is_active, is_staff, is_superuser,
    date_joined, created_at, study_completed_at
) VALUES 
('testuser1', 'test1@example.com', 'pbkdf2_sha256$390000$test$hash', 'CHATGPT', 1, 1, 1, 1, 1, 'TEST001', 1, 0, 0, datetime('now', '-10 days'), datetime('now', '-10 days'), datetime('now', '-1 day')),
('testuser2', 'test2@example.com', 'pbkdf2_sha256$390000$test$hash', 'CHATGPT', 1, 1, 1, 1, 1, 'TEST002', 1, 0, 0, datetime('now', '-9 days'), datetime('now', '-9 days'), datetime('now', '-2 days')),
('testuser3', 'test3@example.com', 'pbkdf2_sha256$390000$test$hash', 'PDF', 1, 1, 1, 1, 1, 'TEST003', 1, 0, 0, datetime('now', '-8 days'), datetime('now', '-8 days'), datetime('now', '-3 days')),
('testuser4', 'test4@example.com', 'pbkdf2_sha256$390000$test$hash', 'PDF', 1, 1, 0, 0, 0, 'TEST004', 1, 0, 0, datetime('now', '-7 days'), datetime('now', '-7 days'), NULL);

-- Insert research study if not exists
INSERT OR IGNORE INTO research_researchstudy (
    name, description, is_active, created_at, created_by_id
) VALUES 
('Linux Learning Study - Test', 'Test study for dashboard testing', 1, datetime('now', '-15 days'), 1);

-- Get the study ID (assuming it's 1)
-- Insert participant profiles
INSERT INTO research_participantprofile (
    user_id, study_id, assigned_group, consent_given, created_at, withdrawn, is_anonymized
) VALUES 
((SELECT id FROM core_user WHERE username='testuser1'), 1, 'CHATGPT', 1, datetime('now', '-10 days'), 0, 0),
((SELECT id FROM core_user WHERE username='testuser2'), 1, 'CHATGPT', 1, datetime('now', '-9 days'), 0, 0),
((SELECT id FROM core_user WHERE username='testuser3'), 1, 'PDF', 1, datetime('now', '-8 days'), 0, 0),
((SELECT id FROM core_user WHERE username='testuser4'), 1, 'PDF', 1, datetime('now', '-7 days'), 0, 0);

-- Insert study sessions
INSERT INTO studies_studysession (
    user_id, session_id, session_started_at, session_ended_at, 
    total_duration, interaction_duration, is_active
) VALUES 
((SELECT id FROM core_user WHERE username='testuser1'), 'session_testuser1', datetime('now', '-5 days'), datetime('now', '-5 days', '+1 hour'), 3600, 3000, 0),
((SELECT id FROM core_user WHERE username='testuser2'), 'session_testuser2', datetime('now', '-4 days'), datetime('now', '-4 days', '+1 hour 5 minutes'), 3900, 3300, 0),
((SELECT id FROM core_user WHERE username='testuser3'), 'session_testuser3', datetime('now', '-3 days'), datetime('now', '-3 days', '+1 hour 10 minutes'), 4200, 3600, 0),
((SELECT id FROM core_user WHERE username='testuser4'), 'session_testuser4', datetime('now', '-2 days'), NULL, 0, 0, 1);

-- Insert chat sessions for ChatGPT users
INSERT INTO chats_chatsession (
    session_id, total_messages, total_tokens_used, total_cost, 
    session_started_at, session_ended_at
) VALUES 
((SELECT id FROM studies_studysession WHERE session_id='session_testuser1'), 10, 1000, 0.05, datetime('now', '-5 days'), datetime('now', '-5 days', '+1 hour')),
((SELECT id FROM studies_studysession WHERE session_id='session_testuser2'), 13, 1500, 0.07, datetime('now', '-4 days'), datetime('now', '-4 days', '+1 hour 5 minutes'));

-- Insert PDF sessions for PDF users  
INSERT INTO pdfs_pdfsession (
    session_id, unique_pages_visited, total_time_spent,
    session_started_at, session_ended_at
) VALUES 
((SELECT id FROM studies_studysession WHERE session_id='session_testuser3'), 10, 2700, datetime('now', '-3 days'), datetime('now', '-3 days', '+1 hour 10 minutes')),
((SELECT id FROM studies_studysession WHERE session_id='session_testuser4'), 5, 1200, datetime('now', '-2 days'), NULL);

-- Insert some interaction logs
INSERT INTO research_interactionlog (
    participant_id, log_type, event_data, timestamp
) VALUES 
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser1')), 'page_view', '{"action": "view_dashboard"}', datetime('now', '-5 days')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser1')), 'chat_message', '{"action": "send_message"}', datetime('now', '-5 days', '+30 minutes')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser2')), 'page_view', '{"action": "view_chat"}', datetime('now', '-4 days')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser3')), 'page_view', '{"action": "view_pdf"}', datetime('now', '-3 days')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser4')), 'page_view', '{"action": "start_session"}', datetime('now', '-2 days'));

-- Insert chat interactions for ChatGPT users
INSERT INTO research_chatinteraction (
    participant_id, message_type, user_message, assistant_response,
    response_time_ms, token_count, cost_usd, message_timestamp, conversation_turn
) VALUES 
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser1')), 'user', 'How do I list files in Linux?', '', 1000, 50, 0.005, datetime('now', '-5 days', '+30 minutes'), 1),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser1')), 'assistant', '', 'Use the ls command to list files. Try ls -la for detailed view.', 1200, 60, 0.006, datetime('now', '-5 days', '+31 minutes'), 2),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser2')), 'user', 'What is the chmod command?', '', 1100, 55, 0.0055, datetime('now', '-4 days', '+20 minutes'), 1),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser2')), 'assistant', '', 'chmod changes file permissions. Use chmod 755 filename to make a file executable.', 1300, 65, 0.0065, datetime('now', '-4 days', '+21 minutes'), 2);

-- Insert PDF viewing behaviors for PDF users
INSERT INTO research_pdfviewingbehavior (
    participant_id, pdf_name, page_number, time_spent_seconds, timestamp
) VALUES 
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser3')), 'linux-commands-reference.pdf', 1, 120, datetime('now', '-3 days', '+10 minutes')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser3')), 'linux-commands-reference.pdf', 2, 180, datetime('now', '-3 days', '+15 minutes')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser3')), 'linux-commands-reference.pdf', 3, 150, datetime('now', '-3 days', '+20 minutes')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser4')), 'linux-commands-reference.pdf', 1, 90, datetime('now', '-2 days', '+5 minutes')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser4')), 'linux-commands-reference.pdf', 2, 110, datetime('now', '-2 days', '+10 minutes'));

-- Insert quiz responses
INSERT INTO research_quizresponse (
    participant_id, quiz_type, question_text, selected_answer, correct_answer,
    is_correct, time_spent_seconds, answered_at
) VALUES 
-- User 1 Pre-quiz (45% score - 1/3 correct)
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser1')), 'pre', 'Basic Linux file operations', 'ls command', 'ls command', 1, 60, datetime('now', '-6 days')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser1')), 'pre', 'Directory navigation', 'cd command', 'pwd command', 0, 75, datetime('now', '-6 days', '+2 minutes')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser1')), 'pre', 'File permissions', 'chmod 777', 'chmod 755', 0, 90, datetime('now', '-6 days', '+4 minutes')),

-- User 1 Post-quiz (85% score - 3/3 correct)  
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser1')), 'post', 'Advanced file operations', 'find command', 'find command', 1, 45, datetime('now', '-1 day')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser1')), 'post', 'Process management', 'ps aux', 'ps aux', 1, 50, datetime('now', '-1 day', '+2 minutes')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser1')), 'post', 'System monitoring', 'top command', 'top command', 1, 55, datetime('now', '-1 day', '+4 minutes')),

-- User 2 Pre-quiz (50% score - 1/3 correct)
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser2')), 'pre', 'Basic Linux file operations', 'ls command', 'ls command', 1, 65, datetime('now', '-5 days')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser2')), 'pre', 'Directory navigation', 'mkdir', 'cd command', 0, 70, datetime('now', '-5 days', '+2 minutes')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser2')), 'pre', 'File permissions', 'chmod 644', 'chmod 755', 0, 80, datetime('now', '-5 days', '+4 minutes')),

-- User 2 Post-quiz (90% score - 3/3 correct)
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser2')), 'post', 'Advanced file operations', 'find command', 'find command', 1, 40, datetime('now', '-1 day')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser2')), 'post', 'Process management', 'ps aux', 'ps aux', 1, 45, datetime('now', '-1 day', '+2 minutes')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser2')), 'post', 'System monitoring', 'top command', 'top command', 1, 50, datetime('now', '-1 day', '+4 minutes')),

-- User 3 Pre-quiz (40% score - 1/3 correct)
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser3')), 'pre', 'Basic Linux file operations', 'dir command', 'ls command', 0, 70, datetime('now', '-4 days')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser3')), 'pre', 'Directory navigation', 'cd command', 'cd command', 1, 85, datetime('now', '-4 days', '+2 minutes')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser3')), 'pre', 'File permissions', 'chmod 777', 'chmod 755', 0, 95, datetime('now', '-4 days', '+4 minutes')),

-- User 3 Post-quiz (75% score - 2/3 correct)
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser3')), 'post', 'Advanced file operations', 'find command', 'find command', 1, 50, datetime('now', '-1 day')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser3')), 'post', 'Process management', 'ps aux', 'ps aux', 1, 60, datetime('now', '-1 day', '+2 minutes')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser3')), 'post', 'System monitoring', 'htop command', 'top command', 0, 65, datetime('now', '-1 day', '+4 minutes')),

-- User 4 Pre-quiz only (55% score - 2/3 correct)
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser4')), 'pre', 'Basic Linux file operations', 'ls command', 'ls command', 1, 55, datetime('now', '-3 days')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser4')), 'pre', 'Directory navigation', 'cd command', 'cd command', 1, 60, datetime('now', '-3 days', '+2 minutes')),
((SELECT id FROM research_participantprofile WHERE user_id=(SELECT id FROM core_user WHERE username='testuser4')), 'pre', 'File permissions', 'chmod 644', 'chmod 755', 0, 75, datetime('now', '-3 days', '+4 minutes'));

-- Print summary
SELECT 'Test data inserted successfully!' as message;
SELECT 'Users created:' as message, COUNT(*) as count FROM core_user WHERE username LIKE 'testuser%';
SELECT 'ChatGPT group:' as message, COUNT(*) as count FROM core_user WHERE username LIKE 'testuser%' AND study_group = 'CHATGPT';
SELECT 'PDF group:' as message, COUNT(*) as count FROM core_user WHERE username LIKE 'testuser%' AND study_group = 'PDF';
SELECT 'Completed studies:' as message, COUNT(*) as count FROM core_user WHERE username LIKE 'testuser%' AND study_completed = 1;