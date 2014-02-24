from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from polls.models import Choice, Poll

def IndexView(generic.ListView):
	template_name = 'polls/index.html'
	context_object_name = 'lastest_poll_list'
	
	def get_queryset(self):
		''' Return the last five published polls. '''
		return Poll.ojects.order_by('-pub_date')[:5]
	
def detail(request, poll_id):
	poll = get_object_or_404(Poll, pk=poll_id)
	return render(request, 'polls/detail.html', {'poll': poll})
	
def results(request, poll_id):
	poll = get_object_or_404(Poll, pk=poll_id)
	return render(request, 'polls/results.html', {'poll': poll})
	
def vote(request, poll_id):
	p = get_object_or_404(Poll, pk=poll_id)
	try:
		selected_choice = p.choice_set.get(pk=request.POST['choice'])
	except (KeyError, Choice.DoesNotExist):
		# Redisplay the poll voting form
		return render(request, 'polls/detail.html', {
			'poll': p,
			'error message': "You didn't select a choice.",
		})
	else:
		selected_choice.votes += 1
		selected_choice.save()
		# Always return an HttpResponseRedirect after successfully dealing
		# with POST data. This prevents data from being posted twice if a user
		# hits the Back button.
		return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))
