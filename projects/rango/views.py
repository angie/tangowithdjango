from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

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
                               

def register(request):
    # Like before, get the request's context.
    context = RequestContext(request)
    context_dict = {}

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
        
    context_dict['user_form'] = user_form
    context_dict['profile_form'] = profile_form
    context_dict['registered'] = registered

    # Render the template depending on the context.
    return render_to_response(
            'rango/register.html', context_dict, context)
            
def user_login(request):
	# Obtain the context for the user's request
	context = RequestContext(request)
	
	# If the request is a POST, try to pull out relevant information.
	if request.method == 'POST':
	# Gather username and password provided by the user.
		username = request.POST['username']
		password = request.POST['password']
	
		# Use Django to check username/password combo validity
		user = authenticate(username=username, password=password)
	
		# If we have a User objection, the details are correct.
		if user is not None:
			# is the account active?
			if user.is_active:
				# If active, we can log in!
				login(request, user)
				return HttpResponseRedirect('/rango/')
			else:
				return HttpResponseRedirect("Your Rango account is disabled.")
		else:
			# Bad login details!
			print "Invalid login details: {0}, {1}".format(username, password)
			return HttpResponse("Invalid login details supplied. You tried to log in as: %s" % username)
			
	# Request is not POST, so display login form.
	else:
		# No context variables to pass, hence blank dictionary
		return render_to_response('rango/login.html', {}, context)
	
@login_required
def restricted(request):
	return HttpResponse("Since you're logged in, you can see this text!")
	
@login_required
def user_logout(request):
	# Since we know the user is logged in, we can just log them out!
	logout(request)
	
	# Return to homepage
	return HttpResponseRedirect('/rango/')
