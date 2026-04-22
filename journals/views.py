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

import os
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .models import Journal
from .utils import get_transcription

# Home page view
def home(request):
    context = {}
    # This is for getting the top 3 journals on the home page
    if request.user.is_authenticated:
        # Get top 3 most recent journals
        journals = request.user.journals.all().order_by('-date_updated')[:3]
        context['journals'] = journals
        
    return render(request, 'journals/home.html', context)



# Creates a new journal entry: This will be called when the user submits the create journal form
@login_required
def createJournal(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'Untitled Entry')                 # Default title if none provided

        # Save the new journal entry to the database
        journal = request.user.journals.create(title=title, content="")
        return redirect('journals:openJournal', journal_id=journal.id)      # Redirect to the newly created journals
    


# Edits an existing/newly created journal entry 
@login_required
def openJournal(request, journal_id):
    # Ensure the journal belongs to the logged-in user
    journal = get_object_or_404(request.user.journals, id=journal_id)
    
    # Handle POST request to save updates to the journal
    # Note: Need to create JS function to send updated content as JSON via fetch API
    if request.method == 'POST':
        data = json.loads(request.body)                                     # Parse JSON data from request body
        journal.content = data.get('content')                               # Update journal content
        journal.save()                                                      # Save changes to the database  
        return JsonResponse({'status': 'success'})

    # The GET request will load the journal content into the editor for viewing/editing
    else:
        return render(request, 'journals/journal.html', {'journal': journal})
    



# Deletes a Journal entry: (not yet implemented)
@login_required
def deleteJournal(request, journal_id):
    if request.method == 'POST':
        journal = get_object_or_404(request.user.journals, id=journal_id)
        journal.delete()
        return redirect('journals:listJournals')



# Display User Journals: This will be called to load and loop through all journals for the logged-in user
@login_required
def listJournals(request):

    if request.method == 'GET':
        journals = request.user.journals.all().order_by('-date_updated')  # Get all journals for the current user, ordered by date_updated descending
        context = {
            'journals': journals
        }
        return render(request, 'journals/listJournals.html', context)
    
    else:
        return render(request, 'journals/listJournals.html')

@login_required
@csrf_exempt
def transcribe_audio(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        
        try:
            # Safely create media/temp_audio directory in the project root
            temp_dir = os.path.join(settings.BASE_DIR, 'media', 'temp_audio')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
                
            fs = FileSystemStorage(location=temp_dir)
            filename = fs.save(audio_file.name, audio_file)
            file_path = fs.path(filename)
            
            # Pass the file path to your PyTorch model via the helper in utils.py
            transcribed_text = get_transcription(file_path)
            
            # Clean up the temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
                
            return JsonResponse({'status': 'success', 'text': transcribed_text})
            
        except Exception as e:
            print(f"Transcription Error: {e}")
            # Clean up the temporary file if it failed along the line
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request or missing audio file'}, status=400)