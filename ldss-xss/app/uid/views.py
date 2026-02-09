import json
import logging
from neomodel import db
from .models import UIDNode, UIDRequestNode
from .models import report_all_uids, report_all_generated_uids, report_uids_by_echelon, GeneratedUIDLog
from rest_framework import viewsets
from rest_framework.response import Response

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages

from django.views.decorators.http import require_http_methods, require_safe

from core.models import NeoTerm
from core.utils import tokencheck
# Set up logging to capture errors and important information
logger = logging.getLogger('dict_config_logger')

MAX_CHILDREN = 2**32 -1

def strip_bad_characters(raw_string: str) -> str:
    return raw_string.strip().replace("\x00\x00", "")

# Create your views here.

@require_http_methods(["POST"])
def generate_uid_node(request: HttpRequest):
    request_body = json.loads(request.body)
    # print(request_body)
    parent_uid = request_body.get('parent_uid', None)
    
    if isinstance(parent_uid, str):
        parent_uid = strip_bad_characters(parent_uid)

    new_child_node = UIDNode.create_node(parent_uid)

    return HttpResponse("{ 'uid': '" + str(new_child_node.uid) + "' }", content_type='application/json')

# Report Generation by echelon
@require_http_methods(["GET"])
def generate_report(request, echelon_level=None):
    if echelon_level == "root": # Getting all root level UID for echelon report
        uids = report_all_uids()
    else:
        # Retrieve UIDs based on the specified echelon level
        uids = report_uids_by_echelon(echelon_level)

    return JsonResponse({'uids': uids})

# Create API endpoint to share current UID repo
class UIDRepoViewSet(viewsets.ViewSet):
    def list(self, request):
        # Retrieve all UIDs from the GeneratedUIDLog model
        uids = GeneratedUIDLog.objects.all()
        uid_data = [{'uid': log.uid, 'generated_at': log.generated_at, 'generator_id': log.generator_id} for log in uids]
        return Response(uid_data)

@require_http_methods(["GET"])
def report_generated_uids(request):
    # Retrieve all UIDs from the GeneratedUIDLog model
    uid_data = report_all_generated_uids()
    return JsonResponse(uid_data, safe=False)

@require_http_methods(["POST"])
def api_generate_uid(request: HttpRequest):
    payload = json.loads(request.body.decode("utf-8"))
    
    if "provider_name" not in payload:
        return JsonResponse({"message": "You must specify a 'provider_name' when requesting a UID."}, status=400)

    given_provider = payload["provider_name"]

    if not isinstance(given_provider, str):
        return JsonResponse({"message": "Param 'provider_name' must be a string less than 100 characters long."}, status=400)
    if len(given_provider) >= 100:
        return JsonResponse({"message": "Param 'provider_name' must be a string less than 100 characters long."}, status=400)

    given_provider = strip_bad_characters(given_provider)

    if "bulk" in payload:
        given_bulk = payload["bulk"]
        if not isinstance(given_bulk, int):
            return JsonResponse({"message": "Param 'bulk' must be an integer between 0 and 100."}, status=400)
        if (given_bulk <= 0) or given_bulk > 100:
            return JsonResponse({"message": "Param 'bulk' must be an integer between 0 and 100."}, status=400)
        
        request_nodes = [UIDRequestNode.create_requested_uid(given_provider) for _ in range(given_bulk)]
        return JsonResponse([
            {
                "token": node.token,
                "uid": node.default_uid,
                "uid_chain": node.default_uid_chain
            }
            for node in request_nodes
        ], safe=False)
        
    else:
        request_node = UIDRequestNode.create_requested_uid(given_provider)
        return JsonResponse({
            "token": request_node.token,
            "uid": request_node.default_uid,
            "uid_chain": request_node.default_uid_chain
        })
    
    # except Exception as ex:
    #     return HttpResponse(f"Could not process request: {ex}")

@require_http_methods(["GET"])
def api_terms(request: HttpRequest):
    tokencheck(request)
    neoterm_nodes = NeoTerm.nodes.all()
    if not neoterm_nodes:
        messages.error(request, "There is no data to export.")
        return JsonResponse([], safe=False, status=200)
    
    data = []
    
    for neoterm in neoterm_nodes:
        
        term = {}

        term['uid'] = neoterm.uid
        term['uid_chain'] = neoterm.uid_chain
        term["term"] = neoterm.term

        aliases = neoterm.alias.all() 
        term['aliases'] = [alias.alias for alias in aliases]

        definitions = neoterm.definition.all()
        if definitions:
            term['definition'] = definitions[0].definition

        contexts = neoterm.context.all()
        term['contexts'] = []

        for context in contexts:
            context_info = {
                'context': context.context 
            }

            context_description_nodes = context.context_description.all()
            if context_description_nodes:
                context_info['context_description'] = context_description_nodes[0].context_description
            
            term['contexts'].append(context_info)

        logger.info(term)

        data.append(term)

    response = JsonResponse(data, safe=False, json_dumps_params={'indent': 4})
    response['Content-Disposition'] = 'attachment; filename="terms.json"'
    return response

@require_http_methods(["GET"])
def api_terms_slim(request: HttpRequest):
    prefix = request.GET.get('prefix')
    if not prefix:
        return JsonResponse([], safe=False, status=400)
    if not isinstance(prefix, str):
        return JsonResponse([], safe=False, status=400)

    prefix = strip_bad_characters(prefix)

    try:
        output = fetch_slim_terms(prefix)
    except Exception:
        return JsonResponse({"error": "Internal error fetching terms"}, status=500)

    logger.info("slim query executed! returned %d values", len(output))
    response = JsonResponse(output, safe=False, json_dumps_params={'indent': 4})
    response['Content-Disposition'] = 'attachment; filename="terms.json"'
    return response

def fetch_slim_terms(prefix: str) -> list:
    """
    Fetch slim terms for a given UID prefix, including contexts, definitions, and aliases.
    Returns a list of dicts matching the JSON shape expected by the API.
    """

    slim_query = """
    MATCH (term:NeoTerm)
    WHERE split(term.uid_chain, "-")[0] = $prefix
    OPTIONAL MATCH (term)<-[:IS_A]-(context:NeoContext)
    OPTIONAL MATCH (term)-[:POINTS_TO]->(definition:NeoDefinition)
    OPTIONAL MATCH (term)<-[:POINTS_TO]-(alias:NeoAlias)
    RETURN DISTINCT
        context.context       AS context_property,
        definition.definition AS definition_property,
        term.uid_chain        AS term_uid_chain,
        alias.alias           AS alias_property
    """
    params = {"prefix": prefix}
    results, _ = db.cypher_query(slim_query, params)

    output = []
    for context_prop, definition_prop, uid_chain, alias_prop in results:
        output.append({
            "contexts": {
                "context": context_prop,
                "contextDescription": context_prop
            },
            "definition": definition_prop,
            "uid_chain": uid_chain,
            "aliases": [alias_prop] if alias_prop else [],
        })

    logger.info("slim query executed! returned %d values", len(output))
    logger.info("output: %s", output)
    return output
