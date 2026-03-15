from rest_framework import serializers
from .models import Receiver, AlertGroup, AlertHistory


class ReceiverSerializer(serializers.ModelSerializer):
    """接收人序列化器"""
    receive_type_display = serializers.CharField(source='get_receive_type_display', read_only=True)

    class Meta:
        model = Receiver
        fields = ['id', 'name', 'receive_type', 'receive_type_display', 'email', 'webhook_url',
                  'phone', 'remark', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AlertGroupSerializer(serializers.ModelSerializer):
    """告警分组序列化器"""
    receivers = ReceiverSerializer(many=True, read_only=True)
    receiver_ids = serializers.PrimaryKeyRelatedField(
        queryset=Receiver.objects.all(),
        many=True,
        write_only=True,
        source='receivers',
        required=False
    )
    receiver_count = serializers.SerializerMethodField()

    class Meta:
        model = AlertGroup
        fields = ['id', 'name', 'description', 'match_rules', 'receivers', 'receiver_ids',
                  'receiver_count', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_receiver_count(self, obj):
        return obj.receivers.count()


class AlertGroupListSerializer(serializers.ModelSerializer):
    """告警分组列表序列化器"""
    receiver_count = serializers.SerializerMethodField()
    receiver_names = serializers.SerializerMethodField()

    class Meta:
        model = AlertGroup
        fields = ['id', 'name', 'description', 'match_rules', 'receiver_count',
                  'receiver_names', 'is_active', 'created_at', 'updated_at']

    def get_receiver_count(self, obj):
        return obj.receivers.count()

    def get_receiver_names(self, obj):
        return [r.name for r in obj.receivers.all()]


class AlertHistorySerializer(serializers.ModelSerializer):
    """告警历史序列化器"""
    alert_group_name = serializers.CharField(source='alert_group.name', read_only=True)

    class Meta:
        model = AlertHistory
        fields = ['id', 'alert_name', 'severity', 'message', 'labels', 'status',
                  'alert_group', 'alert_group_name', 'fired_at', 'resolved_at', 'created_at']
        read_only_fields = ['id', 'created_at']