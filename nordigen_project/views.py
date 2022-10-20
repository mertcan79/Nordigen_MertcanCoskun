from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from nordigen import NordigenClient
import config
from uuid import uuid4
from django.shortcuts import redirect
from django.http import JsonResponse
from dataclasses import dataclass
import json
from celery import shared_task

'''

    Main script to run the logic of the program. Connects to the config.py file to get credentials and country.
    Connects to the selected bank, user enters credentials of that bank.
    Redirects to the django app where user can see details of their account in a JSON format.
    
'''


@dataclass
class Credentials:
    ID: str
    Secret: str
    country: str


creds = Credentials(config.ID, config.Secret, config.country)
REDIRECT_URI = 'http://127.0.0.1:8000/results'

# Get Nordigen client class and generate token.
def get_client():
    client_output = NordigenClient(
        secret_id=creds.ID,
        secret_key=creds.Secret)
    client_output.generate_token()
    return client_output


client = get_client()

# Get list of institutions and showcase them through index.html template.
def home(request: HttpRequest) -> HttpResponse:
    institution_list = client.institution.get_institutions(country=creds.country)
    context = {'list': json.dumps(institution_list)}
    return render(request, "index.html", context=context)

# Get institution ID and redirect to the result page.
def agreements(request: HttpRequest, institution_id: str) -> redirect:
    if institution_id:
        init = client.initialize_session(
            institution_id=institution_id,
            redirect_uri=REDIRECT_URI,
            reference_id=str(uuid4())
        )
        redirect_url = init.link
        request.session["req_id"] = init.requisition_id

        return redirect(redirect_url)

    return redirect("/", permanent=False)

# Return JSON response of details of each account a user has.
@shared_task
def results(request: HttpRequest) -> JsonResponse:
    if "req_id" in request.session:
        accounts = client.requisition.get_requisition_by_id(requisition_id=request.session["req_id"])["accounts"]
        accounts_data = []
        for id in accounts:
            account = client.account_api(id)
            metadata = account.get_metadata()
            transactions = account.get_transactions()
            details = account.get_details()
            balances = account.get_balances()

            accounts_data.append(
                {
                    "metadata": metadata,
                    "details": details,
                    "balances": balances,
                    "transactions": transactions,
                }
            )

        return JsonResponse(accounts_data)
    else:
        raise Exception("Requisition ID is not found.")
