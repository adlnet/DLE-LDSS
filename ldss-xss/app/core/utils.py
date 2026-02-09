from .models import NeoAlias, NeoDefinition, NeoContext, NeoContextDescription, NeoTerm, NeoMapping
from deconfliction_service.views import run_deconfliction
import logging
from uuid import uuid4
from deconfliction_service.node_utils import generate_embedding, find_similar_text_by_embedding
from common.utils import antonyms_in_definition, preprocess_definition
from django.http import JsonResponse
from django.core.exceptions import ValidationError
import pandas as pd
from core.constants import REQUIRED_COLUMNS
from core.exceptions import TermCreationError
import magic
import re

logger = logging.getLogger('dict_config_logger')

## Converted from the Perl example provided by SD Elements:
##
##   Only accept legal character sequences. The W3C provides a Perl regular expression to validate printable UTF-8 characters:
##   
##   $field =~ m/\A( 
#       \x09\x0A\x0D\x20-\x7E   # ASCII 
#       | \xC2-\xDF             # non-overlong 2-byte 
#       | \xE0\xA0-\xBF         # excluding overlongs 
#       | \xE1-\xEC\xEE\xEF{2}  # straight 3-byte 
#       | \xED\x80-\x9F         # excluding surrogates 
#       | \xF0\x90-\xBF{2}      # planes 1-3 
#       | \xF1-\xF3{3}          # planes 4-15 
#       | \xF4\x80-\x8F{2}      # plane 16 
#       )*\z/x;
##
allowable_utf8_regex = re.compile(
    br'\A('
    br'[\x09\x0A\x0D\x20-\x7E]|'           # ASCII
    br'[\xC2-\xDF][\x80-\xBF]|'            # non-overlong 2-byte
    br'\xE0[\xA0-\xBF][\x80-\xBF]|'        # excluding overlongs
    br'[\xE1-\xEC\xEE\xEF][\x80-\xBF]{2}|' # straight 3-byte
    br'\xED[\x80-\x9F][\x80-\xBF]|'        # excluding surrogates
    br'\xF0[\x90-\xBF][\x80-\xBF]{2}|'     # planes 1-3
    br'[\xF1-\xF3][\x80-\xBF]{3}|'         # planes 4-15
    br'\xF4[\x80-\x8F][\x80-\xBF]{2}'      # plane 16
    br')*\Z'
)

BAD_CHARS = {
    '\u00A0',  # NO-BREAK SPACE
    '\u202F',  # NARROW NO-BREAK SPACE
    '\u2000', '\u2001', '\u2002', '\u2003', '\u2004', '\u2005', '\u2006',
    '\u2007', '\u2008', '\u2009', '\u200A',  # Various spaces
    '\u205F',  # Medium Mathematical Space
    '\u3000',  # Ideographic Space (full-width)
}

def has_bad_chars(s: str) -> bool:
    return any(c in BAD_CHARS for c in s)

def is_sane_utf8(s: str) -> bool:

    if has_bad_chars(s):
        return False

    try:
        return bool(allowable_utf8_regex.fullmatch(s.encode("utf-8")))
    except UnicodeEncodeError:
        return False

def tokencheck(request):
    api_token = request.headers.get('x-api-token')
    if not api_token:
        return JsonResponse({'error': 'Missing x-api-token header'}, status=400)
    
    # Your view logic here
    return JsonResponse({'message': 'Success'})

def run_node_creation(definition: str, context: str, context_description: str, entity_id, alias: str=None):
    try:
        logger.info('Running Deconfliction')
        definition_vector_embedding, deconfliction_status, most_similar_text, highest_score = run_deconfliction(alias, definition, context, context_description, entity_id)
        if deconfliction_status == 'unique':
            run_unique_definition_creation(definition=definition, context=context, context_description=context_description, definition_embedding=definition_vector_embedding, alias=alias, entity_id=entity_id)
        elif deconfliction_status == 'duplicate':
            run_duplicate_definition_creation(alias=alias, definition=most_similar_text, context=context, context_description=context_description, entity_id=entity_id)
        elif deconfliction_status == 'collision':
            run_collision_definition_creation(alias, most_similar_text, definition, context, context_description, definition_vector_embedding, entity_id=entity_id)

    except Exception as e:
        logger.error(f"Error in run_node_creation: {e}")
        raise e

def run_unique_definition_creation(definition, context, context_description, definition_embedding, alias, entity_id):
    try:
        term_node = NeoTerm.create_new_term(lcvid=entity_id)
        alias_node, _ = NeoAlias.get_or_create(alias=alias) if alias else (None, None)
        definition_node, _ = NeoDefinition.get_or_create(definition=definition, definition_embedding=definition_embedding, entity_id=entity_id)
        context_node, _ = NeoContext.get_or_create(context=context)
        context_description_node, _ = NeoContextDescription.get_or_create(context_description=context_description, context_node=context_node)

        term_node.set_relationships(alias_node=alias_node, definition_node=definition_node, context_node=context_node)
        context_node.set_relationships(term_node=term_node, alias_node=alias_node, definition_node=definition_node, context_description_node=context_description_node)
        definition_node.set_relationships(term_node=term_node, context_node=context_node, context_description_node=context_description_node)
        context_description_node.set_relationships(definition_node=definition_node, context_node=context_node)

        if alias_node:
            alias_node.set_relationships(term_node=term_node, context_node=context_node)

    except Exception as e:
        logger.error(f"Error in run_unique_definition_creation: {e}")
        raise

def run_duplicate_definition_creation(alias, definition, context, context_description, entity_id):
    try:
        alias_node, _ = NeoAlias.get_or_create(alias=alias) if alias else (None, None)
        context_node, _ = NeoContext.get_or_create(context=context) if context else (None, None)
        context_description_node, _ = NeoContextDescription.get_or_create(context_description=context_description, context_node=context_node) if context_description else (None, None)
        definition_node, _ = NeoDefinition.get_or_create(definition=definition, entity_id=entity_id)

        term_node = definition_node.get_term_node()
        logger.info(term_node)
        if not term_node: # Duplicate collision scenario
            if alias_node:
                alias_node.set_relationships(collided_definition=definition_node, context_node=context_node)
            if context_node:
                context_node.set_relationships(alias_node=alias_node, definition_node=definition_node, context_description_node=context_description_node)
            definition_node.set_relationships(context_node=context_node, context_description_node=context_description_node)
            context_description_node.set_relationships(definition_node=definition_node, context_node=context_node)
            return

        # Duplicate scenario with a term node (acts like unique scenario)
        term_node.set_relationships(alias_node=alias_node, definition_node=definition_node)
        if context_node:
            context_node.set_relationships(term_node=term_node, alias_node=alias_node, definition_node=definition_node, context_description_node=context_description_node)

        definition_node.set_relationships(term_node=term_node, context_node=context_node, context_description_node=context_description_node)
        if context_description_node:
            context_description_node.set_relationships(definition_node=definition_node, context_node=context_node)

        if alias_node:
            if not context_node:
                alias_node.set_relationships(term_node=term_node)
            alias_node.set_relationships(term_node=term_node, context_node=context_node)

    except Exception as e:
        logger.error(f"Error in run_duplicate_definition_creation: {e}")
        raise e

def run_collision_definition_creation(alias, most_similar_definition, definition, context, context_description, definition_vector_embedding, entity_id):
    try:
        alias_node = None
        if alias:
            alias_node, _ = NeoAlias.get_or_create(alias=alias)
        
        existing_definition_node, _ = NeoDefinition.get_or_create(definition=most_similar_definition, entity_id=entity_id)
        
        if not existing_definition_node:
            logger.error('Existing definition node not found')
            raise ValueError('Existing definition node not found, checked for: %s' % definition)
        
        colliding_definition_node, _ = NeoDefinition.get_or_create(definition=definition, entity_id=entity_id, definition_embedding=definition_vector_embedding)
        logger.info(f"Colliding Definition Node: {colliding_definition_node}")
        
        if not colliding_definition_node:
            logger.error('Colliding definition node not found')
            raise ValueError('Colliding definition node not found, checked for: %s' % definition)
        
        context_node, _ = NeoContext.get_or_create(context=context)
        context_description_node, _ = NeoContextDescription.get_or_create(context_description=context_description, context_node=context_node)

        alias_node.set_relationships(context_node=context_node, collided_definition=colliding_definition_node)
        context_node.set_relationships(context_description_node=context_description_node, definition_node=colliding_definition_node)
        context_description_node.set_relationships(definition_node=colliding_definition_node)
        colliding_definition_node.set_relationships(context_node=context_node, context_description_node=context_description_node, collision_alias=alias_node, collision=existing_definition_node)

    except Exception as e:
        logger.error(f"Error in run_collision_definition_creation: {e}")
        raise e

def run_mapping(definition, uid_chain, lcvid, uid, aliases):
    try:
        preprocessed_definition = preprocess_definition(definition)

        logger.info(f"Original definition: {definition}")
        logger.info(f"Preprocessed definition: {preprocessed_definition}")

        vector_embedding = generate_embedding(preprocessed_definition)

        similar_texts = find_similar_text_by_embedding(vector_embedding, 'definitions', lcvid)
        most_similar_text = ""

        for similar_text in similar_texts:
            logger.info(f"Similar text: {similar_text}")
            if similar_text[1] >= 0.80 and not antonyms_in_definition(preprocessed_definition, similar_text[0]): # Check for antonyms within the definitions and verify similarity
                most_similar_text = similar_text[0]

        if most_similar_text == "":
            return {
                "status": "no_match",
                "uid_chain": uid_chain,
                "uid": uid,
                "aliases": aliases,
                "lcvid": lcvid,
                "message": "No similar definition found"
            }

        neo_definition_node = NeoDefinition.get_by_definition(definition=most_similar_text)
        if not neo_definition_node:
            raise ValueError(f"Definition node not found for '{most_similar_text}'")

        term_node = neo_definition_node.get_term_node()
        if not term_node:
            raise ValueError(f"Term node missing for definition '{most_similar_text}'")

        neo_mapping_node = NeoMapping.create_node(lcvid=lcvid, uid_chain=uid_chain, uid=uid, definition=definition, aliases=aliases)
        neo_mapping_node.set_relationships(term_node=term_node)

        return {
            "status": "success",
            "uid_chain": uid_chain,
            "lcvid": lcvid,
            "uid": uid,
            "aliases": aliases,
            "mapped_definition": most_similar_text,
        }

    except ValueError as ve:
        logger.error(f"Validation error in run_mapping: {ve}")
        return {
            "status": "error",
            "uid_chain": uid_chain,
            "uid": uid,
            "lcvid": lcvid,
            "message": str(ve)
        }

    except Exception as e:
        logger.exception(f"Unexpected error in run_mapping for UID {uid}: {e}")
        return {
            "status": "error",
            "uid_chain": uid_chain,
            "uid": uid,
            "lcvid": lcvid,
            "message": "Internal processing error"
        }

def find_most_similar_text(similarity_results):
    if not similarity_results:
        return None

    most_similar_text, highest_score = max(similarity_results, key=lambda x: x[1])

    if highest_score >= 0.85:
        return most_similar_text
    else:
        return None

ALLOWED_MIME_TYPES = [
    'text/csv',
    'application/csv',
]

def validate_csv_file(csv_file):

    initial_pos = csv_file.tell()
    header = csv_file.read(2048)
    csv_file.seek(initial_pos)

    detected = magic.from_buffer(header, mime=True)

    if detected not in ALLOWED_MIME_TYPES:
        raise ValidationError(
            f"Unsupported file type: {detected!r}. Please upload a real CSV."
        )

    try:
        logger.info('Validating CSV file...')
        df = pd.read_csv(csv_file)
        logger.info('%s rows found in CSV file.', len(df))
    except pd.errors.EmptyDataError as e:
        raise ValueError('The CSV file is empty.') from e
    except pd.errors.ParserError as e:
        raise ValueError('The CSV file is malformed or not valid.') from e

    missing_columns = check_missing_columns(df)
    if missing_columns:
        raise ValueError(f"The CSV file is missing required columns: {missing_columns}")

    missing_rows = check_missing_rows(df)
    if missing_rows:
        raise ValueError(f"The CSV file is missing required rows: {missing_rows}")

    return {'data_frame': df}

def check_missing_columns(df):
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return missing_columns

def check_missing_rows(df):
    missing_rows = {}

    for index, row in df.iterrows():
        for column in REQUIRED_COLUMNS:
            if pd.isna(row[column]) or row[column].strip() == '':
                if column not in missing_rows:
                    missing_rows[column] = []
                missing_rows[column].append(index + 1)

    return [{'column': column, 'row_indices': indices} for column, indices in missing_rows.items()]

def create_terms_from_csv(df, entity_id):
    logger.info('Creating terms from CSV file...')
    logger.info('%s rows found in data frame file.', len(df))

    for index, row in df.iterrows():
        try:
            alias_value = row['Alias'] if pd.notna(row['Alias']) and row['Alias'] else None
            run_node_creation(alias=alias_value, definition=row['Definition'], context=row['Context'], context_description=row['Context Description'], entity_id=entity_id)
        except Exception as e:
            logger.error('Error creating term for index %s: %s', index, str(e))
            raise TermCreationError(f'Failed to create term for row {index + 1}: {str(e)}') from e

    logger.info('%s terms created from CSV file.', len(df))

def create_missing_row_message(row):
    has_extra = len(row['row_indices']) > 5
    extra_message = " and more" if has_extra else ""
    
    indices_csv = ', '.join(str(col) for col in row['row_indices'][:5])
    message_content = indices_csv + extra_message
    
    return  f"Missing data in column '{row['column']}' for row {message_content}"
