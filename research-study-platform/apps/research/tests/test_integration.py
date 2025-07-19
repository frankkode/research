"""
Integration tests for study workflow
"""

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.utils import timezone
from datetime import timedelta
import json

from apps.research.models import (
    ResearchStudy, ParticipantProfile, InteractionLog, ChatInteraction,
    PDFViewingBehavior, QuizResponse, DataExport
)
from apps.studies.models import StudySession
from apps.research.logging_service import research_logger
from apps.research.privacy_service import privacy_service
from apps.research.utilities import research_utilities

User = get_user_model()


class StudyWorkflowIntegrationTest(APITestCase):
    """Test complete study workflow integration"""
    
    def setUp(self):
        # Create researcher
        self.researcher = User.objects.create_user(
            username='researcher',
            email='researcher@test.com',
            participant_id='R001',
            study_group='PDF'
        )
        self.researcher.is_staff = True
        self.researcher.save()
        
        self.token = Token.objects.create(user=self.researcher)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    
    def test_complete_study_lifecycle(self):
        """Test complete study lifecycle from creation to completion"""
        
        # Step 1: Create a research study
        study_data = {
            'name': 'Linux Learning Study',
            'description': 'Study comparing PDF vs ChatGPT learning methods',
            'max_participants': 10,
            'group_balance_ratio': {'PDF': 0.5, 'CHATGPT': 0.5},
            'requires_consent': True,
            'has_pre_quiz': True,
            'has_post_quiz': True
        }
        
        study_response = self.client.post(
            reverse('researchstudy-list'),
            study_data,
            format='json'
        )
        
        self.assertEqual(study_response.status_code, status.HTTP_201_CREATED)
        study_id = study_response.data['id']
        
        # Step 2: Bulk generate participants
        participants_data = {
            'participant_count': 6,
            'assignment_method': 'balanced',
            'id_prefix': 'P'
        }
        
        participants_response = self.client.post(
            reverse('researchstudy-bulk-create-participants', kwargs={'pk': study_id}),
            participants_data,
            format='json'
        )
        
        self.assertEqual(participants_response.status_code, status.HTTP_201_CREATED)
        participants = participants_response.data
        self.assertEqual(len(participants), 6)
        
        # Verify balanced group assignment
        pdf_count = sum(1 for p in participants if p['assigned_group'] == 'PDF')
        chatgpt_count = sum(1 for p in participants if p['assigned_group'] == 'CHATGPT')
        self.assertEqual(pdf_count, 3)
        self.assertEqual(chatgpt_count, 3)
        
        # Step 3: Simulate participant study sessions
        for i, participant_data in enumerate(participants[:2]):  # Test with first 2 participants
            participant_id = participant_data['anonymized_id']
            session_id = f"session_{participant_id}_{i}"
            
            # 3a: Log session start
            session_start_response = self.client.post(
                reverse('log_session_event'),
                {
                    'participant_id': participant_id,
                    'session_id': session_id,
                    'event_type': 'session_start',
                    'event_data': {
                        'user_agent': 'Mozilla/5.0...',
                        'screen_resolution': '1920x1080'
                    }
                },
                format='json'
            )
            self.assertEqual(session_start_response.status_code, status.HTTP_201_CREATED)
            
            # 3b: Log consent phase
            consent_response = self.client.post(
                reverse('log_interaction'),
                {
                    'participant_id': participant_id,
                    'session_id': session_id,
                    'log_type': 'form_submit',
                    'event_data': {
                        'form_type': 'consent',
                        'consent_given': True
                    }
                },
                format='json'
            )
            self.assertEqual(consent_response.status_code, status.HTTP_201_CREATED)
            
            # 3c: Log pre-quiz responses
            for q in range(1, 4):  # 3 questions
                quiz_response = self.client.post(
                    reverse('log_quiz_response'),
                    {
                        'participant_id': participant_id,
                        'session_id': session_id,
                        'quiz_type': 'pre_quiz',
                        'question_id': f'q{q}',
                        'question_text': f'Question {q}',
                        'question_type': 'multiple_choice',
                        'response_value': 'option_a',
                        'is_correct': True,
                        'time_spent_seconds': 30
                    },
                    format='json'
                )
                self.assertEqual(quiz_response.status_code, status.HTTP_201_CREATED)
            
            # 3d: Log interaction phase based on group
            if participant_data['assigned_group'] == 'CHATGPT':
                # Log chat interactions
                chat_messages = [
                    'What is the Linux command to list files?',
                    'How do I change file permissions?',
                    'What is the difference between chmod and chown?'
                ]
                
                for message in chat_messages:
                    chat_response = self.client.post(
                        reverse('log_chat_interaction'),
                        {
                            'participant_id': participant_id,
                            'session_id': session_id,
                            'message_type': 'user_message',
                            'content': message,
                            'response_time_ms': 1500,
                            'token_count': 50,
                            'cost_usd': 0.001
                        },
                        format='json'
                    )
                    self.assertEqual(chat_response.status_code, status.HTTP_201_CREATED)
                    
                    # Log assistant response
                    assistant_response = self.client.post(
                        reverse('log_chat_interaction'),
                        {
                            'participant_id': participant_id,
                            'session_id': session_id,
                            'message_type': 'assistant_response',
                            'content': f'Response to: {message}',
                            'response_time_ms': 2000,
                            'token_count': 100,
                            'cost_usd': 0.002
                        },
                        format='json'
                    )
                    self.assertEqual(assistant_response.status_code, status.HTTP_201_CREATED)
            
            else:  # PDF group
                # Log PDF viewing behavior
                for page in range(1, 6):  # 5 pages
                    pdf_response = self.client.post(
                        reverse('log_pdf_viewing'),
                        {
                            'participant_id': participant_id,
                            'session_id': session_id,
                            'pdf_name': 'linux_tutorial.pdf',
                            'pdf_hash': 'abc123hash',
                            'page_number': page,
                            'time_spent_seconds': 120,
                            'scroll_events': [
                                {'timestamp': '2024-01-01T10:00:00Z', 'scroll_y': 100},
                                {'timestamp': '2024-01-01T10:00:05Z', 'scroll_y': 200}
                            ]
                        },
                        format='json'
                    )
                    self.assertEqual(pdf_response.status_code, status.HTTP_201_CREATED)
            
            # 3e: Log post-quiz responses
            for q in range(1, 4):  # 3 questions
                quiz_response = self.client.post(
                    reverse('log_quiz_response'),
                    {
                        'participant_id': participant_id,
                        'session_id': session_id,
                        'quiz_type': 'post_quiz',
                        'question_id': f'q{q}',
                        'question_text': f'Post Question {q}',
                        'question_type': 'multiple_choice',
                        'response_value': 'option_b',
                        'is_correct': False,
                        'time_spent_seconds': 45
                    },
                    format='json'
                )
                self.assertEqual(quiz_response.status_code, status.HTTP_201_CREATED)
            
            # 3f: Log session end
            session_end_response = self.client.post(
                reverse('log_session_event'),
                {
                    'participant_id': participant_id,
                    'session_id': session_id,
                    'event_type': 'session_end',
                    'event_data': {
                        'session_duration_seconds': 3600
                    }
                },
                format='json'
            )
            self.assertEqual(session_end_response.status_code, status.HTTP_201_CREATED)
        
        # Step 4: Get study analytics
        analytics_response = self.client.get(
            reverse('researchstudy-analytics', kwargs={'pk': study_id})
        )
        
        self.assertEqual(analytics_response.status_code, status.HTTP_200_OK)
        analytics = analytics_response.data
        
        # Verify analytics data
        self.assertEqual(analytics['study_overview']['total_participants'], 6)
        self.assertIn('participant_stats', analytics)
        self.assertIn('interaction_stats', analytics)
        self.assertIn('chat_stats', analytics)
        self.assertIn('pdf_stats', analytics)
        self.assertIn('quiz_stats', analytics)
        
        # Step 5: Export data
        export_response = self.client.post(
            reverse('export_participants_enhanced'),
            {
                'study_id': study_id,
                'format': 'json',
                'filters': {}
            },
            format='json'
        )
        
        self.assertEqual(export_response.status_code, status.HTTP_200_OK)
        
        # Step 6: Get session summary for a participant
        participant_id = participants[0]['anonymized_id']
        session_id = f"session_{participant_id}_0"
        
        summary_response = self.client.get(
            reverse('get_session_summary'),
            {
                'participant_id': participant_id,
                'session_id': session_id
            }
        )
        
        self.assertEqual(summary_response.status_code, status.HTTP_200_OK)
        summary = summary_response.data
        
        self.assertEqual(summary['participant_id'], participant_id)
        self.assertEqual(summary['session_id'], session_id)
        self.assertGreater(summary['total_interactions'], 0)
        
        # Step 7: Validate data integrity
        integrity_response = self.client.get(
            reverse('validate_data_integrity'),
            {'study_id': study_id}
        )
        
        self.assertEqual(integrity_response.status_code, status.HTTP_200_OK)
        integrity = integrity_response.data
        
        self.assertIn('checks_performed', integrity)
        self.assertIn('statistics', integrity)
        self.assertEqual(integrity['statistics']['total_participants'], 6)
    
    def test_privacy_workflow(self):
        """Test privacy and GDPR compliance workflow"""
        
        # Create study and participant
        study = ResearchStudy.objects.create(
            name='Privacy Test Study',
            description='Test',
            created_by=self.researcher
        )
        
        participant_user = User.objects.create_user(
            username='participant',
            email='participant@test.com',
            participant_id='P001',
            study_group='PDF'
        )
        
        participant = ParticipantProfile.objects.create(
            user=participant_user,
            study=study,
            assigned_group='PDF',
            consent_given=True,
            gdpr_consent=True,
            data_processing_consent=True
        )
        
        # Create some test data
        InteractionLog.objects.create(
            participant=participant,
            session_id='test_session',
            log_type='button_click',
            event_data={'button_id': 'submit'}
        )
        
        ChatInteraction.objects.create(
            participant=participant,
            session_id='test_session',
            message_type='user_message',
            content='Sensitive information'
        )
        
        # Test 1: Get participant privacy status
        privacy_status_response = self.client.get(
            reverse('get_participant_privacy_status'),
            {'participant_id': participant.anonymized_id}
        )
        
        self.assertEqual(privacy_status_response.status_code, status.HTTP_200_OK)
        privacy_status = privacy_status_response.data
        
        self.assertTrue(privacy_status['consent_given'])
        self.assertTrue(privacy_status['gdpr_consent'])
        self.assertFalse(privacy_status['is_anonymized'])
        self.assertFalse(privacy_status['withdrawn'])
        
        # Test 2: Export participant data (Data Portability)
        export_response = self.client.post(
            reverse('export_participant_data'),
            {
                'participant_id': participant.anonymized_id,
                'format': 'json'
            },
            format='json'
        )
        
        self.assertEqual(export_response.status_code, status.HTTP_200_OK)
        
        # Test 3: Anonymize participant
        anonymize_response = self.client.post(
            reverse('anonymize_participant'),
            {
                'participant_id': participant.anonymized_id,
                'reason': 'GDPR Request'
            },
            format='json'
        )
        
        self.assertEqual(anonymize_response.status_code, status.HTTP_200_OK)
        self.assertTrue(anonymize_response.data['success'])
        
        # Verify anonymization
        participant.refresh_from_db()
        self.assertTrue(participant.is_anonymized)
        
        # Test 4: Get GDPR compliance status
        compliance_response = self.client.get(
            reverse('get_gdpr_compliance_status')
        )
        
        self.assertEqual(compliance_response.status_code, status.HTTP_200_OK)
        compliance = compliance_response.data
        
        self.assertIn('overall_compliance', compliance)
        self.assertIn('studies', compliance)
        
        # Test 5: Generate privacy report
        report_response = self.client.get(
            reverse('generate_privacy_report'),
            {'study_id': str(study.id)}
        )
        
        self.assertEqual(report_response.status_code, status.HTTP_200_OK)
        report = report_response.data
        
        self.assertIn('participant_statistics', report)
        self.assertIn('compliance_status', report)
    
    def test_data_export_workflow(self):
        """Test comprehensive data export workflow"""
        
        # Create study with participants and data
        study = ResearchStudy.objects.create(
            name='Export Test Study',
            description='Test',
            created_by=self.researcher
        )
        
        participants = []
        for i in range(3):
            user = User.objects.create_user(
                username=f'participant{i}',
                email=f'participant{i}@test.com',
                participant_id=f'P{i:03d}',
                study_group='PDF' if i % 2 == 0 else 'CHATGPT'
            )
            
            participant = ParticipantProfile.objects.create(
                user=user,
                study=study,
                assigned_group='PDF' if i % 2 == 0 else 'CHATGPT'
            )
            
            participants.append(participant)
            
            # Create test data
            InteractionLog.objects.create(
                participant=participant,
                session_id=f'session_{i}',
                log_type='session_start',
                event_data={}
            )
            
            if participant.assigned_group == 'CHATGPT':
                ChatInteraction.objects.create(
                    participant=participant,
                    session_id=f'session_{i}',
                    message_type='user_message',
                    content=f'Test message {i}'
                )
            else:
                PDFViewingBehavior.objects.create(
                    participant=participant,
                    session_id=f'session_{i}',
                    pdf_name='test.pdf',
                    pdf_hash='hash123',
                    page_number=1,
                    time_spent_seconds=60
                )
        
        # Test different export formats
        export_tests = [
            {'format': 'csv', 'endpoint': 'export_participants_enhanced'},
            {'format': 'json', 'endpoint': 'export_participants_enhanced'},
            {'format': 'xlsx', 'endpoint': 'export_participants_enhanced'},
        ]
        
        for test in export_tests:
            response = self.client.post(
                reverse(test['endpoint']),
                {
                    'study_id': str(study.id),
                    'format': test['format'],
                    'filters': {}
                },
                format='json'
            )
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Verify content type
            if test['format'] == 'csv':
                self.assertIn('text/csv', response.get('Content-Type', ''))
            elif test['format'] == 'json':
                self.assertIn('application/json', response.get('Content-Type', ''))
            elif test['format'] == 'xlsx':
                self.assertIn('spreadsheet', response.get('Content-Type', ''))
        
        # Test specific data type exports
        data_export_tests = [
            'export_interactions_enhanced',
            'export_chat_interactions_enhanced',
            'export_pdf_behaviors_enhanced'
        ]
        
        for endpoint in data_export_tests:
            response = self.client.post(
                reverse(endpoint),
                {
                    'study_id': str(study.id),
                    'format': 'json',
                    'filters': {}
                },
                format='json'
            )
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test full dataset export
        full_export_response = self.client.post(
            reverse('export_full_dataset'),
            {
                'study_id': str(study.id),
                'filters': {}
            },
            format='json'
        )
        
        self.assertEqual(full_export_response.status_code, status.HTTP_200_OK)
        self.assertIn('spreadsheet', full_export_response.get('Content-Type', ''))
        
        # Test export history
        history_response = self.client.get(
            reverse('get_export_history'),
            {'study_id': str(study.id)}
        )
        
        self.assertEqual(history_response.status_code, status.HTTP_200_OK)
        history = history_response.data
        
        self.assertIn('exports', history)
        self.assertGreater(len(history['exports']), 0)
        
        # Test export statistics
        stats_response = self.client.get(
            reverse('get_export_stats'),
            {'study_id': str(study.id)}
        )
        
        self.assertEqual(stats_response.status_code, status.HTTP_200_OK)
        stats = stats_response.data
        
        self.assertIn('total_exports', stats)
        self.assertGreater(stats['total_exports'], 0)
    
    def test_research_utilities_workflow(self):
        """Test research utilities workflow"""
        
        # Create study
        study = ResearchStudy.objects.create(
            name='Utilities Test Study',
            description='Test',
            created_by=self.researcher,
            max_participants=50
        )
        
        # Test 1: Generate participant IDs
        ids_response = self.client.post(
            reverse('generate_participant_ids'),
            {
                'count': 5,
                'prefix': 'TEST',
                'length': 4
            },
            format='json'
        )
        
        self.assertEqual(ids_response.status_code, status.HTTP_200_OK)
        ids = ids_response.data
        
        self.assertEqual(len(ids['participant_ids']), 5)
        for participant_id in ids['participant_ids']:
            self.assertTrue(participant_id.startswith('TEST'))
        
        # Test 2: Calculate sample size
        sample_size_response = self.client.post(
            reverse('calculate_sample_size'),
            {
                'effect_size': 0.5,
                'alpha': 0.05,
                'power': 0.8,
                'two_tailed': True
            },
            format='json'
        )
        
        self.assertEqual(sample_size_response.status_code, status.HTTP_200_OK)
        sample_size = sample_size_response.data
        
        self.assertIn('sample_size_per_group', sample_size)
        self.assertIn('total_sample_size', sample_size)
        
        # Test 3: Estimate study duration
        duration_response = self.client.post(
            reverse('estimate_study_duration'),
            {
                'total_participants': 100,
                'enrollment_rate_per_day': 5,
                'avg_session_duration_hours': 1.5
            },
            format='json'
        )
        
        self.assertEqual(duration_response.status_code, status.HTTP_200_OK)
        duration = duration_response.data
        
        self.assertIn('estimated_enrollment_days', duration)
        self.assertIn('estimated_completion_date', duration)
        
        # Test 4: Bulk generate participants
        bulk_response = self.client.post(
            reverse('bulk_generate_participants'),
            {
                'study_id': str(study.id),
                'count': 10,
                'assignment_method': 'balanced',
                'id_prefix': 'BULK'
            },
            format='json'
        )
        
        self.assertEqual(bulk_response.status_code, status.HTTP_201_CREATED)
        bulk_result = bulk_response.data
        
        self.assertTrue(bulk_result['success'])
        self.assertEqual(bulk_result['count'], 10)
        
        # Test 5: Get study summary
        summary_response = self.client.get(
            reverse('generate_study_summary'),
            {'study_id': str(study.id)}
        )
        
        self.assertEqual(summary_response.status_code, status.HTTP_200_OK)
        summary = summary_response.data
        
        self.assertIn('participant_statistics', summary)
        self.assertEqual(summary['participant_statistics']['total_participants'], 10)
        
        # Test 6: Validate data integrity
        integrity_response = self.client.get(
            reverse('validate_data_integrity'),
            {'study_id': str(study.id)}
        )
        
        self.assertEqual(integrity_response.status_code, status.HTTP_200_OK)
        integrity = integrity_response.data
        
        self.assertIn('checks_performed', integrity)
        self.assertIn('statistics', integrity)
        
        # Test 7: Get available groups
        groups_response = self.client.get(
            reverse('get_available_groups'),
            {'study_id': str(study.id)}
        )
        
        self.assertEqual(groups_response.status_code, status.HTTP_200_OK)
        groups = groups_response.data
        
        self.assertIn('available_groups', groups)
        self.assertIn('PDF', groups['available_groups'])
        self.assertIn('CHATGPT', groups['available_groups'])


class PerformanceIntegrationTest(TransactionTestCase):
    """Test performance with larger datasets"""
    
    def setUp(self):
        self.researcher = User.objects.create_user(
            username='researcher',
            email='researcher@test.com',
            participant_id='R001',
            study_group='PDF'
        )
        self.researcher.is_staff = True
        self.researcher.save()
        
        self.study = ResearchStudy.objects.create(
            name='Performance Test Study',
            description='Test',
            created_by=self.researcher,
            max_participants=1000
        )
    
    def test_bulk_operations_performance(self):
        """Test performance of bulk operations"""
        
        # Test bulk participant creation
        result = research_utilities.bulk_generate_participants(
            str(self.study.id),
            100,
            'balanced',
            'PERF'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 100)
        
        # Verify participants were created
        self.assertEqual(ParticipantProfile.objects.filter(study=self.study).count(), 100)
        
        # Test bulk logging
        participants = ParticipantProfile.objects.filter(study=self.study)[:10]
        
        interactions = []
        for participant in participants:
            for i in range(10):  # 10 interactions per participant
                interactions.append({
                    'participant_id': participant.anonymized_id,
                    'session_id': f'session_{participant.id}',
                    'log_type': 'button_click',
                    'event_data': {'button_id': f'btn_{i}'}
                })
        
        # Test bulk logging performance
        results = research_logger.bulk_log_interactions(interactions)
        
        self.assertEqual(results['success_count'], 100)
        self.assertEqual(results['error_count'], 0)
        
        # Verify interactions were logged
        self.assertEqual(InteractionLog.objects.count(), 100)
    
    def test_export_performance_with_large_dataset(self):
        """Test export performance with larger dataset"""
        
        # Create participants with data
        participants = []
        for i in range(50):
            user = User.objects.create_user(
                username=f'perfuser{i}',
                email=f'perfuser{i}@test.com',
                participant_id=f'PERF{i:03d}',
                study_group='PDF' if i % 2 == 0 else 'CHATGPT'
            )
            
            participant = ParticipantProfile.objects.create(
                user=user,
                study=self.study,
                assigned_group='PDF' if i % 2 == 0 else 'CHATGPT'
            )
            
            participants.append(participant)
            
            # Create interactions
            for j in range(20):  # 20 interactions per participant
                InteractionLog.objects.create(
                    participant=participant,
                    session_id=f'session_{i}',
                    log_type='button_click',
                    event_data={'button_id': f'btn_{j}'}
                )
        
        # Test export performance
        from apps.research.export_service import research_exporter
        
        # Test CSV export
        csv_response = research_exporter.export_participants(
            study_id=str(self.study.id),
            export_format='csv'
        )
        
        self.assertEqual(csv_response.status_code, 200)
        
        # Test JSON export
        json_response = research_exporter.export_participants(
            study_id=str(self.study.id),
            export_format='json'
        )
        
        self.assertEqual(json_response.status_code, 200)
        
        # Test interactions export
        interactions_response = research_exporter.export_interactions(
            study_id=str(self.study.id),
            export_format='csv'
        )
        
        self.assertEqual(interactions_response.status_code, 200)
    
    def test_analytics_performance(self):
        """Test analytics performance with larger dataset"""
        
        # Create participants and data
        for i in range(30):
            user = User.objects.create_user(
                username=f'analyticsuser{i}',
                email=f'analyticsuser{i}@test.com',
                participant_id=f'ANAL{i:03d}',
                study_group='PDF' if i % 2 == 0 else 'CHATGPT'
            )
            
            participant = ParticipantProfile.objects.create(
                user=user,
                study=self.study,
                assigned_group='PDF' if i % 2 == 0 else 'CHATGPT'
            )
            
            # Create various types of data
            InteractionLog.objects.create(
                participant=participant,
                session_id=f'session_{i}',
                log_type='session_start',
                event_data={}
            )
            
            if participant.assigned_group == 'CHATGPT':
                ChatInteraction.objects.create(
                    participant=participant,
                    session_id=f'session_{i}',
                    message_type='user_message',
                    content=f'Test message {i}',
                    token_count=50,
                    cost_usd=0.001
                )
            else:
                PDFViewingBehavior.objects.create(
                    participant=participant,
                    session_id=f'session_{i}',
                    pdf_name='test.pdf',
                    pdf_hash='hash123',
                    page_number=1,
                    time_spent_seconds=60
                )
            
            QuizResponse.objects.create(
                participant=participant,
                session_id=f'session_{i}',
                quiz_type='pre_quiz',
                question_id='q1',
                question_text='Test question',
                question_type='multiple_choice',
                response_value='option_a',
                is_correct=True,
                first_viewed_at=timezone.now(),
                time_spent_seconds=30
            )
        
        # Test analytics generation
        from apps.research.views import ResearchStudyViewSet
        
        viewset = ResearchStudyViewSet()
        analytics = viewset._generate_study_analytics(self.study)
        
        self.assertIn('study_overview', analytics)
        self.assertIn('participant_stats', analytics)
        self.assertIn('interaction_stats', analytics)
        self.assertIn('chat_stats', analytics)
        self.assertIn('pdf_stats', analytics)
        self.assertIn('quiz_stats', analytics)
        
        # Verify analytics data
        self.assertEqual(analytics['study_overview']['total_participants'], 30)
        self.assertGreater(analytics['interaction_stats']['total_interactions'], 0)
        self.assertGreater(analytics['chat_stats']['total_messages'], 0)
        self.assertGreater(analytics['pdf_stats']['total_page_views'], 0)
        self.assertGreater(analytics['quiz_stats']['total_responses'], 0)