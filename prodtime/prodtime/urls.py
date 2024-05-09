from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers, permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from dealcard.views import ProdTimeDealViewSet

router = routers.DefaultRouter()
router.register(r'prodtime', ProdTimeDealViewSet, basename='prodtime')

schema_view = get_schema_view(
   openapi.Info(
      title="ProdTime API",
      default_version='v1',
      description="ProdTime description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="kel.krsk@mail.ru"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny,],
)

urlpatterns = [
    path('', include('settings.urls', namespace='settings')),
    path('install/', include('core.urls', namespace='core')),
    path('dealcard/', include('dealcard.urls', namespace='dealcard')),
    path('quotecard/', include('quotecard.urls', namespace='quotecard')),
    path('reports/', include('reports.urls', namespace='reports')),
    path('activities/', include('activities.urls', namespace='activities')),
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    # path('api/v1/auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('api-docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
