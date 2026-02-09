import logging

from django.shortcuts import render, redirect
from django.contrib import messages
from neomodel import db
from common.utils import preprocess_definition

from .node_utils import create_vector_index, find_colliding_definition_nodes, find_similar_text_by_embedding, generate_embedding, evaluate_deconfliction_status, get_terms_with_multiple_definitions
from core.models import NeoDefinition, NeoTerm

from django.views.decorators.http import require_POST, require_http_methods

logger = logging.getLogger('dict_config_logger')

admin_deconfliction_redirect = 'admin:admin_deconfliction_view'

def run_deconfliction(alias: str, definition: str, context: str, context_description: str, entity_id: str):
    try:
        preprocessed_definition = preprocess_definition(definition)
        definition_vector_embedding = generate_embedding(preprocessed_definition)
        create_vector_index('definitions', 'NeoDefinition', 'embedding')
        results = find_similar_text_by_embedding(definition_vector_embedding, 'definitions', entity_id)
        deconfliction_status, most_similar_text, highest_score = evaluate_deconfliction_status(results)
        if deconfliction_status == 'unique':
            return definition_vector_embedding, deconfliction_status, None, None
        return definition_vector_embedding, deconfliction_status, most_similar_text, highest_score
    except Exception as e:
        logger.error(f"Error in run_deconfliction: {e}")
        raise e

def deconfliction_admin_view(request):
    try:
        duplicates = get_duplicate_definitions()
        collisions = find_colliding_definition_nodes()
        deviations = get_terms_with_multiple_definitions()

        collision_data = []
        for result in collisions:
            collision = result[0]
            collision_data.append({
                'definition_1': collision['definition_1'],
                'definition_2': collision['definition_2'],
                'id_1': collision['id_1'],
                'id_2': collision['id_2'],
                'entity_id_1': collision['entity_id_1'],
                'entity_id_2': collision['entity_id_2'],
            })

        deviation_data = []
        for result in deviations:
            deviation = result[0]
            deviation_data.append(deviation)

        context = {
            'collisions': collision_data,
            'duplicates': duplicates,
            'deviations': deviation_data,
        }
        return render(request, 'admin/deconfliction_service/deconfliction_admin.html', context)
    except Exception as e:
        logger.error(f"Error in deconfliction_admin_view: {e}")
        messages.error(request, "Error loading deconfliction view")
        return render(request, 'admin/deconfliction_service/deconfliction_admin.html', {
            'collisions': [],
            'duplicates': [],
            'deviations': [],
            'non_atomic_definitions': []
        })


def resolve_duplicate(request, term_id, definition_id):
    try:
        cypher_query = """
        MATCH (t:NeoTerm)-[r:POINTS_TO]->(d:NeoDefinition)
        WHERE id(t) = $term_id AND id(d) = $definition_id
        DELETE r
        RETURN count(r) as deleted_relationships
        """
        results, _ = db.cypher_query(cypher_query, {
            'term_id': term_id,
            'definition_id': definition_id
        })
        deleted_count = results[0][0]

        if deleted_count > 0:
            logger.info(f"Successfully removed relationship between term {term_id} and definition {definition_id}")
            messages.success(request, "Successfully resolved the duplicate relationship.")
        else:
            logger.warning(f"No relationship found between term {term_id} and definition {definition_id}")
            messages.warning(request, "No relationship found between this term and definition.")

        return redirect(admin_deconfliction_redirect)
    except Exception as e:
        logger.error(f"Error resolving duplicate for term {term_id} and definition {definition_id}: {e}")
        messages.error(request, f"Error resolving duplicate: {str(e)}")
        return redirect(admin_deconfliction_redirect)

def resolve_collision(request, definition_1, definition_2, entity_id_1, entity_id_2):
    try:
        logger.info(f"Resolving collision between definitions {definition_1} and {definition_2}")
        definition_node_1 = NeoDefinition.nodes.get_or_none(definition=definition_1, entity_id=entity_id_1)
        definition_node_2 = NeoDefinition.nodes.get_or_none(definition=definition_2, entity_id=entity_id_2)
        if definition_node_1 is None or definition_node_2 is None:
            logger.warning(f"Could not find definitions with definitions {definition_1} and {definition_2}")
            messages.warning(request, "Could not find definitions with these IDs.")
            return redirect(admin_deconfliction_redirect)

        term_1_list = definition_node_1.term.all()

        context_nodes_1 = definition_node_1.context.all()
        context_nodes_2 = definition_node_2.context.all()

        contexts_1 = [context.context for context in context_nodes_1]
        contexts_2 = [context.context for context in context_nodes_2]

        collided_aliases = []
        collided_definition_alias_node = definition_node_2.collision_alias.all()
        collided_aliases = [alias.alias for alias in collided_definition_alias_node]

        term_1_object = term_1_list[0] if term_1_list else None

        aliases_1 = []
        if term_1_object:
            term_aliases = term_1_object.alias.all()
            aliases_1 = [alias.alias for alias in term_aliases]

        context = {
            'aliases_1': aliases_1,
            'aliases_2': collided_aliases,
            'definition_1': definition_node_1,
            'definition_2': definition_node_2,
            'context_1': contexts_1,
            'context_2': contexts_2,
            'entity_id_1': entity_id_1,
            'entity_id_2': entity_id_2
        }

        return render(request, 'admin/deconfliction_service/decollision.html', context)
 
    except Exception as e:
        logger.error(f"Error resolving collision between nodes {definition_1} and {definition_2}: {e}")
        messages.error(request, f"Error resolving collision: {str(e)}")
        return redirect(admin_deconfliction_redirect)

def get_duplicate_definitions():
    """Find NeoDefinition nodes that have the same definition text"""
    cypher_query = """
    MATCH (d1:NeoDefinition)
    MATCH (d2:NeoDefinition)
    WHERE d1.definition = d2.definition 
    AND d1.entity_id = d2.entity_id
    AND id(d1) < id(d2)  // This ensures we don't get reciprocal matches
    WITH d1.definition as definition_text, 
         collect(DISTINCT id(d1)) + collect(DISTINCT id(d2)) as definition_ids
    RETURN definition_text, definition_ids
    """
    results, _ = db.cypher_query(cypher_query)

    duplicates_data = []
    for definition_text, definition_ids in results:

        terms_query = """
        MATCH (t:NeoTerm)-[:POINTS_TO]->(d:NeoDefinition)
        WHERE id(d) IN $definition_ids
        RETURN t.text as term_text, id(t) as term_id, id(d) as definition_id
        """
        terms_results, _ = db.cypher_query(terms_query, {'definition_ids': definition_ids})

        terms_by_definition = {}
        for term_text, term_id, definition_id in terms_results:
            if definition_id not in terms_by_definition:
                terms_by_definition[definition_id] = []
            terms_by_definition[definition_id].append({
                'text': term_text,
                'id': term_id
            })

        duplicates_data.append({
            'definition_text': definition_text,
            'definition_ids': definition_ids,
            'terms_by_definition': terms_by_definition
        })

    return duplicates_data
@require_http_methods(["GET"])
def merge_duplicate_definitions(request, keep_id, remove_id):
    """Merge two duplicate definitions by redirecting all relationships to the kept definition"""
    try:
        merge_query = """
        // Get the definition we want to keep
        MATCH (keep:NeoDefinition)
        WHERE id(keep) = $keep_id
        
        // Get the definition we want to remove
        MATCH (remove:NeoDefinition)
        WHERE id(remove) = $remove_id
        
        // Find all terms pointing to the definition we want to remove
        OPTIONAL MATCH (t:NeoTerm)-[r:POINTS_TO]->(remove)
        
        // Create new relationships to the definition we're keeping
        WITH keep, remove, collect(t) as terms
        FOREACH (term IN terms | 
          MERGE (term)-[:POINTS_TO]->(keep)
        )
        
        // Delete the old node and all its relationships
        DETACH DELETE remove
        
        RETURN size(terms) as redirected_relationships
        """

        results, _ = db.cypher_query(merge_query, {
            'keep_id': keep_id,
            'remove_id': remove_id
        })

        redirected_count = results[0][0]
        logger.info(f"Successfully merged definitions. Redirected {redirected_count} relationships.")
        messages.success(request, f"Successfully merged definitions. Redirected {redirected_count} relationships.")

    except Exception as e:
        logger.error(f"Error merging definitions {keep_id} and {remove_id}: {e}")
        messages.error(request, f"Error merging definitions: {str(e)}")

    return redirect(admin_deconfliction_redirect)

@require_POST
def admin_upgrade_definition(request, definition, entity_id):

    try:
        logger.info('UPGRADING DEFINITION TO TERM')
        definition_node = NeoDefinition.nodes.get_or_none(definition=definition, entity_id=entity_id)
        if definition_node is None:
            messages.warning(request, "Could not find definition with this text.")
            return redirect(admin_deconfliction_redirect)

        logger.info(f"Upgrading definition '{definition}' to a term.")

        logger.info("Creating new term node.")

        term_node = NeoTerm.create_new_term(lcvid=entity_id)
        context_nodes = definition_node.context.all()

        for context_node in context_nodes:
            term_node.context.connect(context_node)
            context_node.term.connect(term_node)

        logger.info(term_node)

        alias_nodes = definition_node.collision_alias.all()

        for alias_node in alias_nodes:
            term_node.alias.connect(alias_node)
            alias_node.term.connect(term_node)

        term_node.definition.connect(definition_node)
        definition_node.term.connect(term_node)

        definition_node.collision_alias.disconnect_all()
        definition_node.collision.disconnect_all()

        logger.info(f"Successfully upgraded definition '{definition}' to a term.")
        messages.success(request, "Definition successfully upgraded to a term.")
        return redirect(admin_deconfliction_redirect)
    except Exception as e:
        logger.error(f"Error upgrading definition '{definition}': {e}")
        messages.error(request, "Error upgrading definition.")
        return redirect(admin_deconfliction_redirect)

def get_non_atomic_definitions():
    """Find NeoDefinition nodes that contain coordinating conjunctions"""
    try:

        definitions = NeoDefinition.nodes.all()

        non_atomic_definitions = []

        coordinating_conjunctions = {
            ' and ', ' or ', ' but ', ' nor ', ' for ', ' yet ', ' so ', ' with '
        }

        for definition in definitions:
            associated_terms = definition.term.all()

            term = associated_terms[0] if associated_terms else None

            if term is None:
                logger.warning(f"No associated term found for definition {definition}")
                continue

            try:
                padded_text = f' {definition.definition} '

                found_conjunctions = [
                    conj.strip() 
                    for conj in coordinating_conjunctions 
                    if conj in padded_text.lower()
                ]

                if len(found_conjunctions) > 0 and not term.deprecated:

                    non_atomic_definitions.append({
                        'definition': definition.definition,
                        'term': term,
                        'conjunctions': found_conjunctions
                    })

            except Exception as e:
                logger.error(f"Error processing definition {definition}: {e}")
                continue

        return non_atomic_definitions
    except Exception as e:
        logger.error(f"Error in getting atomic definitions: {e}")
        return []


@require_http_methods(["GET"])
def deprecate_term_and_definition(request, term_uid):

    try:
        term_node = NeoTerm.nodes.get_or_none(uid=term_uid)

        if not term_node:
            messages.warning(request, "No term found for this definition.")
            return redirect(admin_deconfliction_redirect)

        term_node.deprecated = True
        term_node.save()

        messages.success(request, "Successfully deprecated definition.")
        return redirect(admin_deconfliction_redirect)

    except Exception as e:
        logger.error(f"Error deprecating definition: {e}")
        messages.error(request, f"Error deprecating definition: {str(e)}")
        return redirect(admin_deconfliction_redirect)
