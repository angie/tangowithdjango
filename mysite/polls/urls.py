from django.conf.urls import patterns, url
from polls import views

urlpatterns = patterns('',
	# e.g. /polls/
	url(r'^$', views.index, name='index'),
	# e.g. /polls/5/
	# the 'name' value as called by the {% url %} template tag
	url(r'^(?P<poll_id>\d+)/$', views.detail, name='detail'),
	# e.g. /polls/5/results/
	url(r'^(?P<poll_id>\d+)/results/$', views.results, name='results'),
	# e.g. /polls/5/vote/
	url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),
)
