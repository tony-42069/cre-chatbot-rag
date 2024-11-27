import azure.functions as func
import streamlit as st

def main(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        "This is the API endpoint for the CRE Knowledge Assistant",
        status_code=200
    )
