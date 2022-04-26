from django_request_mapping import UrlPattern

from board.views import MyView


urlpatterns = UrlPattern();
urlpatterns.register(MyView);
