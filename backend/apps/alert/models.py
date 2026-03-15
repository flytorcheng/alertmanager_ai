from django.db import models


class Receiver(models.Model):
    """接收人模型"""
    RECEIVE_TYPE_CHOICES = [
        ('email', '邮件'),
        ('webhook', 'Webhook'),
        ('dingtalk', '钉钉'),
        ('wechat', '企业微信'),
        ('slack', 'Slack'),
    ]

    name = models.CharField('姓名', max_length=100)
    receive_type = models.CharField('接收方式', max_length=20, choices=RECEIVE_TYPE_CHOICES, default='email')
    email = models.EmailField('邮箱地址', blank=True, null=True)
    webhook_url = models.URLField('Webhook地址', blank=True, null=True)
    phone = models.CharField('手机号', max_length=20, blank=True, null=True)
    remark = models.TextField('备注', blank=True, null=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'alert_receiver'
        verbose_name = '接收人'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class AlertGroup(models.Model):
    """告警分组模型"""
    name = models.CharField('分组名称', max_length=100)
    description = models.TextField('分组描述', blank=True, null=True)
    match_rules = models.JSONField('匹配规则', default=dict, help_text='告警标签匹配规则，JSON格式')
    receivers = models.ManyToManyField(Receiver, verbose_name='接收人', related_name='alert_groups', blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'alert_group'
        verbose_name = '告警分组'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class AlertHistory(models.Model):
    """告警历史记录"""
    STATUS_CHOICES = [
        ('firing', '告警中'),
        ('resolved', '已恢复'),
    ]

    alert_name = models.CharField('告警名称', max_length=200)
    severity = models.CharField('严重级别', max_length=20, default='warning')
    message = models.TextField('告警信息')
    labels = models.JSONField('标签', default=dict)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='firing')
    alert_group = models.ForeignKey(AlertGroup, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='告警分组')
    fired_at = models.DateTimeField('触发时间')
    resolved_at = models.DateTimeField('恢复时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'alert_history'
        verbose_name = '告警历史'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.alert_name