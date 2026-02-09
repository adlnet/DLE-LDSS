import logging
import os
import time
from typing import List, Tuple
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from neomodel import db
from django.views.decorators.http import require_http_methods, require_POST
from django.core.exceptions import BadRequest, ValidationError
from core.models import NeoTerm, NeoAlias, NeoDefinition, NeoMapping
from core.utils import run_mapping, validate_csv_file, create_missing_row_message, create_terms_from_csv, is_sane_utf8
from core.exceptions import MissingColumnsError, MissingRowsError, TermCreationError
from deconfliction_service.node_utils import find_similar_text_by_embedding
from common.utils import antonyms_in_definition
from uid.views import fetch_slim_terms
import json

import clamd

from jsonschema import exceptions as jsonschema_exceptions, validate as validate_json

import requests
import traceback

logger = logging.getLogger('dict_config_logger')

CCV = settings.CCV
INSTANCE_ID = settings.INSTANCE_ID

XIA_URLS = os.environ.get('XIA_URLS', '').split(",")
XIA_CATALOG_PATH = os.environ.get('XIA_CATALOG_PATH', '')

CLAM_AV_HOST = os.getenv("CLAM_AV_HOST", "clamav")
CLAM_AV_PORT = int(os.getenv("CLAM_AV_PORT", "3100"))

STR_DATABASE_QUERY_ERROR = "database query error"

P2881_CATALOG_RESULT_TERMS = [
    "Course_ID",
    "Delivery_Method",
    "Description",
    "End_Date",
    "Offered_By",
    "Owned_By",
    "Start_Date",
    "Thumbnail",
    "Title"
]

error_res = {"error": STR_DATABASE_QUERY_ERROR}

def strip_bad_characters(raw_string: str) -> str:
    return raw_string.strip().replace("\x00\x00", "")

def check_status(messages, queryset):
    queryset = queryset.filter(status='published')
    if not queryset:
        message = "Error fetching record, no " \
                  "published record with required parameters"
        messages.append(message)
        logger.error(message)
        raise ObjectDoesNotExist()
    return queryset

@require_http_methods(["GET"])
def check_neo4j_status(request):
    try:
        results, _ = db.cypher_query("RETURN 1 AS result")
        logger.info(results)
        return JsonResponse({
            "status": "OK",
            "message": "Connection to Neo4j successful.",
        })
    except Exception:
        return JsonResponse({
            "status": "ERROR",
            "message": "Neo4j connection failed.",
        }, status=503)

class DataIngest(APIView):
    permission_classes = [AllowAny]
    def post(self, request):

        if request.method != "POST":
            return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

        expected_format = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "definition": {
                        "type": "string",
                        "maxLength": 2000
                    },
                    "uid_chain": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "aliases": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "maxLength": 100
                        }
                    },
                    "lcvid": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "uid": {
                        "type": "string",
                        "maxLength": 100
                    }
                }
            }
        }

        try:
            data = json.loads(request.body)
            logger.info("Data received: %s", data)

            if not isinstance(data, list):
                return JsonResponse({"error": "Expected a list of objects"}, status=400)

            validate_json(instance=data, schema=expected_format)
            
            results = []

            for item in data:
                try:
                    logger.info("Processing item: %s", item)

                    definition = item.get("definition")
                    uid_chain = item.get("uid_chain")
                    aliases = item.get("aliases")
                    lcvid = item.get("lcvid")
                    uid = item.get("uid")

                    if not definition or not lcvid or not uid or not uid_chain:
                        results.append({
                            "uid": uid or "unknown",
                            "status": "error",
                            "message": "Missing required fields"
                        })
                        continue  # Continue to next item instead of failing everything
                    mapping_result = run_mapping(definition, uid_chain, lcvid, uid, aliases)

                    results.append(mapping_result)

                except Exception as item_error:
                    logger.exception("Error processing item with UID %s: %s", item.get('uid', 'unknown'), item_error)
                    results.append({
                        "uid": item.get("uid", "unknown"),
                        "status": "error",
                        "message": "Unexpected error while processing this item"
                    })

            return JsonResponse({"results": results}, status=200)

        except jsonschema_exceptions.ValidationError:
            return JsonResponse({"error": f"Invalid JSON format, expected: {expected_format}"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        except Exception as e:
            logger.exception("Unexpected error in data_ingest_view: %s", e)
            return JsonResponse({"error": INTERNAL_SERVER_ERROR_MESSAGE}, status=500)

INSTANCES = {
    "jko": {
        "url": "https://lcv-a.ldss.tla.adlnet.gov/uid/api/terms/slim",
        "name": "jko",
        "displayName": "JKO"
    },
    "coursera": {
        "url": "https://lcv-b.ldss.tla.adlnet.gov/uid/api/terms/slim",
        "name": "coursera",
        "displayName": "Coursera"
    },
    "p2881": {
        "url": "https://ccv.ldss.tla.adlnet.gov/uid/api/terms/slim",
        "name": "p2881",
        "displayName": "P2881"
    },
    "aetc": {
        "url": "https://ccv.ldss.tla.adlnet.gov/uid/api/terms/slim",
        "name": "aetc",
        "displayName": "AETC"
    }
}

LOCAL_INSTANCES = ["jko", "coursera", "p2881", "aetc"]

INVALID_CHARACTERS_MESSAGE = "Invalid characters included in request."

@require_http_methods(["GET"])
def api_get_instances(request):
    return JsonResponse(INSTANCES)

# Temporary class for hard-coded sources/targets
class Instances:
    def __init__(self):
        # Initialize named dictionaries as attributes of the class
        self.lcv_a = {"url": "https://lcv-a.ldss.tla.adlnet.gov/uid/api/terms", "name": "jko"}
        self.lcv_b = {"url": "https://lcv-b.ldss.tla.adlnet.gov/uid/api/terms", "name": "coursera"}
        self.ccv = {"url": "https://ccv.ldss.tla.adlnet.gov/uid/api/terms", "name": "p2881"}

    def get_dict_by_name(self, target_name):
        for key, value in self.__dict__.items():
            if value.get("name") == target_name:
                return value
        return None

def create_mapping_entry(source_term, target_term):
    entry = {}

    if source_term is not None:
        entry["source"] = {
            "alias": source_term["aliases"][0],
            "definition": source_term["definition"]
        }

    if target_term is not None:
        entry["target"] = {
            "alias": target_term["aliases"][0],
            "definition": target_term["definition"]
        }

    if (target_term is not None) and (source_term is not None):
        entry["relationship"] = True

    return entry

def get_terms_for_instance(name: str) -> List[dict]:

    if name not in INSTANCES and name not in LOCAL_INSTANCES:
        raise BadRequest(f"Unknown instance: {name!r}")

    if name in LOCAL_INSTANCES:
        return fetch_slim_terms(name)
    
    instance = INSTANCES[name]

    response = requests.get(instance["url"], timeout=10)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()
    
@require_http_methods(["GET"])
def api_mapped_nodes(request):

    try:
        source = request.GET.get('source')
        target = request.GET.get('target')

        source_terms = get_terms_for_instance(source)
        target_terms = get_terms_for_instance(target)
        
        if not source_terms or not target_terms:
            return JsonResponse({"error": "No terms found for the given source or target."}, status=404)
        
        source_map = {term["uid_chain"]: term for term in source_terms}
        target_map = {term["uid_chain"]: term for term in target_terms}

    except BadRequest as e:
        logger.error("Bad request: %s", e)
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        logger.error("Error retrieving data from external endpoints")
        logger.error(e)
        logger.error(traceback.print_exc)
        logger.error(traceback.print_exception)
        return JsonResponse({"error": "Term endpoints could not be reached"})

    results: List[List[str]] = []

    paired_source_chains = set()
    paired_target_chains = set()
    logger.info("Starting mapping query")
    # Mapping Query
    #
    # The goal here is to find every mapping between terms that this instance
    # knows about.  Since each instance considers its own terms as NeoTerm nodes,
    # the external terms will be stored as NeoMapping nodes.
    #
    # Actually performing the query with neo4j and its cypher language is simple,
    # as we just provided the expected structure, but that structure will depend on
    # how this instance relates to the source and target contexts.
    #
    # There are two simple cases:
    #   1. We are the source
    #   2. We are the target
    #
    # In eiher of these situations, we can simply query for all terms and mappings
    # within a single jump of each other that belong to those contexts.
    #
    # The slightly more verbose case is if we are neither, and simply posses a term
    # that is being mapped to by the queried contexts.  In this event, we still query
    # based on the structure, but ignore the actual Term node itself and get the mapped
    # UID chains.
    #
    if source == INSTANCE_ID:
        ## Simple Case 1, SOURCE (Terms) --> TARGET (Mappings)
        ##
        logger.info("starting case 1 match query")

        graph_query = """
            MATCH (source_term:NeoTerm)<-[:MAPS_TO]-(target_mapping:NeoMapping)
            WHERE source_term.uid_chain STARTS WITH $source_prefix AND target_mapping.uid_chain STARTS WITH $target_prefix
            RETURN DISTINCT
                source_term.uid_chain AS source_chain,
                target_mapping.uid_chain AS target_chain
        """
    elif target == INSTANCE_ID:
        ## Simple Case 2, SOURCE (Mappings) --> TARGET (Terms)
        ##
        logger.info("starting case 2 match query")
        graph_query = """
            MATCH (source_mapping:NeoMapping)-[:MAPS_TO]->(target_term:NeoTerm)
            WHERE source_mapping.uid_chain STARTS WITH $source_prefix AND target_term.uid_chain STARTS WITH $target_prefix
            RETURN DISTINCT
                source_mapping.uid_chain AS source_chain,
                target_term.uid_chain AS target_chain
        """

    else:
        ## Harder Case, SOURCE (Mappings) -> (Terms) <- TARGET (Mappings)
        ##
        logger.info("starting case 3 match query")
        graph_query = """
            MATCH (source_term:NeoMapping)-[:MAPS_TO]->(_:NeoTerm)<-[:MAPS_TO]-(target_term:NeoMapping)
            WHERE source_term.uid_chain STARTS WITH $source_prefix AND target_term.uid_chain STARTS WITH $target_prefix
            RETURN DISTINCT
                source_term.uid_chain AS source_chain,
                target_term.uid_chain AS target_chain
        """
    try:
        results, _ = db.cypher_query(graph_query, {"source_prefix": source, "target_prefix": target})
    except Exception:
        logger.error("Error executing mapping query:\n%s", traceback.format_exc())
        return JsonResponse({"error": "Mapping query failed"}, status=500)

    output = []
    logger.info("Mapping query results: %s", results)
    for [source_chain, target_chain] in results:
        entry = create_mapping_entry(
            source_map[source_chain],
            target_map[target_chain]
        )

        paired_source_chains.add(source_chain)
        paired_target_chains.add(target_chain)

        output.append(entry)

    for paired_source_chain in paired_source_chains:
        del source_map[paired_source_chain]
    for paired_target_chain in paired_target_chains:
        del target_map[paired_target_chain]

    unmapped_source_entries = [create_mapping_entry(source_map[chain], None) for chain in source_map]
    unmapped_target_entries = [create_mapping_entry(None, target_map[chain]) for chain in target_map]

    output.extend(unmapped_source_entries)
    output.extend(unmapped_target_entries)

    return JsonResponse(output, safe=False)

# Define a function to return catalog data from an lcv
# Move into utils.py later - SP
def get_catalog(provider):
    logger.info("Getting catalog for provider: %s", provider)
    logger.error("Getting catalog for provider: %s", provider)
    if provider == 'coursera':
        provider = 'dau'

    xia_data = {}
    logger.info(XIA_URLS)
    logger.error(XIA_URLS)
    for url in XIA_URLS:
        logger.info("Processing URL: %s", url)
        logger.error(url)
        try:
            if url.strip() == "" or provider not in url:
                continue
            catalog_endpoint = url + XIA_CATALOG_PATH
            catalog_response = requests.get(catalog_endpoint, timeout=10)

            if catalog_response.status_code < 300:
                catalog_data = catalog_response.json()
                catalog_prefix = catalog_data["entity_id"]
                catalog_content = catalog_data["data"]
                xia_data[catalog_prefix] = catalog_content
            else:
                logger.error("Could not retrieve data from: %s", catalog_endpoint)

        except Exception:
            error_message = "Oops! Bad Request!"
            if "_errors" in xia_data:
                xia_data["_errors"].append(error_message)
            else:
                xia_data["_errors"] = [error_message]
    
    return xia_data

# Return all catalog entries from requested xia
@require_http_methods(["GET"])
def api_get_catalog(request):
    xia = request.GET.get('provider')

    if xia is None:
        return HttpResponse("You must include 'provider' query argument", status=400)

    xia = strip_bad_characters(xia)
    valid_chars = is_sane_utf8(xia)
    if not valid_chars:
        return JsonResponse({"error": INVALID_CHARACTERS_MESSAGE}, status=400)

    catalogs = get_catalog(xia)

    if not catalogs or all(len(v) == 0 for k, v in catalogs.items() if k != "_errors"):
        return JsonResponse({"error": "No catalogs found for the specified provider."}, status=404)
    else:
        return JsonResponse(catalogs)

@require_http_methods(["GET"])
def api_get_catalog_entry(request):
    provider = request.GET.get('provider')
    course_id_str = request.GET.get('course_id')  
    if not provider or not course_id_str:
        return HttpResponse("You must include 'provider' and 'course_id' query arguments", status=400)

    if not isinstance(provider, str) or not isinstance(course_id_str, str):
        return HttpResponse("The 'provider' and 'course_id' query arguments must be strings", status=400)
    
    provider = strip_bad_characters(provider)
    course_id_str = strip_bad_characters(course_id_str)

    valid_chars = is_sane_utf8(provider) and is_sane_utf8(course_id_str)
    if not valid_chars:
        return JsonResponse({"error": INVALID_CHARACTERS_MESSAGE}, status=400)

    try:
        try:
            course_id = int(course_id_str)
        except ValueError:
            return HttpResponse("'course_id' must be a valid integer", status=400)

        catalog_data = get_catalog(provider)

        catalogs = catalog_data.get(provider, [])
        catalog = next((item for item in catalogs if item.get("id") == course_id), None)
    
    except Exception:
        return JsonResponse({"error": "Error retrieving catalog entry"}, status=500)
        
    if catalog is not None:
        return JsonResponse(catalog, status=200)
    else:
        return JsonResponse({"error": "Catalog entry not found"}, status=404)

def json_error(message: str, status: int = 400):
    return JsonResponse({"error": message}, status=status)

def get_csv_file_or_400(request):
    if "csv_file" not in request.FILES:
        raise BadRequest("No file uploaded. Missing field: csv_file")
    file = request.FILES["csv_file"]
    if not file.name.lower().endswith(".csv"):
        raise BadRequest("Invalid file type. Only CSV files are allowed.")
    return file

def get_entity_id_or_400(request):
    entity_id = request.POST.get("entity_id")
    if not entity_id:
        raise BadRequest("Missing entity_id in request.")
    return entity_id

def scan_with_clamav_or_400(file, *, host, port):
    cd = clamd.ClamdNetworkSocket(host=host, port=port)
    result = cd.instream(file).get("stream")
    if not result:
        raise BadRequest("Invalid scan result from virus scanner.")
    status = result[0] if isinstance(result, (list, tuple)) else str(result)
    if "OK" not in str(status):
        logger.error("CLAMAV CSV UPLOAD ISSUE - %s", result)
        raise BadRequest(f"Invalid CSV File. CLAMAV: {result}")
    file.seek(0)

def process_csv_or_raise(file, entity_id):
    validation_result = validate_csv_file(csv_file=file)
    df = validation_result["data_frame"]
    create_terms_from_csv(df, entity_id)

@require_POST
def upload_csv(request, use_clamav: bool = True):
    try:
        csv_file = get_csv_file_or_400(request)
        entity_id = get_entity_id_or_400(request)

        if use_clamav:
            scan_with_clamav_or_400(
                csv_file,
                host=CLAM_AV_HOST,
                port=CLAM_AV_PORT,
            )

        process_csv_or_raise(csv_file, entity_id)
        logger.info("Successfully created terms from CSV file.")
        return JsonResponse({"message": "CSV file processed successfully."}, status=200)

    except BadRequest as e:
        return json_error(str(e), status=400)

    except ValidationError as e:
        logger.error("CSV validation error: %s", e)
        return json_error(str(e), status=400)

    except MissingColumnsError as e:
        msg = f"Missing required columns: {', '.join(e.missing_columns)}"
        logger.error(msg)
        return json_error(msg, status=400)

    except MissingRowsError as e:
        row_messages = [create_missing_row_message(row) for row in e.missing_rows]
        msg = row_messages[0] if row_messages else "Missing required rows."
        logger.error(msg)
        return json_error(msg, status=400)

    except TermCreationError:
        logger.error("Error creating terms from CSV file.")
        return json_error("Error creating terms from CSV file.", status=400)

    except Exception as e:
        logger.error("Error processing file: %s", e)
        return json_error("Error processing file.", status=500)

@require_POST
def create_local_mappings(request):
    try:
        source_id, target_id = _parse_entity_ids(request.body)
    except ValueError as e:
        logger.error(str(e))
        return JsonResponse({"error": str(e)}, status=400)

    source_id = strip_bad_characters(source_id)
    target_id = strip_bad_characters(target_id)

    valid_chars = is_sane_utf8(source_id) and is_sane_utf8(target_id)
    if not valid_chars:
        return JsonResponse({"error": INVALID_CHARACTERS_MESSAGE}, status=400)

    result = _run_mapping_generation(source_id, target_id)

    if result["status"] == "error":
        logger.error(result["message"])
        return JsonResponse({"error": result["message"]}, status=result.get("code", 500))

    created = result.get("created", 0)
    msg = f"Successfully created {created} mapping{'s' if created != 1 else ''}."
    return JsonResponse({"status": "success", "created": created, "message": msg}, status=200)


def _parse_entity_ids(body: bytes) -> tuple[str, str]:
    expected_format = {
        "type": "object",
        "properties": {
            "source": {
                "type": "string",
                "maxLength": 20
            },
            "target": {
                "type": "string",
                "maxLength": 20
            }
        },
        "required": ["source", "target"]
    }
    try:
        data = json.loads(body)
        validate_json(instance=data, schema=expected_format)

    except jsonschema_exceptions.ValidationError as ve:
        raise ValueError(f"Invalid JSON format for _parse_entity_ids, expected: {expected_format}") from ve

    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON format.") from exc
    
    source = data.get("source")
    target = data.get("target")
    
    if not source or not target:
        raise ValueError("Both 'source' and 'target' fields are required.")
    
    if not isinstance(source, str) or not isinstance(target, str):
        raise ValueError("Both 'source' and 'target' fields are required.")
    
    source = strip_bad_characters(source)
    target = strip_bad_characters(target)

    valid_chars = is_sane_utf8(source) and is_sane_utf8(target)
    if not valid_chars:
        return JsonResponse({"error": INVALID_CHARACTERS_MESSAGE}, status=400)

    return source, target

INTERNAL_SERVER_ERROR_MESSAGE = "Internal server error. Please try again later."

def _run_mapping_generation(source_entity_id: str, target_entity_id: str) -> dict:
    try:
        service_result = generate_local_mappings(source_entity_id, target_entity_id)
        if service_result.get("status") == "success":
            count = (
                int(service_result.get("message", "").split()[1])
                if "Created" in service_result.get("message", "")
                else 0
            )
            return {"status": "success", "created": count}
        return service_result
    except Exception as e:
        logger.error("Unexpected error in mapping service: %s", e)
        return {"status": "error", "message": INTERNAL_SERVER_ERROR_MESSAGE, "code": 500}


def generate_local_mappings(source_entity_id, target_entity_id):
    try:
        source_terms = NeoTerm.nodes.filter(lcvid=source_entity_id)
        if not source_terms:
            logger.error("No matching terms for source %s", source_entity_id)
            return {"status": "error", "message": "No matching terms found.", "code": 404}
        created = 0
        for term in source_terms:
            definition_node = _get_definition(term)
            if not definition_node:
                continue
            best_text = _find_best_definition_text(definition_node, target_entity_id)
            if not best_text:
                continue
            target_term = _get_target_term(best_text, target_entity_id)
            if not target_term:
                continue
            aliases = [a.alias for a in term.alias.all()]
            if _create_mapping(term, definition_node.definition, aliases, target_term):
                created += 1
        return {"status": "success", "message": f"Created {created} mappings"}
    except Exception as e:
        logger.error("Unexpected error generating mappings: %s", e)
        return {"status": "error", "message": INTERNAL_SERVER_ERROR_MESSAGE, "code": 500}


def _get_definition(term):
    try:
        node = term.definition.single()
        if not node:
            logger.error("Definition missing for %s", term.uid_chain)
            return None
        return node
    except Exception as e:
        logger.error("Error fetching definition for %s: %s", term.uid_chain, e)
        return None


def _find_best_definition_text(def_node, target_entity_id):
    try:
        candidates = find_similar_text_by_embedding(
            input_embedding=def_node.embedding, 
            index_name="definitions", 
            entity_id=target_entity_id
        ) or []
    except Exception as e:
        logger.error("Embedding search failed for definition %s: %s", def_node.definition, e)
        return None
    best_text = None
    best_score = 0.0
    for text, score in candidates:
        if score >= 0.8 and not antonyms_in_definition(def_node.definition, text):
            if score > best_score:
                best_score = score
                best_text = text
    return best_text


def _get_target_term(def_text, target_entity_id):
    try:
        def_node = NeoDefinition.nodes.get_or_none(
            definition=def_text, entity_id=target_entity_id
        )
        if not def_node:
            logger.error("Definition node not found for %s", def_text)
            return None
        term_node = def_node.get_term_node()
        if not term_node:
            logger.error("Term node missing for definition %s", def_text)
            return None
        return term_node
    except Exception as e:
        logger.error("Error retrieving target term for %s: %s", def_text, e)
        return None


def _create_mapping(source_term, definition_text, aliases, target_term):
    try:
        mapping = NeoMapping.create_node(
            uid_chain=source_term.uid_chain,
            lcvid=source_term.lcvid,
            uid=source_term.uid,
            definition=definition_text,
            aliases=aliases
        )
        mapping.set_relationships(term_node=target_term)
        return True
    except Exception as e:
        logger.error("Failed mapping %s -> %s: %s", source_term.uid_chain, target_term.uid_chain, e)
        return False
    