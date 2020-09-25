from django.shortcuts import render
from django import forms
from django.core.files import File
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse 
import markdown2
import random

from . import util

class SearchForm(forms.Form):
    query = forms.CharField(label="Search Encyclopedia")

class CreateForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea)

class EditForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })

#Get entry via util get_entry and display the title 
def entry(request, title):
    if util.get_entry(title) == None:
        return render(request, "encyclopedia/error.html", {
            "form": SearchForm(),
            "error_message": f"The requested page: {title}, was not found. Try the search bar to find a similar page."
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": markdown2.markdown(util.get_entry(title)),
            "form": SearchForm()
        })

def search(request):
    # Check if method is GET
    if request.method == "GET":

        # Take in the data the user submitted and save it as form
        form = SearchForm(request.GET)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the query from the 'cleaned' version of form data
            query = form.cleaned_data["query"]
            all_entries = util.list_entries()
            search_results = []

            #Search if query in all entries, and return entry if it matches
            if query.lower() in (entry.lower() for entry in all_entries):
                return HttpResponseRedirect(reverse("entry", args=[query]))
            #If it doesn't match, display partial matches on search results page
            else:
                for entry in all_entries:
                    if query.lower() in entry.lower():
                        search_results.append(entry)
                return render(request, "encyclopedia/search.html", {
                    "entries": search_results,
                    "form": SearchForm()
                })

        else:

            # If the form is invalid, re-render the page with existing information.
            return render(request, "encyclopedia/index.html", {
                "form": form
            })

    # If method is POST, re-render the page with exisiting information.
    else:
        return render(request, "encyclopedia/index.html", {
        "form": SearchForm()
        })

def create(request):
    # Check if method is GET, if it is display page
    if request.method == "GET":
        return render(request, "encyclopedia/create.html", {
            "form": SearchForm(),
            "createform": CreateForm()
        })
    else:
        # If method is POST
        # Take in the data the user submitted and save it as form
        form = CreateForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the query from the 'cleaned' version of form data
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            all_entries = util.list_entries()

            #Search if title in all entries, if it is return error
            if title.lower() in (entry.lower() for entry in all_entries):
                return render(request, "encyclopedia/error.html", {
                    "form": SearchForm(),
                    "error_message": f"The page {title} already exists. Please edit the existing page."
                })
            #If it doesn't match, create page
            else:
                #Save an entry 
                util.save_entry(title, (f"# {title}" + ("\n" * 2) + content))
                #Redirect the user to the new page 
                return HttpResponseRedirect(reverse("entry", args=[title]))

        else:
            # If the form is invalid, re-render the page with existing information.
            return render(request, "encyclopedia/create.html", {
                "form": form
            })

def edit(request, title):
    if request.method == "GET":
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "editform": EditForm(initial={'content':util.get_entry(title)}),
            "form": SearchForm()
        })
    else:
        # If method is POST
        # Take in the data the user submitted and save it as form
        form = EditForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():
            # Isolate the variables from the 'cleaned' version of form data
            content = form.cleaned_data["content"]

            #Search if title is in all entries, return error if it is not
            all_entries = util.list_entries()
            if title not in all_entries:
                return render(request, "encyclopedia/error.html", {
                    "form": SearchForm(),
                    "error_message": f"The page {title} doesn't exist. Please create the page before you can edit it."
                })
            else:
                #Save the edit 
                util.save_entry(title, content)
                #Redirect the user to the new page 
                return HttpResponseRedirect(reverse("entry", args=[title]))

        else:
            # If the form is invalid, re-render the page with existing information.
            return render(request, "encyclopedia/edit.html", {
                "title": title,
                "editform": form,
                "form": SearchForm()
            })

def randompage(request):
    title = random.choice(util.list_entries())
    return HttpResponseRedirect(reverse("entry", args=[title]))
    