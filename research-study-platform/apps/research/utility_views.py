"""
Research utilities API views
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from .utilities import research_utilities
from .models import ResearchStudy
from django.contrib.auth import get_user_model

User = get_user_model()


def is_staff_user(user):
    """Check if user is staff/admin"""
    return user.is_staff or user.is_superuser


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def generate_participant_ids(request):
    """
    Generate participant IDs
    
    Expected payload:
    {
        "count": 10,
        "prefix": "P",
        "length": 8
    }
    """
    try:
        data = request.data
        count = data.get('count', 1)
        prefix = data.get('prefix', 'P')
        length = data.get('length', 8)
        
        if count <= 0 or count > 1000:
            return Response(
                {'error': 'Count must be between 1 and 1000'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate IDs
        participant_ids = []
        for i in range(count):
            participant_id = research_utilities.generate_participant_id(prefix, length)
            participant_ids.append(participant_id)
        
        return Response({
            'count': count,
            'prefix': prefix,
            'length': length,
            'participant_ids': participant_ids
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def assign_groups(request):
    """
    Assign groups to participants
    
    Expected payload:
    {
        "study_id": "uuid",
        "participant_count": 10,
        "method": "random" or "balanced",
        "group_ratios": {"PDF": 0.5, "CHATGPT": 0.5}
    }
    """
    try:
        data = request.data
        study_id = data.get('study_id')
        participant_count = data.get('participant_count', 1)
        method = data.get('method', 'balanced')
        group_ratios = data.get('group_ratios')
        
        if not study_id:
            return Response(
                {'error': 'study_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if method not in ['random', 'balanced']:
            return Response(
                {'error': 'method must be "random" or "balanced"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Assign groups
        if method == 'random':
            assignments = research_utilities.assign_group_random(
                study_id, participant_count, group_ratios
            )
        else:
            assignments = research_utilities.assign_group_balanced(
                study_id, participant_count
            )
        
        # Calculate distribution
        distribution = {}
        for group in assignments:
            distribution[group] = distribution.get(group, 0) + 1
        
        return Response({
            'study_id': study_id,
            'participant_count': participant_count,
            'method': method,
            'assignments': assignments,
            'distribution': distribution
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def bulk_generate_participants(request):
    """
    Bulk generate participants
    
    Expected payload:
    {
        "study_id": "uuid",
        "count": 50,
        "assignment_method": "balanced",
        "id_prefix": "P"
    }
    """
    try:
        data = request.data
        study_id = data.get('study_id')
        count = data.get('count', 10)
        assignment_method = data.get('assignment_method', 'balanced')
        id_prefix = data.get('id_prefix', 'P')
        
        if not study_id:
            return Response(
                {'error': 'study_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if count <= 0 or count > 1000:
            return Response(
                {'error': 'Count must be between 1 and 1000'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate participants
        result = research_utilities.bulk_generate_participants(
            study_id, count, assignment_method, id_prefix
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def validate_data_integrity(request):
    """
    Validate data integrity
    
    Query parameters:
    - study_id: Validate specific study (optional)
    """
    try:
        study_id = request.GET.get('study_id')
        
        validation_results = research_utilities.validate_data_integrity(study_id)
        
        return Response(validation_results, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def calculate_sample_size(request):
    """
    Calculate required sample size
    
    Expected payload:
    {
        "effect_size": 0.5,
        "alpha": 0.05,
        "power": 0.8,
        "two_tailed": true
    }
    """
    try:
        data = request.data
        effect_size = data.get('effect_size')
        alpha = data.get('alpha', 0.05)
        power = data.get('power', 0.8)
        two_tailed = data.get('two_tailed', True)
        
        if effect_size is None:
            return Response(
                {'error': 'effect_size is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if effect_size <= 0:
            return Response(
                {'error': 'effect_size must be positive'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sample_size = research_utilities.calculate_sample_size(
            effect_size, alpha, power, two_tailed
        )
        
        return Response({
            'effect_size': effect_size,
            'alpha': alpha,
            'power': power,
            'two_tailed': two_tailed,
            'sample_size_per_group': sample_size,
            'total_sample_size': sample_size * 2,
            'calculation_method': 'Two-sample t-test'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def estimate_study_duration(request):
    """
    Estimate study duration
    
    Expected payload:
    {
        "total_participants": 100,
        "enrollment_rate_per_day": 5,
        "avg_session_duration_hours": 1.5
    }
    """
    try:
        data = request.data
        total_participants = data.get('total_participants')
        enrollment_rate_per_day = data.get('enrollment_rate_per_day')
        avg_session_duration_hours = data.get('avg_session_duration_hours', 1.0)
        
        if total_participants is None:
            return Response(
                {'error': 'total_participants is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if enrollment_rate_per_day is None:
            return Response(
                {'error': 'enrollment_rate_per_day is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if total_participants <= 0:
            return Response(
                {'error': 'total_participants must be positive'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if enrollment_rate_per_day <= 0:
            return Response(
                {'error': 'enrollment_rate_per_day must be positive'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        estimation = research_utilities.estimate_study_duration(
            total_participants, enrollment_rate_per_day, avg_session_duration_hours
        )
        
        if 'error' in estimation:
            return Response(estimation, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(estimation, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def generate_study_summary(request):
    """
    Generate comprehensive study summary
    
    Query parameters:
    - study_id: Study identifier (required)
    """
    try:
        study_id = request.GET.get('study_id')
        
        if not study_id:
            return Response(
                {'error': 'study_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        summary = research_utilities.generate_study_summary(study_id)
        
        if 'success' in summary and not summary['success']:
            return Response(summary, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(summary, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def generate_randomization_seed(request):
    """
    Generate randomization seed for a participant
    
    Expected payload:
    {
        "study_id": "uuid",
        "participant_id": "P12345678"
    }
    """
    try:
        data = request.data
        study_id = data.get('study_id')
        participant_id = data.get('participant_id')
        
        if not study_id:
            return Response(
                {'error': 'study_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not participant_id:
            return Response(
                {'error': 'participant_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        seed = research_utilities.generate_randomization_seed(study_id, participant_id)
        
        return Response({
            'study_id': study_id,
            'participant_id': participant_id,
            'randomization_seed': seed
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def get_study_statistics(request):
    """
    Get basic statistics for all studies
    """
    try:
        studies = ResearchStudy.objects.filter(is_active=True)
        
        statistics = []
        for study in studies:
            summary = research_utilities.generate_study_summary(str(study.id))
            if 'success' not in summary or summary.get('success', True):
                statistics.append({
                    'study_id': str(study.id),
                    'study_name': study.name,
                    'total_participants': summary.get('participant_statistics', {}).get('total_participants', 0),
                    'completion_rate': summary.get('participant_statistics', {}).get('completion_rate', 0),
                    'created_at': study.created_at.isoformat(),
                    'is_active': study.is_active
                })
        
        return Response({
            'total_studies': len(statistics),
            'studies': statistics
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def get_available_groups(request):
    """
    Get available study groups
    
    Query parameters:
    - study_id: Get groups for specific study (optional)
    """
    try:
        study_id = request.GET.get('study_id')
        
        if study_id:
            try:
                study = ResearchStudy.objects.get(id=study_id)
                groups = list(study.group_balance_ratio.keys()) if study.group_balance_ratio else research_utilities.available_groups
            except ResearchStudy.DoesNotExist:
                return Response(
                    {'error': 'Study not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            groups = research_utilities.available_groups
        
        return Response({
            'study_id': study_id,
            'available_groups': groups
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )