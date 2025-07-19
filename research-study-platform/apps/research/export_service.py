"""
Enhanced data export service for research data
Supports multiple formats and comprehensive data filtering
"""

import csv
import json
import io
import xlsxwriter
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum
from django.contrib.auth import get_user_model
from .models import (
    ResearchStudy, ParticipantProfile, InteractionLog, ChatInteraction,
    PDFViewingBehavior, QuizResponse, DataExport
)
from apps.studies.models import StudySession
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class ResearchDataExporter:
    """Comprehensive data export service"""
    
    def __init__(self):
        self.supported_formats = ['csv', 'json', 'xlsx']
        self.export_types = [
            'participants', 'interactions', 'chat_interactions',
            'pdf_behaviors', 'quiz_responses', 'session_data', 'full_dataset'
        ]
    
    def export_participants(self, study_id: str = None, export_format: str = 'csv',
                           filters: Dict[str, Any] = None) -> HttpResponse:
        """
        Export participant data
        
        Args:
            study_id: Filter by study ID
            export_format: Export format (csv, json, xlsx)
            filters: Additional filters
        
        Returns:
            HttpResponse: File download response
        """
        # Build queryset
        queryset = ParticipantProfile.objects.select_related('user', 'study')
        
        if study_id:
            queryset = queryset.filter(study_id=study_id)
        
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        # Get data
        participants_data = []
        for participant in queryset:
            # Get session data
            session = participant.user.study_sessions.first()
            last_activity = participant.interaction_logs.first()
            
            participants_data.append({
                'participant_id': participant.anonymized_id,
                'study_name': participant.study.name,
                'assigned_group': participant.assigned_group,
                'created_at': participant.created_at.isoformat(),
                'consent_given': participant.consent_given,
                'consent_timestamp': participant.consent_timestamp.isoformat() if participant.consent_timestamp else None,
                'gdpr_consent': participant.gdpr_consent,
                'data_processing_consent': participant.data_processing_consent,
                'withdrawn': participant.withdrawn,
                'withdrawal_timestamp': participant.withdrawal_timestamp.isoformat() if participant.withdrawal_timestamp else None,
                'withdrawal_reason': participant.withdrawal_reason,
                'is_anonymized': participant.is_anonymized,
                'age_range': participant.age_range,
                'education_level': participant.education_level,
                'technical_background': participant.technical_background,
                'consent_completed': participant.user.consent_completed,
                'pre_quiz_completed': participant.user.pre_quiz_completed,
                'interaction_completed': participant.user.interaction_completed,
                'post_quiz_completed': participant.user.post_quiz_completed,
                'study_completed': participant.user.study_completed,
                'completion_percentage': participant.user.completion_percentage,
                'session_id': session.session_id if session else None,
                'session_duration': session.total_duration if session else None,
                'interaction_duration': session.interaction_duration if session else None,
                'last_activity': last_activity.timestamp.isoformat() if last_activity else None,
                'total_interactions': participant.interaction_logs.count(),
                'chat_messages': participant.chat_interactions.count(),
                'pdf_views': participant.pdf_behaviors.count(),
                'quiz_responses': participant.quiz_responses.count(),
            })
        
        # Export in requested format
        if export_format == 'csv':
            return self._export_to_csv(participants_data, 'participants')
        elif export_format == 'json':
            return self._export_to_json(participants_data, 'participants')
        elif export_format == 'xlsx':
            return self._export_to_xlsx(participants_data, 'participants')
        else:
            raise ValueError(f"Unsupported format: {export_format}")
    
    def export_interactions(self, study_id: str = None, export_format: str = 'csv',
                           filters: Dict[str, Any] = None) -> HttpResponse:
        """Export interaction logs"""
        # Build queryset
        queryset = InteractionLog.objects.select_related('participant', 'participant__study')
        
        if study_id:
            queryset = queryset.filter(participant__study_id=study_id)
        
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        # Get data
        interactions_data = []
        for interaction in queryset:
            interactions_data.append({
                'participant_id': interaction.participant.anonymized_id,
                'study_name': interaction.participant.study.name,
                'session_id': interaction.session_id,
                'log_type': interaction.log_type,
                'timestamp': interaction.timestamp.isoformat(),
                'event_data': json.dumps(interaction.event_data),
                'page_url': interaction.page_url,
                'user_agent': interaction.user_agent,
                'screen_resolution': interaction.screen_resolution,
                'reaction_time_ms': interaction.reaction_time_ms,
                'time_since_last_action_ms': interaction.time_since_last_action_ms,
            })
        
        # Export in requested format
        if export_format == 'csv':
            return self._export_to_csv(interactions_data, 'interactions')
        elif export_format == 'json':
            return self._export_to_json(interactions_data, 'interactions')
        elif export_format == 'xlsx':
            return self._export_to_xlsx(interactions_data, 'interactions')
        else:
            raise ValueError(f"Unsupported format: {export_format}")
    
    def export_chat_interactions(self, study_id: str = None, export_format: str = 'csv',
                                filters: Dict[str, Any] = None) -> HttpResponse:
        """Export chat interactions"""
        # Build queryset
        queryset = ChatInteraction.objects.select_related('participant', 'participant__study')
        
        if study_id:
            queryset = queryset.filter(participant__study_id=study_id)
        
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        # Get data
        chat_data = []
        for chat in queryset:
            chat_data.append({
                'participant_id': chat.participant.anonymized_id,
                'study_name': chat.participant.study.name,
                'session_id': chat.session_id,
                'message_type': chat.message_type,
                'timestamp': chat.timestamp.isoformat(),
                'content': chat.content,
                'content_hash': chat.content_hash,
                'response_time_ms': chat.response_time_ms,
                'token_count': chat.token_count,
                'cost_usd': float(chat.cost_usd) if chat.cost_usd else None,
            })
        
        # Export in requested format
        if export_format == 'csv':
            return self._export_to_csv(chat_data, 'chat_interactions')
        elif export_format == 'json':
            return self._export_to_json(chat_data, 'chat_interactions')
        elif export_format == 'xlsx':
            return self._export_to_xlsx(chat_data, 'chat_interactions')
        else:
            raise ValueError(f"Unsupported format: {export_format}")
    
    def export_pdf_behaviors(self, study_id: str = None, export_format: str = 'csv',
                            filters: Dict[str, Any] = None) -> HttpResponse:
        """Export PDF viewing behaviors"""
        # Build queryset
        queryset = PDFViewingBehavior.objects.select_related('participant', 'participant__study')
        
        if study_id:
            queryset = queryset.filter(participant__study_id=study_id)
        
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        # Get data
        pdf_data = []
        for pdf_behavior in queryset:
            pdf_data.append({
                'participant_id': pdf_behavior.participant.anonymized_id,
                'study_name': pdf_behavior.participant.study.name,
                'session_id': pdf_behavior.session_id,
                'pdf_name': pdf_behavior.pdf_name,
                'pdf_hash': pdf_behavior.pdf_hash,
                'page_number': pdf_behavior.page_number,
                'time_spent_seconds': pdf_behavior.time_spent_seconds,
                'first_viewed_at': pdf_behavior.first_viewed_at.isoformat(),
                'last_viewed_at': pdf_behavior.last_viewed_at.isoformat(),
                'scroll_events': json.dumps(pdf_behavior.scroll_events),
                'zoom_events': json.dumps(pdf_behavior.zoom_events),
                'search_queries': json.dumps(pdf_behavior.search_queries),
            })
        
        # Export in requested format
        if export_format == 'csv':
            return self._export_to_csv(pdf_data, 'pdf_behaviors')
        elif export_format == 'json':
            return self._export_to_json(pdf_data, 'pdf_behaviors')
        elif export_format == 'xlsx':
            return self._export_to_xlsx(pdf_data, 'pdf_behaviors')
        else:
            raise ValueError(f"Unsupported format: {export_format}")
    
    def export_quiz_responses(self, study_id: str = None, export_format: str = 'csv',
                             filters: Dict[str, Any] = None) -> HttpResponse:
        """Export quiz responses"""
        # Build queryset
        queryset = QuizResponse.objects.select_related('participant', 'participant__study')
        
        if study_id:
            queryset = queryset.filter(participant__study_id=study_id)
        
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        # Get data
        quiz_data = []
        for quiz_response in queryset:
            quiz_data.append({
                'participant_id': quiz_response.participant.anonymized_id,
                'study_name': quiz_response.participant.study.name,
                'session_id': quiz_response.session_id,
                'quiz_type': quiz_response.quiz_type,
                'question_id': quiz_response.question_id,
                'question_text': quiz_response.question_text,
                'question_type': quiz_response.question_type,
                'response_value': json.dumps(quiz_response.response_value),
                'response_text': quiz_response.response_text,
                'is_correct': quiz_response.is_correct,
                'first_viewed_at': quiz_response.first_viewed_at.isoformat(),
                'submitted_at': quiz_response.submitted_at.isoformat(),
                'time_spent_seconds': quiz_response.time_spent_seconds,
                'changes_made': quiz_response.changes_made,
            })
        
        # Export in requested format
        if export_format == 'csv':
            return self._export_to_csv(quiz_data, 'quiz_responses')
        elif export_format == 'json':
            return self._export_to_json(quiz_data, 'quiz_responses')
        elif export_format == 'xlsx':
            return self._export_to_xlsx(quiz_data, 'quiz_responses')
        else:
            raise ValueError(f"Unsupported format: {export_format}")
    
    def export_full_dataset(self, study_id: str = None, export_format: str = 'xlsx',
                           filters: Dict[str, Any] = None) -> HttpResponse:
        """Export complete dataset with all data types"""
        if export_format != 'xlsx':
            raise ValueError("Full dataset export only supports xlsx format")
        
        # Create Excel file in memory
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        
        # Add worksheets for each data type
        self._add_participants_worksheet(workbook, study_id, filters)
        self._add_interactions_worksheet(workbook, study_id, filters)
        self._add_chat_worksheet(workbook, study_id, filters)
        self._add_pdf_worksheet(workbook, study_id, filters)
        self._add_quiz_worksheet(workbook, study_id, filters)
        self._add_summary_worksheet(workbook, study_id, filters)
        
        workbook.close()
        output.seek(0)
        
        # Create response
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        response['Content-Disposition'] = f'attachment; filename="research_data_{timestamp}.xlsx"'
        
        return response
    
    def _export_to_csv(self, data: List[Dict], filename: str) -> HttpResponse:
        """Export data to CSV format"""
        if not data:
            # Return empty CSV
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
            return response
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        
        writer = csv.DictWriter(response, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        return response
    
    def _export_to_json(self, data: List[Dict], filename: str) -> HttpResponse:
        """Export data to JSON format"""
        response = JsonResponse(data, safe=False)
        response['Content-Disposition'] = f'attachment; filename="{filename}.json"'
        return response
    
    def _export_to_xlsx(self, data: List[Dict], filename: str) -> HttpResponse:
        """Export data to Excel format"""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet(filename)
        
        if data:
            # Write headers
            headers = list(data[0].keys())
            for col, header in enumerate(headers):
                worksheet.write(0, col, header)
            
            # Write data
            for row, item in enumerate(data, 1):
                for col, header in enumerate(headers):
                    worksheet.write(row, col, item.get(header, ''))
        
        workbook.close()
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
        
        return response
    
    def _add_participants_worksheet(self, workbook, study_id: str, filters: Dict[str, Any]):
        """Add participants worksheet to Excel file"""
        worksheet = workbook.add_worksheet('Participants')
        
        # Get participant data
        queryset = ParticipantProfile.objects.select_related('user', 'study')
        if study_id:
            queryset = queryset.filter(study_id=study_id)
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        # Headers
        headers = [
            'Participant ID', 'Study Name', 'Assigned Group', 'Created At',
            'Consent Given', 'Withdrawn', 'Completion %', 'Session Duration',
            'Total Interactions', 'Chat Messages', 'PDF Views', 'Quiz Responses'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        
        # Data
        for row, participant in enumerate(queryset, 1):
            session = participant.user.study_sessions.first()
            worksheet.write(row, 0, participant.anonymized_id)
            worksheet.write(row, 1, participant.study.name)
            worksheet.write(row, 2, participant.assigned_group)
            worksheet.write(row, 3, participant.created_at.isoformat())
            worksheet.write(row, 4, participant.consent_given)
            worksheet.write(row, 5, participant.withdrawn)
            worksheet.write(row, 6, participant.user.completion_percentage)
            worksheet.write(row, 7, session.total_duration if session else 0)
            worksheet.write(row, 8, participant.interaction_logs.count())
            worksheet.write(row, 9, participant.chat_interactions.count())
            worksheet.write(row, 10, participant.pdf_behaviors.count())
            worksheet.write(row, 11, participant.quiz_responses.count())
    
    def _add_interactions_worksheet(self, workbook, study_id: str, filters: Dict[str, Any]):
        """Add interactions worksheet to Excel file"""
        worksheet = workbook.add_worksheet('Interactions')
        
        # Get interaction data
        queryset = InteractionLog.objects.select_related('participant', 'participant__study')
        if study_id:
            queryset = queryset.filter(participant__study_id=study_id)
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        # Headers
        headers = [
            'Participant ID', 'Session ID', 'Log Type', 'Timestamp',
            'Reaction Time (ms)', 'Time Since Last Action (ms)', 'Page URL'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        
        # Data
        for row, interaction in enumerate(queryset, 1):
            worksheet.write(row, 0, interaction.participant.anonymized_id)
            worksheet.write(row, 1, interaction.session_id)
            worksheet.write(row, 2, interaction.log_type)
            worksheet.write(row, 3, interaction.timestamp.isoformat())
            worksheet.write(row, 4, interaction.reaction_time_ms or '')
            worksheet.write(row, 5, interaction.time_since_last_action_ms or '')
            worksheet.write(row, 6, interaction.page_url)
    
    def _add_chat_worksheet(self, workbook, study_id: str, filters: Dict[str, Any]):
        """Add chat interactions worksheet to Excel file"""
        worksheet = workbook.add_worksheet('Chat Interactions')
        
        # Get chat data
        queryset = ChatInteraction.objects.select_related('participant', 'participant__study')
        if study_id:
            queryset = queryset.filter(participant__study_id=study_id)
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        # Headers
        headers = [
            'Participant ID', 'Session ID', 'Message Type', 'Timestamp',
            'Content', 'Response Time (ms)', 'Token Count', 'Cost (USD)'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        
        # Data
        for row, chat in enumerate(queryset, 1):
            worksheet.write(row, 0, chat.participant.anonymized_id)
            worksheet.write(row, 1, chat.session_id)
            worksheet.write(row, 2, chat.message_type)
            worksheet.write(row, 3, chat.timestamp.isoformat())
            worksheet.write(row, 4, chat.content)
            worksheet.write(row, 5, chat.response_time_ms or '')
            worksheet.write(row, 6, chat.token_count or '')
            worksheet.write(row, 7, float(chat.cost_usd) if chat.cost_usd else '')
    
    def _add_pdf_worksheet(self, workbook, study_id: str, filters: Dict[str, Any]):
        """Add PDF behaviors worksheet to Excel file"""
        worksheet = workbook.add_worksheet('PDF Behaviors')
        
        # Get PDF data
        queryset = PDFViewingBehavior.objects.select_related('participant', 'participant__study')
        if study_id:
            queryset = queryset.filter(participant__study_id=study_id)
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        # Headers
        headers = [
            'Participant ID', 'Session ID', 'PDF Name', 'Page Number',
            'Time Spent (seconds)', 'First Viewed At', 'Last Viewed At',
            'Scroll Events Count', 'Zoom Events Count', 'Search Queries Count'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        
        # Data
        for row, pdf_behavior in enumerate(queryset, 1):
            worksheet.write(row, 0, pdf_behavior.participant.anonymized_id)
            worksheet.write(row, 1, pdf_behavior.session_id)
            worksheet.write(row, 2, pdf_behavior.pdf_name)
            worksheet.write(row, 3, pdf_behavior.page_number)
            worksheet.write(row, 4, pdf_behavior.time_spent_seconds)
            worksheet.write(row, 5, pdf_behavior.first_viewed_at.isoformat())
            worksheet.write(row, 6, pdf_behavior.last_viewed_at.isoformat())
            worksheet.write(row, 7, len(pdf_behavior.scroll_events))
            worksheet.write(row, 8, len(pdf_behavior.zoom_events))
            worksheet.write(row, 9, len(pdf_behavior.search_queries))
    
    def _add_quiz_worksheet(self, workbook, study_id: str, filters: Dict[str, Any]):
        """Add quiz responses worksheet to Excel file"""
        worksheet = workbook.add_worksheet('Quiz Responses')
        
        # Get quiz data
        queryset = QuizResponse.objects.select_related('participant', 'participant__study')
        if study_id:
            queryset = queryset.filter(participant__study_id=study_id)
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        # Headers
        headers = [
            'Participant ID', 'Session ID', 'Quiz Type', 'Question ID',
            'Question Text', 'Question Type', 'Response Value', 'Is Correct',
            'Time Spent (seconds)', 'Changes Made', 'Submitted At'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        
        # Data
        for row, quiz_response in enumerate(queryset, 1):
            worksheet.write(row, 0, quiz_response.participant.anonymized_id)
            worksheet.write(row, 1, quiz_response.session_id)
            worksheet.write(row, 2, quiz_response.quiz_type)
            worksheet.write(row, 3, quiz_response.question_id)
            worksheet.write(row, 4, quiz_response.question_text)
            worksheet.write(row, 5, quiz_response.question_type)
            worksheet.write(row, 6, str(quiz_response.response_value))
            worksheet.write(row, 7, quiz_response.is_correct or '')
            worksheet.write(row, 8, quiz_response.time_spent_seconds)
            worksheet.write(row, 9, quiz_response.changes_made)
            worksheet.write(row, 10, quiz_response.submitted_at.isoformat())
    
    def _add_summary_worksheet(self, workbook, study_id: str, filters: Dict[str, Any]):
        """Add summary statistics worksheet to Excel file"""
        worksheet = workbook.add_worksheet('Summary')
        
        # Get study data
        if study_id:
            study = ResearchStudy.objects.get(id=study_id)
            participants = ParticipantProfile.objects.filter(study=study)
        else:
            participants = ParticipantProfile.objects.all()
        
        # Calculate summary statistics
        total_participants = participants.count()
        completed_participants = participants.filter(user__study_completed=True).count()
        withdrawn_participants = participants.filter(withdrawn=True).count()
        completion_rate = (completed_participants / total_participants * 100) if total_participants > 0 else 0
        
        # Group distribution
        group_dist = participants.values('assigned_group').annotate(count=Count('id'))
        
        # Write summary data
        worksheet.write(0, 0, 'Summary Statistics')
        worksheet.write(2, 0, 'Total Participants')
        worksheet.write(2, 1, total_participants)
        worksheet.write(3, 0, 'Completed Participants')
        worksheet.write(3, 1, completed_participants)
        worksheet.write(4, 0, 'Withdrawn Participants')
        worksheet.write(4, 1, withdrawn_participants)
        worksheet.write(5, 0, 'Completion Rate (%)')
        worksheet.write(5, 1, completion_rate)
        
        # Group distribution
        worksheet.write(7, 0, 'Group Distribution')
        for i, group in enumerate(group_dist, 8):
            worksheet.write(i, 0, group['assigned_group'])
            worksheet.write(i, 1, group['count'])
    
    def _apply_filters(self, queryset, filters: Dict[str, Any]):
        """Apply filters to queryset"""
        if 'date_range_start' in filters:
            queryset = queryset.filter(created_at__gte=filters['date_range_start'])
        
        if 'date_range_end' in filters:
            queryset = queryset.filter(created_at__lte=filters['date_range_end'])
        
        if 'assigned_group' in filters:
            queryset = queryset.filter(assigned_group=filters['assigned_group'])
        
        if 'withdrawn' in filters:
            queryset = queryset.filter(withdrawn=filters['withdrawn'])
        
        if 'completed' in filters:
            queryset = queryset.filter(user__study_completed=filters['completed'])
        
        return queryset


# Global instance
research_exporter = ResearchDataExporter()