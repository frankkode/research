"""
API endpoint tests for research app
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
import json

from apps.research.models import (
    ResearchStudy, ParticipantProfile, InteractionLog, ChatInteraction,
    PDFViewingBehavior, QuizResponse, DataExport
)

User = get_user_model()


class ResearchStudyAPITest(APITestCase):
    """Test Research Study API endpoints"""
    
    def setUp(self):
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
        
        self.study = ResearchStudy.objects.create(
            name='Test Study',
            description='Test study for API testing',
            created_by=self.researcher,
            max_participants=100
        )
    
    def test_list_studies(self):
        """Test listing research studies"""
        url = reverse('researchstudy-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Study')
    
    def test_create_study(self):
        """Test creating a new research study"""
        url = reverse('researchstudy-list')
        data = {
            'name': 'New Study',
            'description': 'A new study for testing',
            'max_participants': 50,
            'group_balance_ratio': {'PDF': 0.5, 'CHATGPT': 0.5}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Study')
        self.assertEqual(response.data['created_by'], self.researcher.id)
    
    def test_get_study_analytics(self):
        """Test getting study analytics"""
        url = reverse('researchstudy-analytics', kwargs={'pk': self.study.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('study_overview', response.data)
        self.assertIn('participant_stats', response.data)
    
    def test_get_study_participants(self):
        """Test getting study participants"""
        # Create a participant
        participant_user = User.objects.create_user(
            username='participant',
            email='participant@test.com',
            participant_id='P001',
            study_group='PDF'
        )
        ParticipantProfile.objects.create(
            user=participant_user,
            study=self.study,
            assigned_group='PDF'
        )
        
        url = reverse('researchstudy-participants', kwargs={'pk': self.study.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['assigned_group'], 'PDF')
    
    def test_bulk_create_participants(self):
        """Test bulk creating participants"""
        url = reverse('researchstudy-bulk-create-participants', kwargs={'pk': self.study.id})
        data = {
            'participant_count': 5,
            'assignment_method': 'balanced',
            'id_prefix': 'T'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 5)
        
        # Check that participants were created
        self.assertEqual(ParticipantProfile.objects.filter(study=self.study).count(), 5)
    
    def test_unauthorized_access(self):
        """Test unauthorized access to study endpoints"""
        self.client.credentials()  # Remove authentication
        
        url = reverse('researchstudy-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ParticipantProfileAPITest(APITestCase):
    """Test Participant Profile API endpoints"""
    
    def setUp(self):
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
    
    def test_list_participants(self):
        """Test listing participant profiles"""
        url = reverse('participantprofile-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_filter_participants_by_study(self):
        """Test filtering participants by study"""
        url = reverse('participantprofile-list') + f'?study_id={self.study.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_participant(self):
        """Test creating a new participant"""
        url = reverse('participantprofile-create-participant')
        data = {
            'email': 'newparticipant@test.com',
            'participant_id': 'P002',
            'study_id': str(self.study.id),
            'assigned_group': 'CHATGPT'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['assigned_group'], 'CHATGPT')
        
        # Check that user was created
        self.assertTrue(User.objects.filter(participant_id='P002').exists())
    
    def test_withdraw_participant(self):
        """Test withdrawing a participant"""
        url = reverse('participantprofile-withdraw', kwargs={'pk': self.participant.id})
        data = {'reason': 'Participant requested withdrawal'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'withdrawn')
        
        # Check that participant was marked as withdrawn
        self.participant.refresh_from_db()
        self.assertTrue(self.participant.withdrawn)
        self.assertEqual(self.participant.withdrawal_reason, 'Participant requested withdrawal')
    
    def test_anonymize_participant(self):
        """Test anonymizing a participant"""
        url = reverse('participantprofile-anonymize', kwargs={'pk': self.participant.id})
        
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'anonymized')
        
        # Check that participant was anonymized
        self.participant.refresh_from_db()
        self.assertTrue(self.participant.is_anonymized)
    
    def test_get_interaction_summary(self):
        """Test getting participant interaction summary"""
        # Create some interactions
        InteractionLog.objects.create(
            participant=self.participant,
            session_id='test_session',
            log_type='session_start',
            event_data={}
        )
        
        url = reverse('participantprofile-interaction-summary', kwargs={'pk': self.participant.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_interactions'], 1)


class LoggingAPITest(APITestCase):
    """Test logging API endpoints"""
    
    def setUp(self):
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
    
    def test_log_interaction(self):
        """Test logging a general interaction"""
        url = reverse('log_interaction')
        data = {
            'participant_id': self.participant.anonymized_id,
            'session_id': 'test_session_123',
            'log_type': 'button_click',
            'event_data': {
                'button_id': 'submit_btn',
                'page': 'quiz'
            },
            'page_url': 'https://example.com/quiz',
            'reaction_time_ms': 1500
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'logged')
        
        # Check that interaction was logged
        self.assertTrue(InteractionLog.objects.filter(
            participant=self.participant,
            log_type='button_click'
        ).exists())
    
    def test_log_chat_interaction(self):
        """Test logging a chat interaction"""
        url = reverse('log_chat_interaction')
        data = {
            'participant_id': self.participant.anonymized_id,
            'session_id': 'test_session_123',
            'message_type': 'user_message',
            'content': 'What is machine learning?',
            'response_time_ms': 2000,
            'token_count': 150,
            'cost_usd': 0.003
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'logged')
        
        # Check that chat interaction was logged
        self.assertTrue(ChatInteraction.objects.filter(
            participant=self.participant,
            message_type='user_message'
        ).exists())
    
    def test_log_pdf_viewing(self):
        """Test logging PDF viewing behavior"""
        url = reverse('log_pdf_viewing')
        data = {
            'participant_id': self.participant.anonymized_id,
            'session_id': 'test_session_123',
            'pdf_name': 'linux_tutorial.pdf',
            'pdf_hash': 'abc123hash',
            'page_number': 5,
            'time_spent_seconds': 120,
            'scroll_events': [
                {'timestamp': '2024-01-01T10:00:00Z', 'scroll_y': 100}
            ]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'logged')
        
        # Check that PDF viewing was logged
        self.assertTrue(PDFViewingBehavior.objects.filter(
            participant=self.participant,
            pdf_name='linux_tutorial.pdf'
        ).exists())
    
    def test_log_quiz_response(self):
        """Test logging quiz response"""
        url = reverse('log_quiz_response')
        data = {
            'participant_id': self.participant.anonymized_id,
            'session_id': 'test_session_123',
            'quiz_type': 'pre_quiz',
            'question_id': 'q1',
            'question_text': 'What is the command to list files?',
            'question_type': 'multiple_choice',
            'response_value': 'ls',
            'is_correct': True,
            'time_spent_seconds': 30
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'logged')
        
        # Check that quiz response was logged
        self.assertTrue(QuizResponse.objects.filter(
            participant=self.participant,
            quiz_type='pre_quiz'
        ).exists())
    
    def test_bulk_log_interactions(self):
        """Test bulk logging interactions"""
        url = reverse('bulk_log_interactions')
        data = {
            'interactions': [
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
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success_count'], 2)
        self.assertEqual(response.data['error_count'], 0)
    
    def test_get_session_summary(self):
        """Test getting session summary"""
        # Create some interactions
        InteractionLog.objects.create(
            participant=self.participant,
            session_id='test_session',
            log_type='session_start',
            event_data={}
        )
        
        url = reverse('get_session_summary')
        response = self.client.get(url, {
            'participant_id': self.participant.anonymized_id,
            'session_id': 'test_session'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['participant_id'], self.participant.anonymized_id)
        self.assertEqual(response.data['session_id'], 'test_session')
    
    def test_invalid_participant_id(self):
        """Test logging with invalid participant ID"""
        url = reverse('log_interaction')
        data = {
            'participant_id': 'INVALID_ID',
            'session_id': 'test_session',
            'log_type': 'button_click',
            'event_data': {}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExportAPITest(APITestCase):
    """Test export API endpoints"""
    
    def setUp(self):
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
    
    def test_export_participants_enhanced(self):
        """Test enhanced participant export"""
        url = reverse('export_participants_enhanced')
        data = {
            'study_id': str(self.study.id),
            'format': 'json',
            'filters': {
                'assigned_group': 'PDF'
            }
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('attachment', response.get('Content-Disposition', ''))
    
    def test_export_full_dataset(self):
        """Test full dataset export"""
        url = reverse('export_full_dataset')
        data = {
            'study_id': str(self.study.id),
            'filters': {}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                      response.get('Content-Type', ''))
    
    def test_get_export_history(self):
        """Test getting export history"""
        # Create an export record
        DataExport.objects.create(
            requested_by=self.researcher,
            study=self.study,
            export_type='participant_data',
            export_format='csv',
            status='completed'
        )
        
        url = reverse('get_export_history')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['exports']), 1)
    
    def test_get_export_stats(self):
        """Test getting export statistics"""
        # Create export records
        DataExport.objects.create(
            requested_by=self.researcher,
            study=self.study,
            export_type='participant_data',
            export_format='csv',
            status='completed'
        )
        
        url = reverse('get_export_stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_exports'], 1)
        self.assertEqual(response.data['successful_exports'], 1)


class PrivacyAPITest(APITestCase):
    """Test privacy API endpoints"""
    
    def setUp(self):
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
    
    def test_anonymize_participant(self):
        """Test anonymizing a participant"""
        url = reverse('anonymize_participant')
        data = {
            'participant_id': self.participant.anonymized_id,
            'reason': 'GDPR Request'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Check that participant was anonymized
        self.participant.refresh_from_db()
        self.assertTrue(self.participant.is_anonymized)
    
    def test_export_participant_data(self):
        """Test exporting participant data"""
        url = reverse('export_participant_data')
        data = {
            'participant_id': self.participant.anonymized_id,
            'format': 'json'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('attachment', response.get('Content-Disposition', ''))
    
    def test_get_gdpr_compliance_status(self):
        """Test getting GDPR compliance status"""
        url = reverse('get_gdpr_compliance_status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('overall_compliance', response.data)
        self.assertIn('studies', response.data)
    
    def test_get_participant_privacy_status(self):
        """Test getting participant privacy status"""
        url = reverse('get_participant_privacy_status')
        response = self.client.get(url, {'participant_id': self.participant.anonymized_id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['participant_id'], self.participant.anonymized_id)
        self.assertIn('consent_given', response.data)
    
    def test_bulk_anonymize_participants(self):
        """Test bulk anonymizing participants"""
        # Create another participant
        participant_user2 = User.objects.create_user(
            username='participant2',
            email='participant2@test.com',
            participant_id='P002',
            study_group='PDF'
        )
        participant2 = ParticipantProfile.objects.create(
            user=participant_user2,
            study=self.study,
            assigned_group='PDF'
        )
        
        url = reverse('bulk_anonymize_participants')
        data = {
            'participant_ids': [
                self.participant.anonymized_id,
                participant2.anonymized_id
            ],
            'reason': 'Bulk GDPR Request'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_requested'], 2)
        self.assertEqual(len(response.data['successful']), 2)
        self.assertEqual(len(response.data['failed']), 0)


class UtilityAPITest(APITestCase):
    """Test utility API endpoints"""
    
    def setUp(self):
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
        
        self.study = ResearchStudy.objects.create(
            name='Test Study',
            description='Test',
            created_by=self.researcher
        )
    
    def test_generate_participant_ids(self):
        """Test generating participant IDs"""
        url = reverse('generate_participant_ids')
        data = {
            'count': 5,
            'prefix': 'T',
            'length': 6
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)
        self.assertEqual(len(response.data['participant_ids']), 5)
        
        # Check that all IDs have the correct prefix
        for participant_id in response.data['participant_ids']:
            self.assertTrue(participant_id.startswith('T'))
    
    def test_assign_groups(self):
        """Test group assignment"""
        url = reverse('assign_groups')
        data = {
            'study_id': str(self.study.id),
            'participant_count': 10,
            'method': 'balanced'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['participant_count'], 10)
        self.assertEqual(len(response.data['assignments']), 10)
    
    def test_calculate_sample_size(self):
        """Test sample size calculation"""
        url = reverse('calculate_sample_size')
        data = {
            'effect_size': 0.5,
            'alpha': 0.05,
            'power': 0.8,
            'two_tailed': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('sample_size_per_group', response.data)
        self.assertIn('total_sample_size', response.data)
    
    def test_estimate_study_duration(self):
        """Test study duration estimation"""
        url = reverse('estimate_study_duration')
        data = {
            'total_participants': 100,
            'enrollment_rate_per_day': 5,
            'avg_session_duration_hours': 1.5
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('estimated_enrollment_days', response.data)
        self.assertIn('estimated_completion_date', response.data)
    
    def test_validate_data_integrity(self):
        """Test data integrity validation"""
        url = reverse('validate_data_integrity')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('checks_performed', response.data)
        self.assertIn('issues_found', response.data)
        self.assertIn('statistics', response.data)
    
    def test_generate_study_summary(self):
        """Test study summary generation"""
        url = reverse('generate_study_summary')
        response = self.client.get(url, {'study_id': str(self.study.id)})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('participant_statistics', response.data)
        self.assertIn('data_collection', response.data)
        self.assertIn('study_configuration', response.data)
    
    def test_get_available_groups(self):
        """Test getting available groups"""
        url = reverse('get_available_groups')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('available_groups', response.data)
        self.assertIn('PDF', response.data['available_groups'])
        self.assertIn('CHATGPT', response.data['available_groups'])


class DashboardAPITest(APITestCase):
    """Test dashboard API endpoints"""
    
    def setUp(self):
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
        
        self.study = ResearchStudy.objects.create(
            name='Test Study',
            description='Test',
            created_by=self.researcher
        )
    
    def test_dashboard_overview(self):
        """Test dashboard overview endpoint"""
        url = reverse('dashboard-overview')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_studies', response.data)
        self.assertIn('total_participants', response.data)
        self.assertIn('completion_rate', response.data)
    
    def test_activity_timeline(self):
        """Test activity timeline endpoint"""
        url = reverse('dashboard-activity-timeline')
        response = self.client.get(url, {'days': 30})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('daily_registrations', response.data)
        self.assertIn('daily_completions', response.data)