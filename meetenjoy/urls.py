from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include, re_path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from graphene_django.views import GraphQLView
from meetings.urls import urlpatterns as meeting_urlpatterns
from accounts.urls import urlpatterns as accounts_urlpatterns

API_V1 = 'api/v1/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path(API_V1, include("rest_auth.urls")),
    path(API_V1, include(accounts_urlpatterns)),
    path(API_V1, include(meeting_urlpatterns)),
    path("graphql", GraphQLView.as_view(graphiql=True)),
]
urlpatterns += staticfiles_urlpatterns()

if settings.USE_SWAGGER:
    api_v4_schema_view = get_schema_view(
        openapi.Info(title="Meetenjoy", default_version="v1", description="Meetenjoy v1 API description"),
        public=True,
        permission_classes=(permissions.AllowAny,),
        patterns=urlpatterns,
    )

    urlpatterns += [
        re_path(
            f"docs/v1/" + r"swagger(?P<format>\.json|\.yaml)$",
            api_v4_schema_view.without_ui(cache_timeout=0),
            name="v4-schema-json",
        ),
        path(
            f"docs/v1/swagger/",
            api_v4_schema_view.with_ui("swagger", cache_timeout=0),
            name="v4-schema-swagger-ui",
        ),
        path(
            f"docs/v1/redoc/",
            api_v4_schema_view.with_ui("redoc", cache_timeout=0),
            name="v4-schema-redoc",
        ),
    ]
