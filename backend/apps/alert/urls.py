from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import (
    ReceiverViewSet,
    AlertGroupViewSet,
    AlertHistoryViewSet,
    alertmanager_webhook,
    alertmanager_webhook_test
)

router = DefaultRouter()
router.register(r'receivers', ReceiverViewSet)
router.register(r'alert-groups', AlertGroupViewSet)
router.register(r'alert-history', AlertHistoryViewSet)

urlpatterns = [
    # AlertManager Webhook 接口
    path('webhook', alertmanager_webhook),
    path('webhook/test', alertmanager_webhook_test),
    re_path(r'^webhook(?P<receiver_name>[\w\-]+)/$', alertmanager_webhook),
    # REST API
    path('', include(router.urls)),
]