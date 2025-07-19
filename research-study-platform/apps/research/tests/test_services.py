"""
Unit tests for research services
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import json

from apps.research.models import (
    ResearchStudy, ParticipantProfile, InteractionLog, ChatInteraction,
    PDFViewingBehavior, QuizResponse
)
from apps.research.logging_service import ResearchDataLogger
from apps.research.privacy_service import PrivacyComplianceService
from apps.research.utilities import ResearchUtilities
from apps.research.export_service import ResearchDataExporter

User = get_user_model()


class ResearchDataLoggerTest(TestCase):
    """Test ResearchDataLogger service"""
    
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
            name='Test Study',
            description='Test',
            created_by=self.researcher
        )
        
        self.participant_user = User.objects.create_user(
            username='participant',
            email='participant@test.com',
            participant_id='P001',
            study_group='PDF'
        )
        
        self.participant = ParticipantProfile.objects.create(
            user=self.participant_user,
            study=self.study,
            assigned_group='PDF'
        )
        
        self.logger = ResearchDataLogger()
    
    def test_log_interaction(self):
        """Test logging general interaction"""
        success = self.logger.log_interaction(
            participant_id=self.participant.anonymized_id,
            session_id='test_session',
            log_type='button_click',
            event_data={'button_id': 'submit'},
            page_url='https://example.com/quiz',
            reaction_time_ms=1500
        )
        
        self.assertTrue(success)
        
        # Check that interaction was logged
        interaction = InteractionLog.objects.get(
            participant=self.participant,
            log_type='button_click'
        )
        self.assertEqual(interaction.event_data['button_id'], 'submit')
        self.assertEqual(interaction.reaction_time_ms, 1500)
    
    def test_log_chat_interaction(self):
        """Test logging chat interaction"""
        success = self.logger.log_chat_interaction(
            participant_id=self.participant.anonymized_id,
            session_id='test_session',
            message_type='user_message',
            content='What is machine learning?',
            response_time_ms=2000,
            token_count=150,
            cost_usd=0.003
        )
        
        self.assertTrue(success)
        
        # Check that chat interaction was logged
        chat = ChatInteraction.objects.get(
            participant=self.participant,
            message_type='user_message'
        )
        self.assertEqual(chat.content, 'What is machine learning?')
        self.assertEqual(chat.token_count, 150)
        self.assertEqual(chat.cost_usd, 0.003)
    
    def test_log_pdf_viewing(self):
        """Test logging PDF viewing behavior"""
        success = self.logger.log_pdf_viewing(
            participant_id=self.participant.anonymized_id,
            session_id='test_session',
            pdf_name='linux_tutorial.pdf',
            pdf_hash='abc123',
            page_number=5,
            time_spent_seconds=120,
            scroll_events=[{'timestamp': '2024-01-01T10:00:00Z', 'scroll_y': 100}]
        )
        
        self.assertTrue(success)
        
        # Check that PDF viewing was logged
        pdf_behavior = PDFViewingBehavior.objects.get(
            participant=self.participant,
            pdf_name='linux_tutorial.pdf'
        )
        self.assertEqual(pdf_behavior.page_number, 5)
        self.assertEqual(pdf_behavior.time_spent_seconds, 120)
        self.assertEqual(len(pdf_behavior.scroll_events), 1)
    
    def test_log_quiz_response(self):
        """Test logging quiz response"""
        success = self.logger.log_quiz_response(
            participant_id=self.participant.anonymized_id,
            session_id='test_session',
            quiz_type='pre_quiz',
            question_id='q1',
            question_text='What is the command to list files?',
            question_type='multiple_choice',
            response_value='ls',
            is_correct=True,
            time_spent_seconds=30
        )
        
        self.assertTrue(success)
        
        # Check that quiz response was logged
        quiz_response = QuizResponse.objects.get(
            participant=self.participant,
            quiz_type='pre_quiz'
        )
        self.assertEqual(quiz_response.question_id, 'q1')
        self.assertEqual(quiz_response.response_value, 'ls')
        self.assertTrue(quiz_response.is_correct)
    
    def test_bulk_log_interactions(self):
        """Test bulk logging interactions"""
        interactions = [
            {
                'participant_id': self.participant.anonymized_id,
                'session_id': 'test_session',
                'log_type': 'button_click',
                'event_data': {'button_id': 'submit'}
            },
            {
                'participant_id': self.participant.anonymized_id,
                'session_id': 'test_session',
                'log_type': 'page_view',
                'event_data': {'page': 'quiz'}
            }
        ]
        
        results = self.logger.bulk_log_interactions(interactions)
        
        self.assertEqual(results['success_count'], 2)
        self.assertEqual(results['error_count'], 0)
        
        # Check that interactions were logged
        self.assertEqual(InteractionLog.objects.filter(participant=self.participant).count(), 2)
    
    def test_get_participant_session_summary(self):
        """Test getting participant session summary"""
        # Create some interactions
        self.logger.log_interaction(
            participant_id=self.participant.anonymized_id,
            session_id='test_session',
            log_type='session_start',
            event_data={}
        )
        
        self.logger.log_interaction(
            participant_id=self.participant.anonymized_id,
            session_id='test_session',
            log_type='button_click',
            event_data={'button_id': 'submit'}
        )
        
        summary = self.logger.get_participant_session_summary(
            self.participant.anonymized_id,
            'test_session'
        )
        
        self.assertEqual(summary['participant_id'], self.participant.anonymized_id)
        self.assertEqual(summary['session_id'], 'test_session')
        self.assertEqual(summary['total_interactions'], 2)
    
    def test_invalid_participant_id(self):
        """Test logging with invalid participant ID"""
        success = self.logger.log_interaction(
            participant_id='INVALID_ID',
            session_id='test_session',
            log_type='button_click',
            event_data={}
        )
        
        self.assertFalse(success)


class PrivacyComplianceServiceTest(TestCase):
    """Test PrivacyComplianceService"""
    
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
            name='Test Study',
            description='Test',
            created_by=self.researcher
        )
        
        self.participant_user = User.objects.create_user(
            username='participant',
            email='participant@test.com',
            participant_id='P001',
            study_group='PDF'
        )
        
        self.participant = ParticipantProfile.objects.create(
            user=self.participant_user,
            study=self.study,
            assigned_group='PDF'
        )
        
        self.privacy_service = PrivacyComplianceService()
    
    def test_anonymize_participant(self):
        """Test anonymizing participant data"""
        result = self.privacy_service.anonymize_participant(
            self.participant.anonymized_id,
            'GDPR Request'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['participant_id'], self.participant.anonymized_id)
        
        # Check that participant was anonymized
        self.participant.refresh_from_db()
        self.assertTrue(self.participant.is_anonymized)
        
        # Check that user data was anonymized
        self.participant.user.refresh_from_db()
        self.assertTrue(self.participant.user.email.endswith('@anonymized.local'))
    
    def test_export_participant_data(self):
        """Test exporting participant data"""
        # Create some test data
        InteractionLog.objects.create(
            participant=self.participant,
            session_id='test_session',
            log_type='button_click',
            event_data={'button_id': 'submit'}
        )
        
        result = self.privacy_service.export_participant_data(
            self.participant.anonymized_id,
            'json'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['participant_id'], self.participant.anonymized_id)
        self.assertIn('data', result)
        self.assertIn('participant_info', result['data'])
        self.assertIn('interactions', result['data'])
    
    def test_generate_privacy_report(self):
        """Test generating privacy report"""
        report = self.privacy_service.generate_privacy_report(str(self.study.id))
        
        self.assertIn('participant_statistics', report)
        self.assertIn('compliance_status', report)
        self.assertIn('data_retention', report)
        self.assertEqual(report['participant_statistics']['total_participants'], 1)
    
    def test_process_data_retention_dry_run(self):
        """Test data retention processing in dry run mode"""
        # Create an old participant (simulate old data)
        old_participant_user = User.objects.create_user(
            username='old_participant',
            email='old@test.com',
            participant_id='P002',
            study_group='PDF'
        )
        
        old_participant = ParticipantProfile.objects.create(
            user=old_participant_user,
            study=self.study,
            assigned_group='PDF'
        )
        
        # Manually set old creation date
        old_date = timezone.now() - timedelta(days=3000)  # > 7 years ago
        old_participant.created_at = old_date
        old_participant.save()
        
        results = self.privacy_service.process_data_retention(
            study_id=str(self.study.id),
            dry_run=True
        )
        
        self.assertTrue(results['dry_run'])
        self.assertEqual(results['participants_found'], 1)
        self.assertEqual(len(results['processed_participants']), 1)
    
    def test_delete_participant_data(self):
        """Test deleting participant data"""
        participant_id = self.participant.anonymized_id
        
        # Create some test data
        InteractionLog.objects.create(
            participant=self.participant,
            session_id='test_session',
            log_type='button_click',
            event_data={}
        )
        
        result = self.privacy_service.delete_participant_data(
            participant_id,
            'Right to be Forgotten'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['participant_id'], participant_id)
        self.assertIn('deleted_counts', result)
        
        # Check that participant was deleted
        self.assertFalse(ParticipantProfile.objects.filter(anonymized_id=participant_id).exists())
        
        # Check that related data was deleted
        self.assertEqual(InteractionLog.objects.filter(participant__anonymized_id=participant_id).count(), 0)


class ResearchUtilitiesTest(TestCase):
    """Test ResearchUtilities service"""
    
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
            name='Test Study',
            description='Test',
            created_by=self.researcher,
            max_participants=100,
            group_balance_ratio={'PDF': 0.5, 'CHATGPT': 0.5}
        )
        
        self.utilities = ResearchUtilities()
    
    def test_generate_participant_id(self):
        """Test generating participant ID"""
        participant_id = self.utilities.generate_participant_id('T', 6)
        
        self.assertTrue(participant_id.startswith('T'))
        self.assertEqual(len(participant_id), 7)  # T + 6 chars
    
    def test_generate_session_id(self):
        """Test generating session ID"""
        session_id = self.utilities.generate_session_id('P001')
        
        self.assertTrue(session_id.startswith('P001_'))
        self.assertTrue('_' in session_id)
    
    def test_assign_group_random(self):
        """Test random group assignment"""
        assignments = self.utilities.assign_group_random(str(self.study.id), 10)
        
        self.assertEqual(len(assignments), 10)
        
        # Check that all assignments are valid groups
        for assignment in assignments:
            self.assertIn(assignment, ['PDF', 'CHATGPT'])
    
    def test_assign_group_balanced(self):
        """Test balanced group assignment"""
        assignments = self.utilities.assign_group_balanced(str(self.study.id), 4)
        
        self.assertEqual(len(assignments), 4)
        
        # Check that groups are balanced
        pdf_count = assignments.count('PDF')
        chatgpt_count = assignments.count('CHATGPT')
        self.assertEqual(pdf_count, 2)
        self.assertEqual(chatgpt_count, 2)
    
    def test_bulk_generate_participants(self):
        """Test bulk generating participants"""
        result = self.utilities.bulk_generate_participants(
            str(self.study.id),
            5,
            'balanced',
            'T'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 5)
        self.assertEqual(len(result['participants']), 5)
        
        # Check that participants were created
        self.assertEqual(ParticipantProfile.objects.filter(study=self.study).count(), 5)
        
        # Check that all participants have the correct prefix
        for participant in result['participants']:
            self.assertTrue(participant['participant_id'].startswith('T'))
    
    def test_calculate_sample_size(self):
        """Test sample size calculation"""
        sample_size = self.utilities.calculate_sample_size(
            effect_size=0.5,
            alpha=0.05,
            power=0.8
        )
        
        self.assertIsInstance(sample_size, int)
        self.assertGreater(sample_size, 0)
    
    def test_estimate_study_duration(self):
        """Test study duration estimation"""
        estimation = self.utilities.estimate_study_duration(
            total_participants=100,
            enrollment_rate_per_day=5,
            avg_session_duration_hours=1.5
        )
        
        self.assertIn('estimated_enrollment_days', estimation)
        self.assertIn('total_session_hours', estimation)
        self.assertEqual(estimation['estimated_enrollment_days'], 20)
        self.assertEqual(estimation['total_session_hours'], 150)
    
    def test_validate_data_integrity(self):
        """Test data integrity validation"""
        # Create a participant
        participant_user = User.objects.create_user(
            username='participant',
            email='participant@test.com',
            participant_id='P001',
            study_group='PDF'
        )
        
        participant = ParticipantProfile.objects.create(
            user=participant_user,
            study=self.study,
            assigned_group='PDF'
        )
        
        results = self.utilities.validate_data_integrity(str(self.study.id))
        
        self.assertIn('checks_performed', results)
        self.assertIn('issues_found', results)
        self.assertIn('statistics', results)
        self.assertEqual(results['statistics']['total_participants'], 1)
    
    def test_generate_study_summary(self):
        """Test generating study summary"""
        # Create a participant
        participant_user = User.objects.create_user(
            username='participant',
            email='participant@test.com',
            participant_id='P001',
            study_group='PDF'
        )
        
        participant = ParticipantProfile.objects.create(
            user=participant_user,
            study=self.study,
            assigned_group='PDF'
        )
        
        summary = self.utilities.generate_study_summary(str(self.study.id))
        
        self.assertIn('participant_statistics', summary)
        self.assertIn('group_distribution', summary)
        self.assertIn('data_collection', summary)
        self.assertEqual(summary['participant_statistics']['total_participants'], 1)
    
    def test_generate_randomization_seed(self):
        """Test generating randomization seed"""
        seed = self.utilities.generate_randomization_seed(str(self.study.id), 'P001')
        
        self.assertIsInstance(seed, str)
        self.assertEqual(len(seed), 16)
        
        # Test that same inputs produce same seed
        seed2 = self.utilities.generate_randomization_seed(str(self.study.id), 'P001')
        self.assertEqual(seed, seed2)
    
    def test_bulk_generate_exceeds_limit(self):
        """Test bulk generation exceeding study limit"""
        # Set a low limit
        self.study.max_participants = 3
        self.study.save()
        
        result = self.utilities.bulk_generate_participants(
            str(self.study.id),
            5,  # Exceeds limit
            'balanced'
        )
        
        self.assertFalse(result['success'])
        self.assertIn('exceed maximum participants', result['error'])


class ResearchDataExporterTest(TestCase):
    """Test ResearchDataExporter service"""
    
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
            name='Test Study',
            description='Test',
            created_by=self.researcher
        )
        
        self.participant_user = User.objects.create_user(
            username='participant',
            email='participant@test.com',
            participant_id='P001',
            study_group='PDF'
        )
        
        self.participant = ParticipantProfile.objects.create(
            user=self.participant_user,
            study=self.study,
            assigned_group='PDF'
        )
        
        self.exporter = ResearchDataExporter()
    
    def test_export_participants_json(self):
        """Test exporting participants to JSON"""
        response = self.exporter.export_participants(
            study_id=str(self.study.id),
            export_format='json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/json', response.get('Content-Type', ''))
    
    def test_export_participants_csv(self):
        """Test exporting participants to CSV"""
        response = self.exporter.export_participants(
            study_id=str(self.study.id),
            export_format='csv'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response.get('Content-Type', ''))
    
    def test_export_participants_xlsx(self):
        """Test exporting participants to Excel"""
        response = self.exporter.export_participants(
            study_id=str(self.study.id),
            export_format='xlsx'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('spreadsheet', response.get('Content-Type', ''))
    
    def test_export_interactions(self):
        """Test exporting interactions"""
        # Create test interaction
        InteractionLog.objects.create(
            participant=self.participant,
            session_id='test_session',
            log_type='button_click',
            event_data={'button_id': 'submit'}
        )
        
        response = self.exporter.export_interactions(
            study_id=str(self.study.id),
            export_format='json'
        )
        
        self.assertEqual(response.status_code, 200)
    
    def test_export_chat_interactions(self):
        """Test exporting chat interactions"""
        # Create test chat interaction
        ChatInteraction.objects.create(
            participant=self.participant,
            session_id='test_session',
            message_type='user_message',
            content='Test message'
        )
        
        response = self.exporter.export_chat_interactions(
            study_id=str(self.study.id),
            export_format='json'
        )
        
        self.assertEqual(response.status_code, 200)
    
    def test_export_full_dataset(self):
        """Test exporting full dataset"""
        # Create test data
        InteractionLog.objects.create(
            participant=self.participant,
            session_id='test_session',
            log_type='button_click',
            event_data={}
        )
        
        response = self.exporter.export_full_dataset(
            study_id=str(self.study.id),
            export_format='xlsx'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('spreadsheet', response.get('Content-Type', ''))
    
    def test_export_with_filters(self):
        """Test exporting with filters"""
        filters = {
            'assigned_group': 'PDF',
            'withdrawn': False
        }
        
        response = self.exporter.export_participants(
            study_id=str(self.study.id),
            export_format='json',
            filters=filters
        )
        
        self.assertEqual(response.status_code, 200)
    
    def test_unsupported_format(self):
        """Test exporting with unsupported format"""
        with self.assertRaises(ValueError):
            self.exporter.export_participants(
                study_id=str(self.study.id),
                export_format='xml'  # Unsupported format
            )