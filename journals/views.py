'''
This is where all the crud (create, read, update, delete) operations for journals will be handled.
Completed:
- Read: listJournals() - lists all journals for the logged-in user
'''

from django.shortcuts import render

# Home page view
def home(request):
    return render(request, 'journals/home.html')



# Creates a new journal entry (not yet implemented)
def createJournal(request):
    if request.method == 'POST':
        pass



# Edits an existing journal entry (not yet implemented)
def editJournal(request, journal_id):
    if request.method == 'POST':
        pass



# Deletes a journal entry (not yet implemented)
def deleteJournal(request, journal_id):
    if request.method == 'POST':
        pass



# Gathers and displays a list of journals for the logged-in user
def listJournals(request):

    if request.method == 'GET':
        journals = request.user.journals.all()  # Get all journals for the current user
        context = {
            'journals': journals
        }
        return render(request, 'journals/listJournals.html', context)
    
    else:
        return render(request, 'journals/listJournals.html')