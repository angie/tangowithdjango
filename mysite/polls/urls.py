from django.conf.urls import patterns, url
from polls import views

urlpatterns = patterns('',
	url(r'^$', views.IndexView.as_view(), name='index'), # e.g. /polls/
	url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'), # e.g. /polls/5/. The 'name' value as called by the {% url %} template tag
	url(r'^(?P<pk>\d+)/results/$', views.ResultsView.as_view(), name='results'), # e.g. /polls/5/results/
	url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'), # e.g. /polls/5/vote/
)
