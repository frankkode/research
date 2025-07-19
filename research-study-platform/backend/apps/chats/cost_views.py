from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from datetime import datetime, timedelta
from .cost_management import CostManagementService
import json


def is_staff_user(user):
    """Check if user is staff/admin"""
    return user.is_staff or user.is_superuser


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def get_cost_overview(request):
    """Get overview of OpenAI API costs"""
    try:
        # Get date range from query parameters
        days = int(request.GET.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()
        
        stats = CostManagementService.get_cost_stats(start_date, end_date)
        system_limits = CostManagementService.get_system_limits()
        
        overview = {
            'stats': {
                'total_cost': float(stats['total_cost']),
                'total_interactions': stats['total_interactions'],
                'total_tokens': stats['total_tokens'],
                'average_cost_per_interaction': float(stats['average_cost_per_interaction'])
            },
            'limits': system_limits,
            'cost_by_model': [
                {
                    'model': item['openai_model'],
                    'total_cost': float(item['total_cost']),
                    'count': item['count']
                }
                for item in stats['cost_by_model']
            ],
            'daily_costs': [
                {
                    'date': item['date'].strftime('%Y-%m-%d'),
                    'cost': float(item['total_cost']),
                    'interactions': item['count']
                }
                for item in stats['daily_costs']
            ]
        }
        
        return Response(overview, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def get_user_costs(request):
    """Get cost breakdown by user"""
    try:
        top_users = CostManagementService.get_top_users_by_cost(limit=20)
        
        user_costs = [
            {
                'participant_id': user['user__participant_id'],
                'study_group': user['user__study_group'],
                'username': user['user__username'],
                'total_cost': float(user['total_cost']),
                'total_interactions': user['total_interactions'],
                'total_tokens': user['total_tokens'],
                'avg_cost_per_interaction': float(user['total_cost'] / user['total_interactions']) if user['total_interactions'] > 0 else 0
            }
            for user in top_users
        ]
        
        return Response(user_costs, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(is_staff_user)
def export_cost_report(request):
    """Export comprehensive cost report"""
    try:
        # Get date range from request data
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')
        
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
        
        report = CostManagementService.export_cost_report(start_date, end_date)
        
        return JsonResponse(report, status=200, safe=False)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_user_limits(request):
    """Check current user's cost limits"""
    try:
        limits = CostManagementService.check_user_limits(request.user.id)
        
        response_data = {
            'daily_cost': float(limits['daily_cost']),
            'weekly_cost': float(limits['weekly_cost']),
            'daily_limit_exceeded': limits['daily_limit_exceeded'],
            'weekly_limit_exceeded': limits['weekly_limit_exceeded'],
            'daily_remaining': float(limits['daily_remaining']),
            'weekly_remaining': float(limits['weekly_remaining'])
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)