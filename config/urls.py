from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    ###############################
    #          ADMIN V1          #
    ###############################
    path('admin/', admin.site.urls),
    ###############################
    #         API V1             #
    ###############################
    path("api/v1/", include("weather_api.urls")),
    path("api/v1/webapp/", include("web_app.urls")),
    ###############################
    #         HEALTH CHECK        #
    ###############################
    path(r"health/", include("health_check.urls")),
]


if settings.ENABLE_DOCS:
    urlpatterns += [
        path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("api/v1/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path("api/v1/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]


if settings.ENABLE_SILK:
    urlpatterns.append(path("silk/", include("silk.urls", namespace="silk")))
