"""
Unit tests for research models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import json

from apps.research.models import (
    ResearchStudy, ParticipantProfile, InteractionLog, ChatInteraction,
    PDFViewingBehavior, QuizResponse, DataExport, ResearcherAccess
)
from apps.studies.models import StudySession

User = get_user_model()


class ResearchStudyModelTest(TestCase):
    """Test ResearchStudy model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='researcher',
            email='researcher@test.com',
            participant_id='R001',
            study_group='PDF'
        )
        self.user.is_staff = True
        self.user.save()
    
    def test_create_research_study(self):
        """Test creating a research study"""
        study = ResearchStudy.objects.create(
            name='Test Study',
            description='A test study for unit testing',
            created_by=self.user,
            max_participants=100,
            group_balance_ratio={'PDF': 0.5, 'CHATGPT': 0.5}
        )
        
        self.assertEqual(study.name, 'Test Study')
        self.assertEqual(study.created_by, self.user)
        self.assertTrue(study.is_active)
        self.assertEqual(study.max_participants, 100)
        self.assertEqual(study.participant_count, 0)
        self.assertEqual(study.completion_rate, 0)
    
    def test_study_participant_count(self):
        """Test study participant count property"""
        study = ResearchStudy.objects.create(
            name='Test Study',
            description='Test',
            created_by=self.user
        )
        
        # Create participants
        for i in range(3):
            user = User.objects.create_user(
                username=f'participant{i}',
                email=f'participant{i}@test.com',
                participant_id=f'P{i:03d}',
                study_group='PDF'
            )
            ParticipantProfile.objects.create(
                user=user,
                study=study,
                assigned_group='PDF'
            )
        
        self.assertEqual(study.participant_count, 3)
    
    def test_study_completion_rate(self):
        """Test study completion rate calculation"""
        study = ResearchStudy.objects.create(
            name='Test Study',
            description='Test',
            created_by=self.user
        )
        
        # Create participants
        for i in range(4):
            user = User.objects.create_user(
                username=f'participant{i}',
                email=f'participant{i}@test.com',
                participant_id=f'P{i:03d}',
                study_group='PDF'
            )
            # Mark first 2 as completed
            if i < 2:
                user.study_completed = True
                user.save()
                
            ParticipantProfile.objects.create(
                user=user,
                study=study,
                assigned_group='PDF'
            )
        
        self.assertEqual(study.completion_rate, 50.0)


class ParticipantProfileModelTest(TestCase):
    """Test ParticipantProfile model"""
    
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
    
    def test_create_participant_profile(self):
        """Test creating a participant profile"""
        profile = ParticipantProfile.objects.create(
            user=self.participant_user,
            study=self.study,
            assigned_group='PDF',
            age_range='18-25',
            education_level='Bachelor',
            technical_background='Beginner'
        )
        
        self.assertEqual(profile.user, self.participant_user)
        self.assertEqual(profile.study, self.study)
        self.assertEqual(profile.assigned_group, 'PDF')
        self.assertIsNotNone(profile.anonymized_id)
        self.assertTrue(profile.anonymized_id.startswith('P'))
        self.assertEqual(len(profile.anonymized_id), 9)  # P + 8 chars
        self.assertFalse(profile.is_anonymized)
        self.assertFalse(profile.withdrawn)
    
    def test_anonymized_id_generation(self):
        """Test automatic anonymized ID generation"""
        profile = ParticipantProfile.objects.create(
            user=self.participant_user,
            study=self.study,
            assigned_group='PDF'
        )
        
        # Check that anonymized ID was generated
        self.assertIsNotNone(profile.anonymized_id)
        self.assertNotEqual(profile.anonymized_id, '')
        
        # Check uniqueness
        another_user = User.objects.create_user(
            username='participant2',
            email='participant2@test.com',
            participant_id='P002',
            study_group='PDF'
        )
        another_profile = ParticipantProfile.objects.create(
            user=another_user,
            study=self.study,
            assigned_group='PDF'
        )
        
        self.assertNotEqual(profile.anonymized_id, another_profile.anonymized_id)
    
    def test_randomization_seed_generation(self):
        """Test randomization seed generation"""
        profile = ParticipantProfile.objects.create(
            user=self.participant_user,
            study=self.study,
            assigned_group='PDF'
        )
        
        self.assertIsNotNone(profile.randomization_seed)
        self.assertEqual(len(profile.randomization_seed), 32)


class InteractionLogModelTest(TestCase):
    """Test InteractionLog model"""
    
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
    
    def test_create_interaction_log(self):
        """Test creating interaction log"""
        log = InteractionLog.objects.create(
            participant=self.participant,
            session_id='test_session_123',
            log_type='button_click',
            event_data={'button_id': 'submit_btn', 'page': 'quiz'},
            page_url='https://example.com/quiz',
            user_agent='Mozilla/5.0...',
            reaction_time_ms=1500
        )
        
        self.assertEqual(log.participant, self.participant)
        self.assertEqual(log.session_id, 'test_session_123')
        self.assertEqual(log.log_type, 'button_click')
        self.assertEqual(log.event_data['button_id'], 'submit_btn')
        self.assertEqual(log.reaction_time_ms, 1500)
        self.assertIsNotNone(log.timestamp)
    
    def test_interaction_log_ordering(self):
        """Test interaction log ordering"""
        # Create logs with different timestamps
        log1 = InteractionLog.objects.create(
            participant=self.participant,
            session_id='test_session',
            log_type='session_start',
            event_data={}
        )
        
        log2 = InteractionLog.objects.create(
            participant=self.participant,
            session_id='test_session',
            log_type='button_click',
            event_data={}
        )
        
        # Should be ordered by timestamp descending
        logs = InteractionLog.objects.all()
        self.assertEqual(logs[0], log2)
        self.assertEqual(logs[1], log1)


class ChatInteractionModelTest(TestCase):
    """Test ChatInteraction model"""
    
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
            study_group='CHATGPT'
        )
        
        self.participant = ParticipantProfile.objects.create(
            user=self.participant_user,
            study=self.study,
            assigned_group='CHATGPT'
        )
    
    def test_create_chat_interaction(self):
        """Test creating chat interaction"""
        chat = ChatInteraction.objects.create(
            participant=self.participant,
            session_id='test_session_123',
            message_type='user_message',
            content='What is machine learning?',
            response_time_ms=2000,
            token_count=150,
            cost_usd=0.003
        )
        
        self.assertEqual(chat.participant, self.participant)
        self.assertEqual(chat.message_type, 'user_message')
        self.assertEqual(chat.content, 'What is machine learning?')
        self.assertEqual(chat.token_count, 150)
        self.assertEqual(chat.cost_usd, 0.003)
        self.assertIsNotNone(chat.content_hash)
    
    def test_content_hash_generation(self):
        """Test content hash generation"""
        chat = ChatInteraction.objects.create(
            participant=self.participant,
            session_id='test_session',
            message_type='user_message',
            content='Test message'
        )
        
        self.assertIsNotNone(chat.content_hash)
        self.assertEqual(len(chat.content_hash), 64)  # SHA256 hash


class PDFViewingBehaviorModelTest(TestCase):
    """Test PDFViewingBehavior model"""
    
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
    
    def test_create_pdf_viewing_behavior(self):
        """Test creating PDF viewing behavior"""
        pdf_behavior = PDFViewingBehavior.objects.create(
            participant=self.participant,
            session_id='test_session_123',
            pdf_name='linux_tutorial.pdf',
            pdf_hash='abc123hash',
            page_number=5,
            time_spent_seconds=120,
            scroll_events=[
                {'timestamp': '2024-01-01T10:00:00Z', 'scroll_y': 100},
                {'timestamp': '2024-01-01T10:00:05Z', 'scroll_y': 200}
            ],
            zoom_events=[
                {'timestamp': '2024-01-01T10:00:10Z', 'zoom_level': 1.5}
            ],
            search_queries=['linux commands', 'file permissions']
        )
        
        self.assertEqual(pdf_behavior.participant, self.participant)
        self.assertEqual(pdf_behavior.pdf_name, 'linux_tutorial.pdf')
        self.assertEqual(pdf_behavior.page_number, 5)
        self.assertEqual(pdf_behavior.time_spent_seconds, 120)
        self.assertEqual(len(pdf_behavior.scroll_events), 2)
        self.assertEqual(len(pdf_behavior.zoom_events), 1)
        self.assertEqual(len(pdf_behavior.search_queries), 2)
    
    def test_pdf_unique_constraint(self):
        """Test unique constraint on participant, session, PDF, and page"""
        # Create first PDF behavior
        PDFViewingBehavior.objects.create(
            participant=self.participant,
            session_id='test_session',
            pdf_name='test.pdf',
            pdf_hash='hash123',
            page_number=1,
            time_spent_seconds=60
        )
        
        # Creating another with same participant, session, PDF, and page should be allowed
        # as the unique constraint is on all four fields together
        pdf_behavior2 = PDFViewingBehavior.objects.create(
            participant=self.participant,
            session_id='test_session',
            pdf_name='test.pdf',
            pdf_hash='hash123',
            page_number=2,  # Different page
            time_spent_seconds=30
        )
        
        self.assertEqual(pdf_behavior2.page_number, 2)


class QuizResponseModelTest(TestCase):
    """Test QuizResponse model"""
    
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
    
    def test_create_quiz_response(self):
        """Test creating quiz response"""
        response = QuizResponse.objects.create(
            participant=self.participant,
            session_id='test_session_123',
            quiz_type='pre_quiz',
            question_id='q1',
            question_text='What is the command to list files?',
            question_type='multiple_choice',
            response_value='ls',
            response_text='',
            is_correct=True,
            first_viewed_at=timezone.now(),
            time_spent_seconds=30,
            changes_made=1
        )
        
        self.assertEqual(response.participant, self.participant)
        self.assertEqual(response.quiz_type, 'pre_quiz')
        self.assertEqual(response.question_id, 'q1')
        self.assertEqual(response.response_value, 'ls')
        self.assertTrue(response.is_correct)
        self.assertEqual(response.time_spent_seconds, 30)
        self.assertEqual(response.changes_made, 1)
    
    def test_quiz_response_unique_constraint(self):
        """Test unique constraint on participant, session, quiz type, and question"""
        # Create first response
        QuizResponse.objects.create(
            participant=self.participant,
            session_id='test_session',
            quiz_type='pre_quiz',
            question_id='q1',
            question_text='Test question',
            question_type='multiple_choice',
            response_value='answer1',
            first_viewed_at=timezone.now()
        )
        
        # Creating another with same participant, session, quiz type, and question
        # should raise an IntegrityError due to unique constraint
        with self.assertRaises(Exception):
            QuizResponse.objects.create(
                participant=self.participant,
                session_id='test_session',
                quiz_type='pre_quiz',
                question_id='q1',
                question_text='Test question',
                question_type='multiple_choice',
                response_value='answer2',
                first_viewed_at=timezone.now()
            )


class DataExportModelTest(TestCase):
    """Test DataExport model"""
    
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
    
    def test_create_data_export(self):
        """Test creating data export record"""
        export = DataExport.objects.create(
            requested_by=self.researcher,
            study=self.study,
            export_type='participant_data',
            export_format='csv',
            filters={'date_range_start': '2024-01-01'},
            status='pending'
        )
        
        self.assertEqual(export.requested_by, self.researcher)
        self.assertEqual(export.study, self.study)
        self.assertEqual(export.export_type, 'participant_data')
        self.assertEqual(export.export_format, 'csv')
        self.assertEqual(export.status, 'pending')
        self.assertEqual(export.download_count, 0)
    
    def test_export_status_choices(self):
        """Test export status choices"""
        export = DataExport.objects.create(
            requested_by=self.researcher,
            study=self.study,
            export_type='full_dataset',
            export_format='xlsx'
        )
        
        # Test status transitions
        export.status = 'processing'
        export.save()
        self.assertEqual(export.status, 'processing')
        
        export.status = 'completed'
        export.exported_at = timezone.now()
        export.save()
        self.assertEqual(export.status, 'completed')
        self.assertIsNotNone(export.exported_at)


class ResearcherAccessModelTest(TestCase):
    """Test ResearcherAccess model"""
    
    def setUp(self):
        self.researcher1 = User.objects.create_user(
            username='researcher1',
            email='researcher1@test.com',
            participant_id='R001',
            study_group='PDF'
        )
        self.researcher1.is_staff = True
        self.researcher1.save()
        
        self.researcher2 = User.objects.create_user(
            username='researcher2',
            email='researcher2@test.com',
            participant_id='R002',
            study_group='PDF'
        )
        self.researcher2.is_staff = True
        self.researcher2.save()
        
        self.study = ResearchStudy.objects.create(
            name='Test Study',
            description='Test',
            created_by=self.researcher1
        )
    
    def test_create_researcher_access(self):
        """Test creating researcher access record"""
        access = ResearcherAccess.objects.create(
            user=self.researcher2,
            study=self.study,
            permission_level='view',
            granted_by=self.researcher1
        )
        
        self.assertEqual(access.user, self.researcher2)
        self.assertEqual(access.study, self.study)
        self.assertEqual(access.permission_level, 'view')
        self.assertEqual(access.granted_by, self.researcher1)
        self.assertEqual(access.access_count, 0)
    
    def test_researcher_access_unique_constraint(self):
        """Test unique constraint on user and study"""
        # Create first access record
        ResearcherAccess.objects.create(
            user=self.researcher2,
            study=self.study,
            permission_level='view',
            granted_by=self.researcher1
        )
        
        # Creating another with same user and study should raise an IntegrityError
        with self.assertRaises(Exception):
            ResearcherAccess.objects.create(
                user=self.researcher2,
                study=self.study,
                permission_level='export',
                granted_by=self.researcher1
            )


class ModelRelationshipTest(TestCase):
    """Test model relationships and cascading"""
    
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
    
    def test_participant_cascade_delete(self):
        """Test cascading delete when participant is deleted"""
        # Create related objects
        InteractionLog.objects.create(
            participant=self.participant,
            session_id='test_session',
            log_type='session_start',
            event_data={}
        )
        
        ChatInteraction.objects.create(
            participant=self.participant,
            session_id='test_session',
            message_type='user_message',
            content='Test message'
        )
        
        # Delete participant
        participant_id = self.participant.id
        self.participant.delete()
        
        # Check that related objects are deleted
        self.assertEqual(InteractionLog.objects.filter(participant_id=participant_id).count(), 0)
        self.assertEqual(ChatInteraction.objects.filter(participant_id=participant_id).count(), 0)
    
    def test_study_cascade_delete(self):
        """Test cascading delete when study is deleted"""
        # Create related objects
        DataExport.objects.create(
            requested_by=self.researcher,
            study=self.study,
            export_type='participant_data',
            export_format='csv'
        )
        
        # Delete study
        study_id = self.study.id
        self.study.delete()
        
        # Check that participants and exports are deleted
        self.assertEqual(ParticipantProfile.objects.filter(study_id=study_id).count(), 0)
        self.assertEqual(DataExport.objects.filter(study_id=study_id).count(), 0)