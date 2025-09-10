from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Sum, Count, Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from django.conf import settings

from .models import AccountBase
from .serializers import AccountBaseSerializer, AccountBaseSummarySerializer
from userManagement.permissions import CanViewAccountBase, CanViewReports, CanExportReports


# Custom OR permission
class CanViewAccountBaseOrReports(BasePermission):
    """
    Allow access if the user has either view_accountbase OR view_reports permission
    """
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        return (
            user.has_perm('userManagement.view_accountbase') or
            user.has_perm('userManagement.view_reports')
        )


class ReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    def get_queryset(self):
        return self.queryset


class AccountBaseViewSet(ReadOnlyModelViewSet):
    queryset = AccountBase.objects.all()
    serializer_class = AccountBaseSerializer
    search_fields = [
        'account_number', 
        'customer_name', 
        'customer_no',
        'phone_number',
        'branch_name',
        'product_name'
    ]
    filterset_fields = [
        'branch_code',
        'branch_name',
        'region',
        'currency',
        'category',
        'product_name',
        'sector',
        'industry',
        'cust_type'
    ]
    ordering_fields = [
        'account_number',
        'customer_name',
        'working_balance',
        'opening_date',
        'report_date'
    ]
    ordering = ['-report_date', '-report_time']

    def get_permissions(self):
        """
        Set permissions for different actions
        """
        if getattr(settings, "DEVELOPMENT", False):
            # Development mode: allow everything
            return []
        if self.action in ['list', 'retrieve']:
            return [CanViewAccountBaseOrReports()]
        elif self.action in ['stats', 'by_branch', 'high_balance', 'search_customer', 'recent_accounts', 'health_check']:
            return [IsAuthenticated(), CanViewReports()]
        elif self.action in ['export', 'permissions']:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'list':
            return AccountBaseSummarySerializer
        return AccountBaseSerializer

    @swagger_auto_schema(
        operation_description="Check database health and connectivity",
        responses={200: 'Health check successful'}
    )
    @action(detail=False, methods=['get'], url_path='health')
    def health_check(self, request):
        try:
            count = AccountBase.objects.count()
            return  Response({"status": "ok"})
            # Response({
            #     'status': 'healthy',
            #     'database': 'connected',
            #     'record_count': count,
            #     'timestamp': timezone.now().isoformat()
            # })
        except Exception as e:
            return Response({
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    @swagger_auto_schema(
        operation_description="Check user permissions for report endpoints",
        responses={200: 'Permissions information'}
    )
    @action(detail=False, methods=['get'])
    def permissions(self, request):
        user = request.user
        permissions_status = {
            'view_accountbase': user.has_perm('userManagement.view_accountbase'),
            'view_reports': user.has_perm('userManagement.view_reports'),
            'export_reports': user.has_perm('userManagement.export_reports'),
        }
        
        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role.name if user.role else None
            },
            'permissions': permissions_status,
            'accessible_endpoints': self.get_accessible_endpoints(permissions_status)
        })

    def get_accessible_endpoints(self, permissions):
        base_url = '/api/reports/account-base/'
        accessible = permissions['view_accountbase'] or permissions['view_reports']
        advanced = permissions['view_reports']
        export = permissions['export_reports']
        
        return {
            'basic': {
                'list': f'{base_url}' if accessible else None,
                'detail': f'{base_url}{{account_number}}/' if accessible else None,
            },
            'advanced': {
                'stats': f'{base_url}stats/' if advanced else None,
                'by_branch': f'{base_url}by_branch/' if advanced else None,
                'high_balance': f'{base_url}high_balance/' if advanced else None,
                'search_customer': f'{base_url}search_customer/' if advanced else None,
                'recent_accounts': f'{base_url}recent_accounts/' if advanced else None,
            },
            'export': {
                'export': f'{base_url}export/' if export else None,
            },
            'system': {
                'permissions': f'{base_url}permissions/',
                'health': f'{base_url}health/',
            }
        }

    @swagger_auto_schema(
        operation_description="Get account statistics",
        responses={200: 'Statistics data'}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_accounts = self.get_queryset().count()
        total_balance = self.get_queryset().aggregate(
            total=Sum('working_balance')
        )['total'] or 0
        
        branch_stats = self.get_queryset().values('branch_name').annotate(
            count=Count('account_number'),
            total_balance=Sum('working_balance')
        ).order_by('-total_balance')
        
        product_stats = self.get_queryset().values('product_name').annotate(
            count=Count('account_number'),
            total_balance=Sum('working_balance')
        ).order_by('-total_balance')
        
        return Response({
            'total_accounts': total_accounts,
            'total_balance': float(total_balance),
            'by_branch': list(branch_stats),
            'by_product': list(product_stats)
        })

    @swagger_auto_schema(
        operation_description="Get accounts filtered by branch",
        manual_parameters=[
            openapi.Parameter('branch_code', openapi.IN_QUERY, description="Branch code", type=openapi.TYPE_STRING),
            openapi.Parameter('branch_name', openapi.IN_QUERY, description="Branch name", type=openapi.TYPE_STRING),
        ],
        responses={200: AccountBaseSummarySerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_branch(self, request):
        branch_code = request.query_params.get('branch_code')
        branch_name = request.query_params.get('branch_name')
        
        queryset = self.get_queryset()
        
        if branch_code:
            queryset = queryset.filter(branch_code=branch_code)
        elif branch_name:
            queryset = queryset.filter(branch_name__icontains=branch_name)
        else:
            return Response(
                {'error': 'Please provide branch_code or branch_name parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get accounts with high working balance",
        manual_parameters=[
            openapi.Parameter('min_balance', openapi.IN_QUERY, description="Minimum balance", type=openapi.TYPE_NUMBER, default=100000),
        ],
        responses={200: AccountBaseSummarySerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def high_balance(self, request):
        try:
            min_balance = float(request.query_params.get('min_balance', 100000))
        except ValueError:
            return Response(
                {'error': 'min_balance must be a valid number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            working_balance__gte=min_balance
        ).order_by('-working_balance')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Search customers by name or phone",
        manual_parameters=[
            openapi.Parameter('q', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING, required=True),
        ],
        responses={200: AccountBaseSummarySerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def search_customer(self, request):
        query = request.query_params.get('q')
        
        if not query:
            return Response(
                {'error': 'Please provide search query (q parameter)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            Q(customer_name__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(customer_no__icontains=query)
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get recently opened accounts",
        manual_parameters=[
            openapi.Parameter('limit', openapi.IN_QUERY, description="Number of records", type=openapi.TYPE_INTEGER, default=100),
        ],
        responses={200: AccountBaseSummarySerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def recent_accounts(self, request):
        try:
            limit = int(request.query_params.get('limit', 100))
        except ValueError:
            return Response(
                {'error': 'limit must be a valid integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().order_by('-opening_date')[:limit]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Export data to CSV",
        manual_parameters=[
            openapi.Parameter('branch_code', openapi.IN_QUERY, description="Filter by branch code", type=openapi.TYPE_STRING),
        ],
        responses={200: 'CSV file'}
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        if not request.user.has_perm('userManagement.export_reports'):
            return Response(
                {'error': 'You do not have permission to export reports'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from django.http import HttpResponse
        import csv
        
        queryset = self.get_queryset()
        branch_code = request.query_params.get('branch_code')
        if branch_code:
            queryset = queryset.filter(branch_code=branch_code)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="account_base_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Account Number', 'Customer Name', 'Customer No', 'Phone Number',
            'Working Balance', 'Currency', 'Branch Name', 'Product Name',
            'Category', 'Sector', 'Industry', 'Opening Date'
        ])
        
        for account in queryset[:1000]:
            writer.writerow([
                account.account_number,
                account.customer_name or '',
                account.customer_no or '',
                account.phone_number or '',
                account.working_balance or 0,
                account.currency or '',
                account.branch_name or '',
                account.product_name or '',
                account.category or '',
                account.sector or '',
                account.industry or '',
                account.opening_date.strftime('%Y-%m-%d') if account.opening_date else ''
            ])
        
        return response

    @swagger_auto_schema(
        operation_description="List all accounts with filtering and pagination",
        responses={200: AccountBaseSummarySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve account details",
        responses={200: AccountBaseSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
