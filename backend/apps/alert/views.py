from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
import logging

from .models import Receiver, AlertGroup, AlertHistory
from .serializers import (
    ReceiverSerializer,
    AlertGroupSerializer,
    AlertGroupListSerializer,
    AlertHistorySerializer
)

logger = logging.getLogger(__name__)


class ReceiverViewSet(viewsets.ModelViewSet):
    """接收人管理视图集"""
    queryset = Receiver.objects.all()
    serializer_class = ReceiverSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        receive_type = self.request.query_params.get('receive_type')
        is_active = self.request.query_params.get('is_active')

        if name:
            queryset = queryset.filter(name__icontains=name)
        if receive_type:
            queryset = queryset.filter(receive_type=receive_type)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """切换激活状态"""
        receiver = self.get_object()
        receiver.is_active = not receiver.is_active
        receiver.save()
        return Response({
            'id': receiver.id,
            'is_active': receiver.is_active,
            'message': f'接收人已{"启用" if receiver.is_active else "禁用"}'
        })


class AlertGroupViewSet(viewsets.ModelViewSet):
    """告警分组视图集"""
    queryset = AlertGroup.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return AlertGroupListSerializer
        return AlertGroupSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        is_active = self.request.query_params.get('is_active')

        if name:
            queryset = queryset.filter(name__icontains=name)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """切换激活状态"""
        alert_group = self.get_object()
        alert_group.is_active = not alert_group.is_active
        alert_group.save()
        return Response({
            'id': alert_group.id,
            'is_active': alert_group.is_active,
            'message': f'告警分组已{"启用" if alert_group.is_active else "禁用"}'
        })

    @action(detail=True, methods=['get', 'post'])
    def receivers(self, request, pk=None):
        """管理分组的接收人"""
        alert_group = self.get_object()

        if request.method == 'GET':
            receivers = alert_group.receivers.all()
            serializer = ReceiverSerializer(receivers, many=True)
            return Response(serializer.data)

        # POST - 更新接收人列表
        receiver_ids = request.data.get('receiver_ids', [])
        alert_group.receivers.set(receiver_ids)
        return Response({
            'message': '接收人已更新',
            'receiver_count': alert_group.receivers.count()
        })


class AlertHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """告警历史视图集（只读）"""
    queryset = AlertHistory.objects.all()
    serializer_class = AlertHistorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        alert_name = self.request.query_params.get('alert_name')
        severity = self.request.query_params.get('severity')
        status = self.request.query_params.get('status')
        alert_group = self.request.query_params.get('alert_group')

        if alert_name:
            queryset = queryset.filter(alert_name__icontains=alert_name)
        if severity:
            queryset = queryset.filter(severity=severity)
        if status:
            queryset = queryset.filter(status=status)
        if alert_group:
            queryset = queryset.filter(alert_group_id=alert_group)

        return queryset


def match_alert_group(labels):
    """
    根据告警标签匹配告警分组
    返回匹配的分组，如果没有匹配则返回 None
    """
    alert_groups = AlertGroup.objects.filter(is_active=True)

    for group in alert_groups:
        if not group.match_rules:
            continue

        # 检查所有规则是否匹配
        matched = True
        for key, value in group.match_rules.items():
            if labels.get(key) != value:
                matched = False
                break

        if matched:
            return group

    return None


def parse_alertmanager_time(time_str):
    """解析 AlertManager 的时间格式"""
    if not time_str:
        return None
    try:
        # AlertManager 使用 ISO 8601 格式: 2024-01-01T12:00:00.000Z
        if time_str.endswith('Z'):
            time_str = time_str[:-1] + '+00:00'
        return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return timezone.now()


def process_alert(alert_data, receiver_name=''):
    """
    处理单个告警并存储到数据库

    AlertManager 告警格式:
    {
        "status": "firing" | "resolved",
        "labels": {"alertname": "...", "severity": "...", ...},
        "annotations": {"description": "...", "summary": "..."},
        "startsAt": "2024-01-01T12:00:00.000Z",
        "endsAt": "0001-01-01T00:00:00.000Z",
        "fingerprint": "..."
    }
    """
    labels = alert_data.get('labels', {})
    annotations = alert_data.get('annotations', {})
    alert_status = alert_data.get('status', 'firing')

    # 获取告警名称
    alert_name = labels.get('alertname', labels.get('alert_name', 'Unknown Alert'))

    # 获取严重级别
    severity = labels.get('severity', 'warning')

    # 构建告警信息
    message_parts = []
    if annotations.get('summary'):
        message_parts.append(f"摘要: {annotations['summary']}")
    if annotations.get('description'):
        message_parts.append(f"描述: {annotations['description']}")
    if receiver_name:
        message_parts.append(f"接收器: {receiver_name}")

    message = '\n'.join(message_parts) if message_parts else f"告警: {alert_name}"

    # 匹配告警分组
    alert_group = match_alert_group(labels)

    # 解析时间
    fired_at = parse_alertmanager_time(alert_data.get('startsAt'))
    resolved_at = parse_alertmanager_time(alert_data.get('endsAt')) if alert_status == 'resolved' else None

    # 如果 resolved_at 是默认值（0001-01-01），则设为 None
    if resolved_at and resolved_at.year < 2000:
        resolved_at = None

    # 创建告警历史记录
    alert_history = AlertHistory.objects.create(
        alert_name=alert_name,
        severity=severity,
        message=message,
        labels=labels,
        status=alert_status,
        alert_group=alert_group,
        fired_at=fired_at or timezone.now(),
        resolved_at=resolved_at
    )

    return alert_history


@api_view(['POST'])
@permission_classes([AllowAny])
def alertmanager_webhook(request, receiver_name=''):
    """
    AlertManager Webhook 接收接口

    接收 AlertManager 发送的告警通知，支持以下格式:
    - POST /api/webhook/
    - POST /api/webhook/<receiver_name>/

    AlertManager 发送的数据格式:
    {
        "receiver": "webhook-receiver",
        "status": "firing" | "resolved",
        "alerts": [
            {
                "status": "firing",
                "labels": {"alertname": "...", "severity": "..."},
                "annotations": {"summary": "...", "description": "..."},
                "startsAt": "2024-01-01T12:00:00.000Z",
                "endsAt": "0001-01-01T00:00:00.000Z",
                "fingerprint": "..."
            }
        ],
        "groupLabels": {"alertname": "..."},
        "commonLabels": {"...": "..."},
        "commonAnnotations": {"...": "..."},
        "externalURL": "http://alertmanager:9093",
        "version": "4",
        "groupKey": "{}:{}"
    }
    """
    try:
        data = request.data

        # 记录接收到的数据
        logger.info(f"Received AlertManager webhook, receiver: {receiver_name or 'default'}")
        logger.debug(f"Webhook data: {data}")

        # 获取告警列表
        alerts = data.get('alerts', [])

        if not alerts:
            logger.warning("No alerts in webhook payload")
            return Response({
                'status': 'success',
                'message': 'No alerts to process',
                'processed': 0
            })

        # 处理每个告警
        processed_alerts = []
        for alert_data in alerts:
            try:
                alert = process_alert(alert_data, receiver_name or data.get('receiver', ''))
                processed_alerts.append({
                    'id': alert.id,
                    'name': alert.alert_name,
                    'status': alert.status,
                    'group': alert.alert_group.name if alert.alert_group else None
                })
                logger.info(f"Processed alert: {alert.alert_name}, status: {alert.status}")
            except Exception as e:
                logger.error(f"Failed to process alert: {e}", exc_info=True)

        return Response({
            'status': 'success',
            'message': f'Processed {len(processed_alerts)} alert(s)',
            'processed': len(processed_alerts),
            'alerts': processed_alerts
        })

    except Exception as e:
        logger.error(f"Webhook processing error: {e}", exc_info=True)
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def alertmanager_webhook_test(request):
    """
    测试接口 - 用于测试 Webhook 连通性
    """
    return Response({
        'status': 'success',
        'message': 'Webhook is reachable',
        'timestamp': timezone.now().isoformat()
    })