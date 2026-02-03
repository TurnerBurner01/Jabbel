'''
This is where all the crud (create, read, update, delete) operations for journals will be handled.
Completed:
- ReadAll: listJournals() - lists all journals for the logged-in user
- Read: openJournal() - opens an existing journal entry for viewing/editing
- Create: createJournal() - creates a new journal entry for the logged-in user
'''

'''
Data Pipeline for Journal entries:
1. Create a new journal entry - createJournal()
2. Passes that new journal.id to openJournal() to open it for editing
'''

import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Journal

# Home page view
def home(request):
    return render(request, 'journals/home.html')



# Creates a new journal entry: This will be called when the user submits the create journal form
@login_required
def createJournal(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'Untitled Entry')  # Default title if none provided

        # Save the new journal entry to the database
        journal = request.user.journals.create(title=title, content={})
        return redirect('journals:openJournal', journal_id=journal.id)  # Redirect to the newly created journal
    else:
        return render(request, 'journals/createJournal.html')
    


# Edits an existing/newly created journal entry (not yet implemented)
@login_required
def openJournal(request, journal_id):

    # Handle GET request to open and view the journal
    if request.method == 'GET':
        journal = get_object_or_404(request.user.journals, id=journal_id) # Ensure the journal belongs to the logged-in user
        context = { 
            'journal': journal
        }
        return render(request, 'journals/Journal.html', context)
    
    # Handle POST request to save updates to the journal
    elif request.method == 'POST':
        data = json.loads(request.body)
        journal.content = data.get('content')
        journal.save()
        return JsonResponse({'status': 'success'})

    # User just opened the page
    else:
        return render(request, 'journals/Journal.html', {'journal': journal})
    



# Deletes a Journal entry: (not yet implemented)
@login_required
def deleteJournal(request, journal_id):
    if request.method == 'POST':
        pass



# Display User Journals: This will be called to load and loop through all journals for the logged-in user
@login_required
def listJournals(request):

    if request.method == 'GET':
        journals = request.user.journals.all()  # Get all journals for the current user
        context = {
            'journals': journals
        }
        return render(request, 'journals/listJournals.html', context)
    
    else:
        return render(request, 'journals/listJournals.html')