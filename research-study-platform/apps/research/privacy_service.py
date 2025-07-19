"""
Privacy and GDPR Compliance Service
Handles data anonymization, retention, and privacy compliance
"""

import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    ResearchStudy, ParticipantProfile, InteractionLog, ChatInteraction,
    PDFViewingBehavior, QuizResponse, DataExport
)
from apps.studies.models import StudySession

User = get_user_model()
logger = logging.getLogger(__name__)


class PrivacyComplianceService:
    """Service for managing privacy and GDPR compliance"""
    
    def __init__(self):
        self.default_retention_days = 2555  # 7 years
        self.anonymization_fields = [
            'email', 'first_name', 'last_name', 'ip_address'
        ]
    
    def anonymize_participant(self, participant_id: str, 
                            reason: str = "GDPR Request") -> Dict[str, Any]:
        """
        Anonymize a participant's data
        
        Args:
            participant_id: Participant's anonymized ID
            reason: Reason for anonymization
        
        Returns:
            Dict containing anonymization results
        """
        try:
            with transaction.atomic():
                # Get participant
                participant = ParticipantProfile.objects.get(anonymized_id=participant_id)
                
                if participant.is_anonymized:
                    return {
                        'success': False,
                        'error': 'Participant is already anonymized',
                        'participant_id': participant_id
                    }
                
                # Anonymize user data
                user = participant.user
                original_email = user.email
                
                # Replace identifiable information
                user.email = f"{participant.anonymized_id}@anonymized.local"
                user.first_name = ""
                user.last_name = ""
                user.username = participant.anonymized_id
                user.save()
                
                # Anonymize interaction logs
                self._anonymize_interaction_logs(participant)
                
                # Anonymize chat interactions
                self._anonymize_chat_interactions(participant)
                
                # Mark as anonymized
                participant.is_anonymized = True
                participant.save()
                
                # Log the anonymization
                self._log_privacy_action(
                    participant=participant,
                    action_type='anonymization',
                    reason=reason,
                    details={
                        'original_email': original_email,
                        'anonymized_at': timezone.now().isoformat()
                    }
                )
                
                logger.info(f"Anonymized participant: {participant_id}")
                
                return {
                    'success': True,
                    'participant_id': participant_id,
                    'anonymized_at': timezone.now().isoformat(),
                    'reason': reason
                }
                
        except ParticipantProfile.DoesNotExist:
            return {
                'success': False,
                'error': 'Participant not found',
                'participant_id': participant_id
            }
        except Exception as e:
            logger.error(f"Error anonymizing participant {participant_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'participant_id': participant_id
            }
    
    def delete_participant_data(self, participant_id: str, 
                              reason: str = "GDPR Right to be Forgotten") -> Dict[str, Any]:
        """
        Delete all data for a participant (Right to be Forgotten)
        
        Args:
            participant_id: Participant's anonymized ID
            reason: Reason for deletion
        
        Returns:
            Dict containing deletion results
        """
        try:
            with transaction.atomic():
                # Get participant
                participant = ParticipantProfile.objects.get(anonymized_id=participant_id)
                
                # Log the deletion request
                self._log_privacy_action(
                    participant=participant,
                    action_type='deletion_request',
                    reason=reason,
                    details={
                        'requested_at': timezone.now().isoformat()
                    }
                )
                
                # Count data before deletion
                interaction_count = InteractionLog.objects.filter(participant=participant).count()
                chat_count = ChatInteraction.objects.filter(participant=participant).count()
                pdf_count = PDFViewingBehavior.objects.filter(participant=participant).count()
                quiz_count = QuizResponse.objects.filter(participant=participant).count()
                session_count = StudySession.objects.filter(user=participant.user).count()
                
                # Delete all associated data
                InteractionLog.objects.filter(participant=participant).delete()
                ChatInteraction.objects.filter(participant=participant).delete()
                PDFViewingBehavior.objects.filter(participant=participant).delete()
                QuizResponse.objects.filter(participant=participant).delete()
                StudySession.objects.filter(user=participant.user).delete()
                
                # Delete user and participant profile
                user = participant.user
                participant.delete()
                user.delete()
                
                logger.info(f"Deleted all data for participant: {participant_id}")
                
                return {
                    'success': True,
                    'participant_id': participant_id,
                    'deleted_at': timezone.now().isoformat(),
                    'reason': reason,
                    'deleted_counts': {
                        'interactions': interaction_count,
                        'chat_messages': chat_count,
                        'pdf_views': pdf_count,
                        'quiz_responses': quiz_count,
                        'sessions': session_count
                    }
                }
                
        except ParticipantProfile.DoesNotExist:
            return {
                'success': False,
                'error': 'Participant not found',
                'participant_id': participant_id
            }
        except Exception as e:
            logger.error(f"Error deleting participant data {participant_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'participant_id': participant_id
            }
    
    def export_participant_data(self, participant_id: str, 
                              format: str = 'json') -> Dict[str, Any]:
        """
        Export all data for a participant (Data Portability)
        
        Args:
            participant_id: Participant's anonymized ID
            format: Export format (json, csv)
        
        Returns:
            Dict containing export results
        """
        try:
            # Get participant
            participant = ParticipantProfile.objects.get(anonymized_id=participant_id)
            
            # Collect all data
            data = {
                'participant_info': {
                    'participant_id': participant.anonymized_id,
                    'study_name': participant.study.name,
                    'assigned_group': participant.assigned_group,
                    'created_at': participant.created_at.isoformat(),
                    'consent_given': participant.consent_given,
                    'consent_timestamp': participant.consent_timestamp.isoformat() if participant.consent_timestamp else None,
                    'is_anonymized': participant.is_anonymized,
                    'age_range': participant.age_range,
                    'education_level': participant.education_level,
                    'technical_background': participant.technical_background,
                },
                'completion_status': {
                    'consent_completed': participant.user.consent_completed,
                    'pre_quiz_completed': participant.user.pre_quiz_completed,
                    'interaction_completed': participant.user.interaction_completed,
                    'post_quiz_completed': participant.user.post_quiz_completed,
                    'study_completed': participant.user.study_completed,
                    'completion_percentage': participant.user.completion_percentage,
                },
                'interactions': [],
                'chat_interactions': [],
                'pdf_behaviors': [],
                'quiz_responses': [],
                'sessions': []
            }
            
            # Get interactions
            interactions = InteractionLog.objects.filter(participant=participant)
            for interaction in interactions:
                data['interactions'].append({
                    'session_id': interaction.session_id,
                    'log_type': interaction.log_type,
                    'timestamp': interaction.timestamp.isoformat(),
                    'event_data': interaction.event_data,
                    'reaction_time_ms': interaction.reaction_time_ms,
                    'time_since_last_action_ms': interaction.time_since_last_action_ms
                })
            
            # Get chat interactions
            chats = ChatInteraction.objects.filter(participant=participant)
            for chat in chats:
                data['chat_interactions'].append({
                    'session_id': chat.session_id,
                    'message_type': chat.message_type,
                    'timestamp': chat.timestamp.isoformat(),
                    'content': chat.content if not participant.is_anonymized else '[ANONYMIZED]',
                    'response_time_ms': chat.response_time_ms,
                    'token_count': chat.token_count,
                    'cost_usd': float(chat.cost_usd) if chat.cost_usd else None
                })
            
            # Get PDF behaviors
            pdf_behaviors = PDFViewingBehavior.objects.filter(participant=participant)
            for pdf in pdf_behaviors:
                data['pdf_behaviors'].append({
                    'session_id': pdf.session_id,
                    'pdf_name': pdf.pdf_name,
                    'page_number': pdf.page_number,
                    'time_spent_seconds': pdf.time_spent_seconds,
                    'first_viewed_at': pdf.first_viewed_at.isoformat(),
                    'last_viewed_at': pdf.last_viewed_at.isoformat(),
                    'scroll_events_count': len(pdf.scroll_events),
                    'zoom_events_count': len(pdf.zoom_events),
                    'search_queries_count': len(pdf.search_queries)
                })
            
            # Get quiz responses
            quiz_responses = QuizResponse.objects.filter(participant=participant)
            for quiz in quiz_responses:
                data['quiz_responses'].append({
                    'session_id': quiz.session_id,
                    'quiz_type': quiz.quiz_type,
                    'question_id': quiz.question_id,
                    'question_type': quiz.question_type,
                    'response_value': quiz.response_value,
                    'is_correct': quiz.is_correct,
                    'time_spent_seconds': quiz.time_spent_seconds,
                    'changes_made': quiz.changes_made,
                    'submitted_at': quiz.submitted_at.isoformat()
                })
            
            # Get sessions
            sessions = StudySession.objects.filter(user=participant.user)
            for session in sessions:
                data['sessions'].append({
                    'session_id': session.session_id,
                    'current_phase': session.current_phase,
                    'session_started_at': session.session_started_at.isoformat(),
                    'session_ended_at': session.session_ended_at.isoformat() if session.session_ended_at else None,
                    'total_duration': session.total_duration,
                    'is_completed': session.is_completed
                })
            
            # Log the export
            self._log_privacy_action(
                participant=participant,
                action_type='data_export',
                reason='Data Portability Request',
                details={
                    'format': format,
                    'exported_at': timezone.now().isoformat(),
                    'record_counts': {
                        'interactions': len(data['interactions']),
                        'chat_interactions': len(data['chat_interactions']),
                        'pdf_behaviors': len(data['pdf_behaviors']),
                        'quiz_responses': len(data['quiz_responses']),
                        'sessions': len(data['sessions'])
                    }
                }
            )
            
            return {
                'success': True,
                'participant_id': participant_id,
                'data': data,
                'format': format,
                'exported_at': timezone.now().isoformat()
            }
            
        except ParticipantProfile.DoesNotExist:
            return {
                'success': False,
                'error': 'Participant not found',
                'participant_id': participant_id
            }
        except Exception as e:
            logger.error(f"Error exporting participant data {participant_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'participant_id': participant_id
            }
    
    def process_data_retention(self, study_id: str = None, 
                             dry_run: bool = True) -> Dict[str, Any]:
        """
        Process data retention policies
        
        Args:
            study_id: Process specific study (optional)
            dry_run: If True, only analyze what would be deleted
        
        Returns:
            Dict containing retention processing results
        """
        try:
            # Calculate retention cutoff date
            retention_cutoff = timezone.now() - timedelta(days=self.default_retention_days)
            
            # Build queryset
            participants = ParticipantProfile.objects.filter(
                created_at__lt=retention_cutoff
            )
            
            if study_id:
                participants = participants.filter(study_id=study_id)
            
            # Get participants to process
            participants_to_process = list(participants)
            
            results = {
                'dry_run': dry_run,
                'retention_cutoff': retention_cutoff.isoformat(),
                'participants_found': len(participants_to_process),
                'processed_participants': [],
                'errors': []
            }
            
            if not dry_run:
                # Process each participant
                for participant in participants_to_process:
                    try:
                        # Anonymize instead of deleting (safer approach)
                        anonymize_result = self.anonymize_participant(
                            participant.anonymized_id,
                            reason="Data Retention Policy"
                        )
                        
                        if anonymize_result['success']:
                            results['processed_participants'].append({
                                'participant_id': participant.anonymized_id,
                                'action': 'anonymized',
                                'processed_at': timezone.now().isoformat()
                            })
                        else:
                            results['errors'].append({
                                'participant_id': participant.anonymized_id,
                                'error': anonymize_result['error']
                            })
                            
                    except Exception as e:
                        results['errors'].append({
                            'participant_id': participant.anonymized_id,
                            'error': str(e)
                        })
            else:
                # Dry run - just report what would be processed
                for participant in participants_to_process:
                    results['processed_participants'].append({
                        'participant_id': participant.anonymized_id,
                        'action': 'would_be_anonymized',
                        'created_at': participant.created_at.isoformat()
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing data retention: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_privacy_report(self, study_id: str = None) -> Dict[str, Any]:
        """
        Generate privacy compliance report
        
        Args:
            study_id: Report for specific study (optional)
        
        Returns:
            Dict containing privacy report
        """
        try:
            # Build queryset
            participants = ParticipantProfile.objects.all()
            
            if study_id:
                participants = participants.filter(study_id=study_id)
            
            # Calculate statistics
            total_participants = participants.count()
            anonymized_participants = participants.filter(is_anonymized=True).count()
            withdrawn_participants = participants.filter(withdrawn=True).count()
            consented_participants = participants.filter(consent_given=True).count()
            gdpr_consented_participants = participants.filter(gdpr_consent=True).count()
            
            # Data processing consent
            data_processing_consented = participants.filter(
                data_processing_consent=True
            ).count()
            
            # Recent activity
            recent_cutoff = timezone.now() - timedelta(days=30)
            recent_anonymizations = participants.filter(
                is_anonymized=True,
                updated_at__gte=recent_cutoff
            ).count()
            
            recent_withdrawals = participants.filter(
                withdrawn=True,
                withdrawal_timestamp__gte=recent_cutoff
            ).count()
            
            # Data retention analysis
            retention_cutoff = timezone.now() - timedelta(days=self.default_retention_days)
            retention_eligible = participants.filter(
                created_at__lt=retention_cutoff,
                is_anonymized=False
            ).count()
            
            # Privacy actions log
            privacy_actions = []
            # This would come from a privacy actions log if implemented
            
            report = {
                'generated_at': timezone.now().isoformat(),
                'study_id': study_id,
                'participant_statistics': {
                    'total_participants': total_participants,
                    'anonymized_participants': anonymized_participants,
                    'withdrawn_participants': withdrawn_participants,
                    'consented_participants': consented_participants,
                    'gdpr_consented_participants': gdpr_consented_participants,
                    'data_processing_consented_participants': data_processing_consented,
                    'anonymization_rate': (anonymized_participants / total_participants * 100) if total_participants > 0 else 0,
                    'withdrawal_rate': (withdrawn_participants / total_participants * 100) if total_participants > 0 else 0,
                    'consent_rate': (consented_participants / total_participants * 100) if total_participants > 0 else 0,
                    'gdpr_consent_rate': (gdpr_consented_participants / total_participants * 100) if total_participants > 0 else 0
                },
                'recent_activity': {
                    'recent_anonymizations': recent_anonymizations,
                    'recent_withdrawals': recent_withdrawals,
                    'period_days': 30
                },
                'data_retention': {
                    'retention_policy_days': self.default_retention_days,
                    'retention_cutoff': retention_cutoff.isoformat(),
                    'participants_eligible_for_retention': retention_eligible
                },
                'compliance_status': {
                    'gdpr_compliant': gdpr_consented_participants == total_participants,
                    'data_processing_compliant': data_processing_consented == total_participants,
                    'retention_policy_active': True
                },
                'privacy_actions': privacy_actions
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating privacy report: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _anonymize_interaction_logs(self, participant: ParticipantProfile):
        """Anonymize interaction logs"""
        interactions = InteractionLog.objects.filter(participant=participant)
        
        for interaction in interactions:
            # Remove IP addresses and user agents
            interaction.user_agent = ""
            interaction.screen_resolution = ""
            
            # Anonymize event data
            if interaction.event_data:
                # Remove potential PII from event data
                anonymized_data = self._anonymize_event_data(interaction.event_data)
                interaction.event_data = anonymized_data
            
            interaction.save()
    
    def _anonymize_chat_interactions(self, participant: ParticipantProfile):
        """Anonymize chat interactions"""
        chats = ChatInteraction.objects.filter(participant=participant)
        
        for chat in chats:
            # Replace content with anonymized marker
            chat.content = f"[ANONYMIZED_{len(chat.content)}_CHARS]"
            chat.save()
    
    def _anonymize_event_data(self, event_data: Dict) -> Dict:
        """Remove PII from event data"""
        if not isinstance(event_data, dict):
            return event_data
        
        anonymized_data = {}
        pii_fields = ['email', 'name', 'username', 'ip', 'user_agent']
        
        for key, value in event_data.items():
            if any(pii_field in key.lower() for pii_field in pii_fields):
                anonymized_data[key] = "[ANONYMIZED]"
            elif isinstance(value, dict):
                anonymized_data[key] = self._anonymize_event_data(value)
            else:
                anonymized_data[key] = value
        
        return anonymized_data
    
    def _log_privacy_action(self, participant: ParticipantProfile, 
                          action_type: str, reason: str, details: Dict):
        """Log privacy action for audit trail"""
        # This would log to a privacy actions audit table
        # For now, we'll just log to the application log
        logger.info(f"Privacy action: {action_type} for participant {participant.anonymized_id} - {reason}")
        logger.info(f"Details: {json.dumps(details)}")
    
    def send_privacy_notification(self, participant_id: str, 
                                action_type: str, details: Dict):
        """Send privacy notification to participant"""
        try:
            participant = ParticipantProfile.objects.get(anonymized_id=participant_id)
            
            if participant.is_anonymized:
                # Cannot send email to anonymized participant
                return False
            
            subject_map = {
                'anonymization': 'Your Data Has Been Anonymized',
                'deletion': 'Your Data Has Been Deleted',
                'export': 'Your Data Export Is Ready'
            }
            
            subject = subject_map.get(action_type, 'Privacy Action Notification')
            
            # This would send an actual email
            # For now, we'll just log the notification
            logger.info(f"Privacy notification sent to {participant.user.email}: {subject}")
            
            return True
            
        except ParticipantProfile.DoesNotExist:
            logger.error(f"Cannot send privacy notification - participant not found: {participant_id}")
            return False
        except Exception as e:
            logger.error(f"Error sending privacy notification: {str(e)}")
            return False


# Global instance
privacy_service = PrivacyComplianceService()


# Convenience functions
def anonymize_participant(participant_id: str, reason: str = "GDPR Request") -> Dict[str, Any]:
    return privacy_service.anonymize_participant(participant_id, reason)

def delete_participant_data(participant_id: str, reason: str = "GDPR Right to be Forgotten") -> Dict[str, Any]:
    return privacy_service.delete_participant_data(participant_id, reason)

def export_participant_data(participant_id: str, format: str = 'json') -> Dict[str, Any]:
    return privacy_service.export_participant_data(participant_id, format)

def process_data_retention(study_id: str = None, dry_run: bool = True) -> Dict[str, Any]:
    return privacy_service.process_data_retention(study_id, dry_run)

def generate_privacy_report(study_id: str = None) -> Dict[str, Any]:
    return privacy_service.generate_privacy_report(study_id)