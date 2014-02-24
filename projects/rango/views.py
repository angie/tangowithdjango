from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm, PageForm

# Methods to encode and decode URLs
def encode_url(str):
	return str.replace(' ', '_')
	
def decode_url(str):
	return str.replace('_', ' ')
	
def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__startswith=starts_with)
    else:
        cat_list = Category.objects.all()

    if max_results > 0:
        if (len(cat_list) > max_results):
            cat_list = cat_list[:max_results]

    for cat in cat_list:
        cat.url = encode_url(cat.name)
    
    return cat_list

def index(request):
    # Request the context of the request.
	context = RequestContext(request)

	# Query the database for a list of ALL categories currently stored
	# Order the categories by no. likes in descending order
	# Retrieve the top 5 only - or all if less than 5
	category_list = Category.objects.order_by('-likes')[:5]
	context_dict = {'categories' : category_list}
	
	# Loop through each category returned and create a URL attribute
	for category in category_list:
		category.url = encode_url(category.name)
		
	# Top 5 most viewed pages
	top_pages_list = Page.objects.order_by('-views')[:5]
	context_dict['top_pages'] = top_pages_list

	# Render the response and send it back!
	return render_to_response('rango/index.html', context_dict, context)

def about(request):
	return render_to_response('rango/about.html')

def category(request, category_name_url):
	# Request our context from the request passed to us.
	context = RequestContext(request)

	# Change underscores in the category name to spaces.
	category_name = decode_url(category_name_url)
	
	# Create a context dictionary which we can pass to the template rendering engine.
	# We start by containing the name of the category passed by the user.
	context_dict = {'category_name' : category_name}
	
	try:
		# Returns one model object to hops to except block
		category = Category.objects.get(name=category_name)
	
		# Retrieve all of the associated pages.
		pages = Page.objects.filter(category=category)
	
		# Adds our results list to the template context under name pages.
		context_dict['pages'] = pages
		# We also add the category object from the database to the context dictionary.
		# We'll use this in the template to verify that the category exists.
		context_dict['category'] = category
	except: Category.DoesNotExist
		# We get here if we didn't find the specified category.
		# Don't do anything - the template displays the "no category" message for us.
	pass
	
	context_dict['category_name_url'] = category_name_url
		
	# Go render the response and return it to the client.
	return render_to_response('rango/category.html', context_dict, context)
	
def add_category(request):
	# Get the context from the request
	context = RequestContext(request)
	
	# A HTTP POST?
	if request.method == 'POST':
		form = CategoryForm(request.POST)
		
		# Have we been provided with a valid form?
		if form.is_valid():
			# Save the new category to the DB
			form.save(commit=True)
			
			# Now call the index() view.
			# The user will be shown the homepage.
			return index(request)
		else:
			# The supplied form contained errors - just print them to the terminal
			print form.errors
			
	else:
		# If the request was not a POST, display the form to enter details.
		form = CategoryForm()
		
	# Bad form (or form details), no form supplied...
	# Render the form with error messages (if any).
	return render_to_response('rango/add_category.html', {'form': form}, context)
		
def add_page(request, category_name_url):
    context = RequestContext(request)
    cat_list = get_category_list()
    context_dict = {}
    context_dict['cat_list'] = cat_list

    category_name = decode_url(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)
        
        if form.is_valid():
            # This time we cannot commit straight away.
            # Not all fields are automatically populated!
            page = form.save(commit=False)

            # Retrieve the associated Category object so we can add it.
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                return render_to_response( 'rango/add_page.html',
                                          context_dict,
                                          context)

            # Also, create a default value for the number of views.
            page.views = 0

            # With this, we can then save our new model instance.
            page.save()

            # Now that the page is saved, display the category instead.
            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict['category_name_url']= category_name_url
    context_dict['category_name'] =  category_name
    context_dict['form'] = form

    return render_to_response( 'rango/add_page.html',
                               context_dict,
                               context)