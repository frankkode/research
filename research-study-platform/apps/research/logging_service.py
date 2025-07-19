"""
Research Data Logging Service
Comprehensive logging for all participant interactions and behaviors
"""

import logging
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import (
    ParticipantProfile, InteractionLog, ChatInteraction, 
    PDFViewingBehavior, QuizResponse
)

User = get_user_model()

logger = logging.getLogger(__name__)


class ResearchDataLogger:
    """Centralized logging service for research data collection"""
    
    def __init__(self):
        self.session_cache = {}
    
    def log_interaction(self, participant_id: str, session_id: str, 
                       log_type: str, event_data: Dict[str, Any],
                       page_url: str = None, user_agent: str = None,
                       reaction_time_ms: int = None) -> bool:
        """
        Log a general interaction event
        
        Args:
            participant_id: Anonymized participant ID
            session_id: Current session identifier
            log_type: Type of interaction (from InteractionLog.LOG_TYPES)
            event_data: Additional event data as JSON
            page_url: Current page URL
            user_agent: User's browser info
            reaction_time_ms: Time taken to react (optional)
        
        Returns:
            bool: Success status
        """
        try:
            participant = ParticipantProfile.objects.get(anonymized_id=participant_id)
            
            # Calculate time since last action
            time_since_last_action = self._calculate_time_since_last_action(
                participant, session_id
            )
            
            InteractionLog.objects.create(
                participant=participant,
                session_id=session_id,
                log_type=log_type,
                event_data=event_data,
                page_url=page_url or '',
                user_agent=user_agent or '',
                reaction_time_ms=reaction_time_ms,
                time_since_last_action_ms=time_since_last_action
            )
            
            logger.info(f"Logged interaction: {participant_id} - {log_type}")
            return True
            
        except ParticipantProfile.DoesNotExist:
            logger.error(f"Participant not found: {participant_id}")
            return False
        except Exception as e:
            logger.error(f"Error logging interaction: {str(e)}")
            return False
    
    def log_chat_interaction(self, participant_id: str, session_id: str,
                            message_type: str, content: str,
                            response_time_ms: int = None,
                            token_count: int = None,
                            cost_usd: float = None) -> bool:
        """
        Log ChatGPT interaction
        
        Args:
            participant_id: Anonymized participant ID
            session_id: Current session identifier
            message_type: Type of message (user_message, assistant_response, system_message)
            content: Message content
            response_time_ms: Time taken for response
            token_count: Number of tokens used
            cost_usd: Cost of the interaction
        
        Returns:
            bool: Success status
        """
        try:
            participant = ParticipantProfile.objects.get(anonymized_id=participant_id)
            
            # Create content hash for deduplication
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            ChatInteraction.objects.create(
                participant=participant,
                session_id=session_id,
                message_type=message_type,
                content=content,
                content_hash=content_hash,
                response_time_ms=response_time_ms,
                token_count=token_count,
                cost_usd=cost_usd
            )
            
            # Also log as general interaction
            self.log_interaction(
                participant_id=participant_id,
                session_id=session_id,
                log_type=f'chat_{message_type}',
                event_data={
                    'message_type': message_type,
                    'content_length': len(content),
                    'token_count': token_count,
                    'cost_usd': float(cost_usd) if cost_usd else None
                },
                reaction_time_ms=response_time_ms
            )
            
            logger.info(f"Logged chat interaction: {participant_id} - {message_type}")
            return True
            
        except ParticipantProfile.DoesNotExist:
            logger.error(f"Participant not found: {participant_id}")
            return False
        except Exception as e:
            logger.error(f"Error logging chat interaction: {str(e)}")
            return False
    
    def log_pdf_viewing(self, participant_id: str, session_id: str,
                       pdf_name: str, pdf_hash: str, page_number: int,
                       time_spent_seconds: int = 0,
                       scroll_events: List[Dict] = None,
                       zoom_events: List[Dict] = None,
                       search_queries: List[str] = None) -> bool:
        """
        Log PDF viewing behavior
        
        Args:
            participant_id: Anonymized participant ID
            session_id: Current session identifier
            pdf_name: Name of the PDF file
            pdf_hash: Hash of the PDF content
            page_number: Current page number
            time_spent_seconds: Time spent on this page
            scroll_events: List of scroll events
            zoom_events: List of zoom events
            search_queries: List of search queries
        
        Returns:
            bool: Success status
        """
        try:
            participant = ParticipantProfile.objects.get(anonymized_id=participant_id)
            
            # Get or create PDF viewing record
            pdf_behavior, created = PDFViewingBehavior.objects.get_or_create(
                participant=participant,
                session_id=session_id,
                pdf_name=pdf_name,
                page_number=page_number,
                defaults={
                    'pdf_hash': pdf_hash,
                    'time_spent_seconds': time_spent_seconds,
                    'scroll_events': scroll_events or [],
                    'zoom_events': zoom_events or [],
                    'search_queries': search_queries or []
                }
            )
            
            if not created:
                # Update existing record
                pdf_behavior.time_spent_seconds += time_spent_seconds
                if scroll_events:
                    pdf_behavior.scroll_events.extend(scroll_events)
                if zoom_events:
                    pdf_behavior.zoom_events.extend(zoom_events)
                if search_queries:
                    pdf_behavior.search_queries.extend(search_queries)
                pdf_behavior.save()
            
            # Log as general interaction
            self.log_interaction(
                participant_id=participant_id,
                session_id=session_id,
                log_type='pdf_page_viewed',
                event_data={
                    'pdf_name': pdf_name,
                    'page_number': page_number,
                    'time_spent_seconds': time_spent_seconds,
                    'has_scroll_events': bool(scroll_events),
                    'has_zoom_events': bool(zoom_events),
                    'has_search_queries': bool(search_queries)
                }
            )
            
            logger.info(f"Logged PDF viewing: {participant_id} - {pdf_name} p{page_number}")
            return True
            
        except ParticipantProfile.DoesNotExist:
            logger.error(f"Participant not found: {participant_id}")
            return False
        except Exception as e:
            logger.error(f"Error logging PDF viewing: {str(e)}")
            return False
    
    def log_quiz_response(self, participant_id: str, session_id: str,
                         quiz_type: str, question_id: str,
                         question_text: str, question_type: str,
                         response_value: Any, response_text: str = '',
                         is_correct: bool = None,
                         time_spent_seconds: int = 0,
                         changes_made: int = 0) -> bool:
        """
        Log quiz response
        
        Args:
            participant_id: Anonymized participant ID
            session_id: Current session identifier
            quiz_type: Type of quiz (pre_quiz, post_quiz)
            question_id: Unique question identifier
            question_text: The question text
            question_type: Type of question (multiple_choice, text, etc.)
            response_value: The response value (can be various types)
            response_text: Text response if applicable
            is_correct: Whether the response is correct
            time_spent_seconds: Time spent on this question
            changes_made: Number of times answer was changed
        
        Returns:
            bool: Success status
        """
        try:
            participant = ParticipantProfile.objects.get(anonymized_id=participant_id)
            
            QuizResponse.objects.create(
                participant=participant,
                session_id=session_id,
                quiz_type=quiz_type,
                question_id=question_id,
                question_text=question_text,
                question_type=question_type,
                response_value=response_value,
                response_text=response_text,
                is_correct=is_correct,
                first_viewed_at=timezone.now(),
                time_spent_seconds=time_spent_seconds,
                changes_made=changes_made
            )
            
            # Log as general interaction
            self.log_interaction(
                participant_id=participant_id,
                session_id=session_id,
                log_type='quiz_answer_submitted',
                event_data={
                    'quiz_type': quiz_type,
                    'question_id': question_id,
                    'question_type': question_type,
                    'is_correct': is_correct,
                    'time_spent_seconds': time_spent_seconds,
                    'changes_made': changes_made
                }
            )
            
            logger.info(f"Logged quiz response: {participant_id} - {quiz_type} Q{question_id}")
            return True
            
        except ParticipantProfile.DoesNotExist:
            logger.error(f"Participant not found: {participant_id}")
            return False
        except Exception as e:
            logger.error(f"Error logging quiz response: {str(e)}")
            return False
    
    def log_session_event(self, participant_id: str, session_id: str,
                         event_type: str, event_data: Dict[str, Any] = None) -> bool:
        """
        Log session-level events (start, end, phase transitions)
        
        Args:
            participant_id: Anonymized participant ID
            session_id: Current session identifier
            event_type: Type of session event
            event_data: Additional event data
        
        Returns:
            bool: Success status
        """
        session_events = {
            'session_start': 'session_start',
            'session_end': 'session_end',
            'phase_transition': 'phase_transition'
        }
        
        log_type = session_events.get(event_type, 'session_start')
        
        return self.log_interaction(
            participant_id=participant_id,
            session_id=session_id,
            log_type=log_type,
            event_data=event_data or {}
        )
    
    def log_navigation_event(self, participant_id: str, session_id: str,
                           from_page: str, to_page: str,
                           navigation_type: str = 'click') -> bool:
        """
        Log navigation between pages
        
        Args:
            participant_id: Anonymized participant ID
            session_id: Current session identifier
            from_page: Source page
            to_page: Destination page
            navigation_type: Type of navigation (click, back, forward, etc.)
        
        Returns:
            bool: Success status
        """
        return self.log_interaction(
            participant_id=participant_id,
            session_id=session_id,
            log_type='navigation',
            event_data={
                'from_page': from_page,
                'to_page': to_page,
                'navigation_type': navigation_type
            }
        )
    
    def log_error_event(self, participant_id: str, session_id: str,
                       error_type: str, error_message: str,
                       error_context: Dict[str, Any] = None) -> bool:
        """
        Log error events
        
        Args:
            participant_id: Anonymized participant ID
            session_id: Current session identifier
            error_type: Type of error
            error_message: Error message
            error_context: Additional error context
        
        Returns:
            bool: Success status
        """
        return self.log_interaction(
            participant_id=participant_id,
            session_id=session_id,
            log_type='error_occurred',
            event_data={
                'error_type': error_type,
                'error_message': error_message,
                'error_context': error_context or {}
            }
        )
    
    def _calculate_time_since_last_action(self, participant: ParticipantProfile,
                                        session_id: str) -> Optional[int]:
        """
        Calculate time since last action for the participant in this session
        
        Args:
            participant: ParticipantProfile instance
            session_id: Current session identifier
        
        Returns:
            Optional[int]: Time in milliseconds since last action
        """
        try:
            last_interaction = InteractionLog.objects.filter(
                participant=participant,
                session_id=session_id
            ).order_by('-timestamp').first()
            
            if last_interaction:
                time_diff = timezone.now() - last_interaction.timestamp
                return int(time_diff.total_seconds() * 1000)
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating time since last action: {str(e)}")
            return None
    
    def bulk_log_interactions(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bulk log multiple interactions for performance
        
        Args:
            interactions: List of interaction dictionaries
        
        Returns:
            Dict[str, Any]: Summary of results
        """
        results = {
            'success_count': 0,
            'error_count': 0,
            'errors': []
        }
        
        with transaction.atomic():
            for interaction in interactions:
                try:
                    success = self.log_interaction(**interaction)
                    if success:
                        results['success_count'] += 1
                    else:
                        results['error_count'] += 1
                        
                except Exception as e:
                    results['error_count'] += 1
                    results['errors'].append(str(e))
        
        return results
    
    def get_participant_session_summary(self, participant_id: str, 
                                      session_id: str) -> Dict[str, Any]:
        """
        Get summary of participant's session activity
        
        Args:
            participant_id: Anonymized participant ID
            session_id: Session identifier
        
        Returns:
            Dict[str, Any]: Session summary
        """
        try:
            participant = ParticipantProfile.objects.get(anonymized_id=participant_id)
            
            # Get all interactions for this session
            interactions = InteractionLog.objects.filter(
                participant=participant,
                session_id=session_id
            ).order_by('timestamp')
            
            if not interactions.exists():
                return {}
            
            # Calculate summary statistics
            first_interaction = interactions.first()
            last_interaction = interactions.last()
            session_duration = (last_interaction.timestamp - first_interaction.timestamp).total_seconds()
            
            # Count interactions by type
            interaction_counts = {}
            for interaction in interactions:
                interaction_counts[interaction.log_type] = interaction_counts.get(interaction.log_type, 0) + 1
            
            # Get chat statistics
            chat_messages = ChatInteraction.objects.filter(
                participant=participant,
                session_id=session_id
            ).count()
            
            # Get PDF statistics
            pdf_views = PDFViewingBehavior.objects.filter(
                participant=participant,
                session_id=session_id
            ).count()
            
            # Get quiz statistics
            quiz_responses = QuizResponse.objects.filter(
                participant=participant,
                session_id=session_id
            ).count()
            
            return {
                'session_id': session_id,
                'participant_id': participant_id,
                'session_duration_seconds': session_duration,
                'total_interactions': interactions.count(),
                'interaction_counts': interaction_counts,
                'chat_messages': chat_messages,
                'pdf_views': pdf_views,
                'quiz_responses': quiz_responses,
                'first_interaction': first_interaction.timestamp,
                'last_interaction': last_interaction.timestamp
            }
            
        except ParticipantProfile.DoesNotExist:
            logger.error(f"Participant not found: {participant_id}")
            return {}
        except Exception as e:
            logger.error(f"Error getting session summary: {str(e)}")
            return {}


# Global instance
research_logger = ResearchDataLogger()


# Convenience functions for easy import
def log_interaction(participant_id: str, session_id: str, log_type: str, 
                   event_data: Dict[str, Any], **kwargs) -> bool:
    return research_logger.log_interaction(participant_id, session_id, log_type, event_data, **kwargs)

def log_chat_interaction(participant_id: str, session_id: str, message_type: str, 
                        content: str, **kwargs) -> bool:
    return research_logger.log_chat_interaction(participant_id, session_id, message_type, content, **kwargs)

def log_pdf_viewing(participant_id: str, session_id: str, pdf_name: str, 
                   pdf_hash: str, page_number: int, **kwargs) -> bool:
    return research_logger.log_pdf_viewing(participant_id, session_id, pdf_name, pdf_hash, page_number, **kwargs)

def log_quiz_response(participant_id: str, session_id: str, quiz_type: str, 
                     question_id: str, question_text: str, question_type: str, 
                     response_value: Any, **kwargs) -> bool:
    return research_logger.log_quiz_response(participant_id, session_id, quiz_type, question_id, question_text, question_type, response_value, **kwargs)

def log_session_event(participant_id: str, session_id: str, event_type: str, 
                     event_data: Dict[str, Any] = None) -> bool:
    return research_logger.log_session_event(participant_id, session_id, event_type, event_data)

def log_navigation_event(participant_id: str, session_id: str, from_page: str, 
                        to_page: str, navigation_type: str = 'click') -> bool:
    return research_logger.log_navigation_event(participant_id, session_id, from_page, to_page, navigation_type)

def log_error_event(participant_id: str, session_id: str, error_type: str, 
                   error_message: str, error_context: Dict[str, Any] = None) -> bool:
    return research_logger.log_error_event(participant_id, session_id, error_type, error_message, error_context)