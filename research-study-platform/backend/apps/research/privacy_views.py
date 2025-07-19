"""
Privacy and GDPR compliance views
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import datetime
import json
from .privacy_service import privacy_service
from .models import ResearchStudy, ParticipantProfile
from django.contrib.auth import get_user_model

User = get_user_model()


def is_staff_user(user):
    """Check if user is staff/admin"""
    return user.is_staff or user.is_superuser


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def anonymize_participant(request):
    """
    Anonymize a participant's data
    
    Expected payload:
    {
        "participant_id": "P12345678",
        "reason": "GDPR Request"
    }
    """
    try:
        data = request.data
        participant_id = data.get('participant_id')
        reason = data.get('reason', 'GDPR Request')
        
        if not participant_id:
            return Response(
                {'error': 'participant_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = privacy_service.anonymize_participant(participant_id, reason)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def delete_participant_data(request):
    """
    Delete all data for a participant (Right to be Forgotten)
    
    Expected payload:
    {
        "participant_id": "P12345678",
        "reason": "GDPR Right to be Forgotten",
        "confirmation": "DELETE"
    }
    """
    try:
        data = request.data
        participant_id = data.get('participant_id')
        reason = data.get('reason', 'GDPR Right to be Forgotten')
        confirmation = data.get('confirmation')
        
        if not participant_id:
            return Response(
                {'error': 'participant_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if confirmation != 'DELETE':
            return Response(
                {'error': 'confirmation must be "DELETE" to proceed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = privacy_service.delete_participant_data(participant_id, reason)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def export_participant_data(request):
    """
    Export all data for a participant (Data Portability)
    
    Expected payload:
    {
        "participant_id": "P12345678",
        "format": "json"
    }
    """
    try:
        data = request.data
        participant_id = data.get('participant_id')
        export_format = data.get('format', 'json')
        
        if not participant_id:
            return Response(
                {'error': 'participant_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if export_format not in ['json', 'csv']:
            return Response(
                {'error': 'format must be "json" or "csv"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = privacy_service.export_participant_data(participant_id, export_format)
        
        if result['success']:
            # Return as downloadable file
            response = JsonResponse(result['data'], safe=False)
            response['Content-Disposition'] = f'attachment; filename="participant_{participant_id}_data.json"'
            return response
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def process_data_retention(request):
    """
    Process data retention policies
    
    Expected payload:
    {
        "study_id": "uuid",
        "dry_run": true
    }
    """
    try:
        data = request.data
        study_id = data.get('study_id')
        dry_run = data.get('dry_run', True)
        
        result = privacy_service.process_data_retention(study_id, dry_run)
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def generate_privacy_report(request):
    """
    Generate privacy compliance report
    
    Query parameters:
    - study_id: Report for specific study (optional)
    """
    try:
        study_id = request.GET.get('study_id')
        
        report = privacy_service.generate_privacy_report(study_id)
        
        return Response(report, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def get_gdpr_compliance_status(request):
    """
    Get GDPR compliance status for all studies
    """
    try:
        studies = ResearchStudy.objects.filter(is_active=True)
        
        compliance_data = []
        
        for study in studies:
            participants = ParticipantProfile.objects.filter(study=study)
            total_participants = participants.count()
            
            if total_participants == 0:
                continue
            
            # Calculate compliance metrics
            consented = participants.filter(consent_given=True).count()
            gdpr_consented = participants.filter(gdpr_consent=True).count()
            data_processing_consented = participants.filter(data_processing_consent=True).count()
            anonymized = participants.filter(is_anonymized=True).count()
            withdrawn = participants.filter(withdrawn=True).count()
            
            compliance_data.append({
                'study_id': str(study.id),
                'study_name': study.name,
                'total_participants': total_participants,
                'consent_rate': (consented / total_participants * 100) if total_participants > 0 else 0,
                'gdpr_consent_rate': (gdpr_consented / total_participants * 100) if total_participants > 0 else 0,
                'data_processing_consent_rate': (data_processing_consented / total_participants * 100) if total_participants > 0 else 0,
                'anonymization_rate': (anonymized / total_participants * 100) if total_participants > 0 else 0,
                'withdrawal_rate': (withdrawn / total_participants * 100) if total_participants > 0 else 0,
                'is_gdpr_compliant': gdpr_consented == total_participants,
                'is_data_processing_compliant': data_processing_consented == total_participants,
                'created_at': study.created_at.isoformat()
            })
        
        # Calculate overall compliance
        total_all_participants = sum(item['total_participants'] for item in compliance_data)
        total_gdpr_consented = sum(
            item['total_participants'] * item['gdpr_consent_rate'] / 100 
            for item in compliance_data
        )
        
        overall_compliance = {
            'total_studies': len(compliance_data),
            'total_participants': total_all_participants,
            'overall_gdpr_compliance_rate': (total_gdpr_consented / total_all_participants * 100) if total_all_participants > 0 else 0,
            'compliant_studies': sum(1 for item in compliance_data if item['is_gdpr_compliant']),
            'non_compliant_studies': sum(1 for item in compliance_data if not item['is_gdpr_compliant']),
            'generated_at': datetime.now().isoformat()
        }
        
        return Response({
            'overall_compliance': overall_compliance,
            'studies': compliance_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def get_participant_privacy_status(request):
    """
    Get privacy status for a specific participant
    
    Query parameters:
    - participant_id: Participant's anonymized ID
    """
    try:
        participant_id = request.GET.get('participant_id')
        
        if not participant_id:
            return Response(
                {'error': 'participant_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            participant = ParticipantProfile.objects.get(anonymized_id=participant_id)
        except ParticipantProfile.DoesNotExist:
            return Response(
                {'error': 'Participant not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get privacy status
        privacy_status = {
            'participant_id': participant.anonymized_id,
            'study_name': participant.study.name,
            'consent_given': participant.consent_given,
            'consent_timestamp': participant.consent_timestamp.isoformat() if participant.consent_timestamp else None,
            'gdpr_consent': participant.gdpr_consent,
            'data_processing_consent': participant.data_processing_consent,
            'is_anonymized': participant.is_anonymized,
            'withdrawn': participant.withdrawn,
            'withdrawal_timestamp': participant.withdrawal_timestamp.isoformat() if participant.withdrawal_timestamp else None,
            'withdrawal_reason': participant.withdrawal_reason,
            'created_at': participant.created_at.isoformat(),
            'last_activity': None,
            'data_summary': {
                'total_interactions': participant.interaction_logs.count(),
                'chat_messages': participant.chat_interactions.count(),
                'pdf_views': participant.pdf_behaviors.count(),
                'quiz_responses': participant.quiz_responses.count(),
                'sessions': participant.user.study_sessions.count()
            }
        }
        
        # Get last activity
        last_interaction = participant.interaction_logs.first()
        if last_interaction:
            privacy_status['last_activity'] = last_interaction.timestamp.isoformat()
        
        return Response(privacy_status, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def bulk_anonymize_participants(request):
    """
    Bulk anonymize multiple participants
    
    Expected payload:
    {
        "participant_ids": ["P12345678", "P87654321"],
        "reason": "Bulk GDPR Request"
    }
    """
    try:
        data = request.data
        participant_ids = data.get('participant_ids', [])
        reason = data.get('reason', 'Bulk GDPR Request')
        
        if not participant_ids:
            return Response(
                {'error': 'participant_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(participant_ids, list):
            return Response(
                {'error': 'participant_ids must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = {
            'total_requested': len(participant_ids),
            'successful': [],
            'failed': [],
            'reason': reason,
            'processed_at': datetime.now().isoformat()
        }
        
        for participant_id in participant_ids:
            result = privacy_service.anonymize_participant(participant_id, reason)
            
            if result['success']:
                results['successful'].append({
                    'participant_id': participant_id,
                    'anonymized_at': result['anonymized_at']
                })
            else:
                results['failed'].append({
                    'participant_id': participant_id,
                    'error': result['error']
                })
        
        return Response(results, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def get_data_retention_candidates(request):
    """
    Get participants eligible for data retention processing
    
    Query parameters:
    - study_id: Filter by study ID (optional)
    - days: Override retention days (optional)
    """
    try:
        study_id = request.GET.get('study_id')
        days = int(request.GET.get('days', 2555))  # Default 7 years
        
        from datetime import timedelta
        from django.utils import timezone
        
        # Calculate retention cutoff
        retention_cutoff = timezone.now() - timedelta(days=days)
        
        # Get eligible participants
        participants = ParticipantProfile.objects.filter(
            created_at__lt=retention_cutoff,
            is_anonymized=False
        )
        
        if study_id:
            participants = participants.filter(study_id=study_id)
        
        # Prepare data
        candidates = []
        for participant in participants:
            last_activity = participant.interaction_logs.first()
            
            candidates.append({
                'participant_id': participant.anonymized_id,
                'study_name': participant.study.name,
                'created_at': participant.created_at.isoformat(),
                'days_since_created': (timezone.now() - participant.created_at).days,
                'last_activity': last_activity.timestamp.isoformat() if last_activity else None,
                'consent_given': participant.consent_given,
                'withdrawn': participant.withdrawn,
                'data_counts': {
                    'interactions': participant.interaction_logs.count(),
                    'chat_messages': participant.chat_interactions.count(),
                    'pdf_views': participant.pdf_behaviors.count(),
                    'quiz_responses': participant.quiz_responses.count()
                }
            })
        
        return Response({
            'retention_policy_days': days,
            'retention_cutoff': retention_cutoff.isoformat(),
            'candidates_count': len(candidates),
            'candidates': candidates
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )