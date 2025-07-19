"""
Enhanced export views using the new export service
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import json
from .export_service import research_exporter
from .models import ResearchStudy, DataExport
from django.contrib.auth import get_user_model

User = get_user_model()


def is_staff_user(user):
    """Check if user is staff/admin"""
    return user.is_staff or user.is_superuser


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def export_participants_enhanced(request):
    """
    Enhanced participant export with filtering options
    
    Expected payload:
    {
        "study_id": "uuid",
        "format": "csv|json|xlsx",
        "filters": {
            "date_range_start": "2024-01-01",
            "date_range_end": "2024-12-31",
            "assigned_group": "CHATGPT",
            "withdrawn": false,
            "completed": true
        }
    }
    """
    try:
        data = request.data
        study_id = data.get('study_id')
        export_format = data.get('format', 'csv')
        filters = data.get('filters', {})
        
        # Validate format
        if export_format not in ['csv', 'json', 'xlsx']:
            return Response(
                {'error': 'Invalid format. Supported formats: csv, json, xlsx'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate study if provided
        if study_id:
            try:
                study = ResearchStudy.objects.get(id=study_id)
            except ResearchStudy.DoesNotExist:
                return Response(
                    {'error': 'Study not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Create export record
        export_record = DataExport.objects.create(
            requested_by=request.user,
            study_id=study_id,
            export_type='participant_data',
            export_format=export_format,
            filters=filters
        )
        
        # Generate export
        try:
            response = research_exporter.export_participants(
                study_id=study_id,
                export_format=export_format,
                filters=filters
            )
            
            # Update export record
            export_record.status = 'completed'
            export_record.exported_at = datetime.now()
            export_record.save()
            
            return response
            
        except Exception as e:
            export_record.status = 'failed'
            export_record.save()
            raise e
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def export_interactions_enhanced(request):
    """
    Enhanced interaction export with filtering options
    
    Expected payload:
    {
        "study_id": "uuid",
        "format": "csv|json|xlsx",
        "filters": {
            "date_range_start": "2024-01-01",
            "date_range_end": "2024-12-31",
            "log_type": "chat_message_sent",
            "participant_id": "P12345678"
        }
    }
    """
    try:
        data = request.data
        study_id = data.get('study_id')
        export_format = data.get('format', 'csv')
        filters = data.get('filters', {})
        
        # Validate format
        if export_format not in ['csv', 'json', 'xlsx']:
            return Response(
                {'error': 'Invalid format. Supported formats: csv, json, xlsx'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create export record
        export_record = DataExport.objects.create(
            requested_by=request.user,
            study_id=study_id,
            export_type='interaction_logs',
            export_format=export_format,
            filters=filters
        )
        
        # Generate export
        try:
            response = research_exporter.export_interactions(
                study_id=study_id,
                export_format=export_format,
                filters=filters
            )
            
            # Update export record
            export_record.status = 'completed'
            export_record.exported_at = datetime.now()
            export_record.save()
            
            return response
            
        except Exception as e:
            export_record.status = 'failed'
            export_record.save()
            raise e
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def export_chat_interactions_enhanced(request):
    """
    Enhanced chat interaction export with filtering options
    """
    try:
        data = request.data
        study_id = data.get('study_id')
        export_format = data.get('format', 'csv')
        filters = data.get('filters', {})
        
        # Validate format
        if export_format not in ['csv', 'json', 'xlsx']:
            return Response(
                {'error': 'Invalid format. Supported formats: csv, json, xlsx'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create export record
        export_record = DataExport.objects.create(
            requested_by=request.user,
            study_id=study_id,
            export_type='chat_interactions',
            export_format=export_format,
            filters=filters
        )
        
        # Generate export
        try:
            response = research_exporter.export_chat_interactions(
                study_id=study_id,
                export_format=export_format,
                filters=filters
            )
            
            # Update export record
            export_record.status = 'completed'
            export_record.exported_at = datetime.now()
            export_record.save()
            
            return response
            
        except Exception as e:
            export_record.status = 'failed'
            export_record.save()
            raise e
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def export_pdf_behaviors_enhanced(request):
    """
    Enhanced PDF behavior export with filtering options
    """
    try:
        data = request.data
        study_id = data.get('study_id')
        export_format = data.get('format', 'csv')
        filters = data.get('filters', {})
        
        # Validate format
        if export_format not in ['csv', 'json', 'xlsx']:
            return Response(
                {'error': 'Invalid format. Supported formats: csv, json, xlsx'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create export record
        export_record = DataExport.objects.create(
            requested_by=request.user,
            study_id=study_id,
            export_type='pdf_behaviors',
            export_format=export_format,
            filters=filters
        )
        
        # Generate export
        try:
            response = research_exporter.export_pdf_behaviors(
                study_id=study_id,
                export_format=export_format,
                filters=filters
            )
            
            # Update export record
            export_record.status = 'completed'
            export_record.exported_at = datetime.now()
            export_record.save()
            
            return response
            
        except Exception as e:
            export_record.status = 'failed'
            export_record.save()
            raise e
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def export_quiz_responses_enhanced(request):
    """
    Enhanced quiz response export with filtering options
    """
    try:
        data = request.data
        study_id = data.get('study_id')
        export_format = data.get('format', 'csv')
        filters = data.get('filters', {})
        
        # Validate format
        if export_format not in ['csv', 'json', 'xlsx']:
            return Response(
                {'error': 'Invalid format. Supported formats: csv, json, xlsx'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create export record
        export_record = DataExport.objects.create(
            requested_by=request.user,
            study_id=study_id,
            export_type='quiz_responses',
            export_format=export_format,
            filters=filters
        )
        
        # Generate export
        try:
            response = research_exporter.export_quiz_responses(
                study_id=study_id,
                export_format=export_format,
                filters=filters
            )
            
            # Update export record
            export_record.status = 'completed'
            export_record.exported_at = datetime.now()
            export_record.save()
            
            return response
            
        except Exception as e:
            export_record.status = 'failed'
            export_record.save()
            raise e
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def export_full_dataset(request):
    """
    Export complete dataset with all data types
    
    Expected payload:
    {
        "study_id": "uuid",
        "filters": {
            "date_range_start": "2024-01-01",
            "date_range_end": "2024-12-31"
        }
    }
    """
    try:
        data = request.data
        study_id = data.get('study_id')
        filters = data.get('filters', {})
        
        # Validate study if provided
        if study_id:
            try:
                study = ResearchStudy.objects.get(id=study_id)
            except ResearchStudy.DoesNotExist:
                return Response(
                    {'error': 'Study not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Create export record
        export_record = DataExport.objects.create(
            requested_by=request.user,
            study_id=study_id,
            export_type='full_dataset',
            export_format='xlsx',
            filters=filters
        )
        
        # Generate export
        try:
            response = research_exporter.export_full_dataset(
                study_id=study_id,
                export_format='xlsx',
                filters=filters
            )
            
            # Update export record
            export_record.status = 'completed'
            export_record.exported_at = datetime.now()
            export_record.save()
            
            return response
            
        except Exception as e:
            export_record.status = 'failed'
            export_record.save()
            raise e
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def get_export_history(request):
    """
    Get export history for the current user
    
    Query parameters:
    - study_id: Filter by study ID (optional)
    - export_type: Filter by export type (optional)
    - limit: Limit number of results (default 50)
    """
    try:
        study_id = request.GET.get('study_id')
        export_type = request.GET.get('export_type')
        limit = int(request.GET.get('limit', 50))
        
        # Build queryset
        exports = DataExport.objects.filter(requested_by=request.user)
        
        if study_id:
            exports = exports.filter(study_id=study_id)
        
        if export_type:
            exports = exports.filter(export_type=export_type)
        
        exports = exports.order_by('-created_at')[:limit]
        
        # Serialize data
        export_data = []
        for export in exports:
            export_data.append({
                'id': str(export.id),
                'export_type': export.export_type,
                'export_format': export.export_format,
                'status': export.status,
                'created_at': export.created_at.isoformat(),
                'exported_at': export.exported_at.isoformat() if export.exported_at else None,
                'study_name': export.study.name if export.study else None,
                'filters': export.filters,
                'file_size_bytes': export.file_size_bytes,
                'record_count': export.record_count,
                'download_count': export.download_count
            })
        
        return Response({
            'exports': export_data,
            'total_count': exports.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def get_export_stats(request):
    """
    Get export statistics
    
    Query parameters:
    - study_id: Filter by study ID (optional)
    - days: Number of days to look back (default 30)
    """
    try:
        study_id = request.GET.get('study_id')
        days = int(request.GET.get('days', 30))
        
        from datetime import datetime, timedelta
        from django.utils import timezone
        from django.db.models import Count, Sum
        
        # Date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Build queryset
        exports = DataExport.objects.filter(created_at__gte=start_date)
        
        if study_id:
            exports = exports.filter(study_id=study_id)
        
        # Calculate statistics
        total_exports = exports.count()
        successful_exports = exports.filter(status='completed').count()
        failed_exports = exports.filter(status='failed').count()
        
        # Export type distribution
        export_types = exports.values('export_type').annotate(count=Count('id'))
        export_type_distribution = {item['export_type']: item['count'] for item in export_types}
        
        # Format distribution
        export_formats = exports.values('export_format').annotate(count=Count('id'))
        export_format_distribution = {item['export_format']: item['count'] for item in export_formats}
        
        # Daily export counts
        daily_exports = exports.extra(
            select={'day': 'DATE(created_at)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        # Total download counts
        total_downloads = exports.aggregate(total=Sum('download_count'))['total'] or 0
        
        stats = {
            'total_exports': total_exports,
            'successful_exports': successful_exports,
            'failed_exports': failed_exports,
            'success_rate': (successful_exports / total_exports * 100) if total_exports > 0 else 0,
            'export_type_distribution': export_type_distribution,
            'export_format_distribution': export_format_distribution,
            'daily_exports': list(daily_exports),
            'total_downloads': total_downloads,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )