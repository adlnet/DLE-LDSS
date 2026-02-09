from neomodel import db
import logging
from core.constants import MODEL_VECTOR_DIMENSION
from common.model_loader import get_semantic_model
logger = logging.getLogger('dict_config_logger')

def generate_embedding(text: str) -> list:
    try:
        if not text or not isinstance(text, str):
            raise ValueError("Invalid input: Text must be a non-empty string.")
        semantic_model = get_semantic_model()
        embedding = semantic_model.encode(text, normalize_embeddings=True).tolist()
        logger.info(f"Embedding generated successfully for text: {text}")
        return embedding

    except ValueError as ve:
        logger.error(f"ValueError in generate_embedding: {ve}")
        raise  # Reraise the exception for upstream handling

    except Exception as e:
        logger.error(f"Unexpected error in generate_embedding: {e}")
        raise RuntimeError("Failed to generate embedding due to an unexpected error.") from e

def get_terms_with_multiple_definitions():
    cypher_query = """
    MATCH (t:NeoTerm)-[:POINTS_TO]->(d:NeoDefinition)
    WITH t, COUNT(d) AS definition_count
    WHERE definition_count > 1
    RETURN {
    term_uid: t.uid,
    count: definition_count
    }
    """
    results, _ = db.cypher_query(cypher_query)

    logger.info(f"Results: {results}")

    return results

def show_current_vector_indeces():
    try:
        cypher_query = """
        SHOW INDEXES WHERE type = "VECTOR"
        """

        logger.info(f"Current vector indeces: {db.cypher_query(cypher_query)}")
    except Exception as e:
        logger.error(f'Error showing vector indeces: {e}')
        raise e

def create_vector_index(index_name, node_name, embedding_field_name='embedding'):
    try:
        cypher_query = f"""
        CREATE VECTOR INDEX `{index_name}` IF NOT EXISTS
        FOR (n:{node_name})
        ON (n.{embedding_field_name})
        OPTIONS {{
            indexConfig: {{
                `vector.dimensions`: {MODEL_VECTOR_DIMENSION},
                `vector.similarity_function`: 'cosine'
            }}
        }}
        """

        results, _ = db.cypher_query(cypher_query)
        show_current_vector_indeces()
    except Exception as e:
        logger.error(f'Error creating vector index: {e}')
        raise e

def find_similar_text_by_embedding(
    input_embedding,
    index_name,
    entity_id,
    desired_count: int = 20,
    max_k: int = 1000,
):
    if (
        not isinstance(input_embedding, list)
        or not all(isinstance(x, (int, float)) for x in input_embedding)
    ):
        logger.error("Invalid input_embedding: Must be a list of numbers.")
        return {"error": "Invalid input_embedding: Must be a list of numbers."}

    def _query(k: int) -> list[tuple[str, float]]:
        cypher = """
            CALL db.index.vector.queryNodes($index, $k, $emb)
            YIELD node, score
            WHERE node.entity_id = $eid
            RETURN node.definition AS text, score
            ORDER BY score DESC
            LIMIT $k
        """
        params = {
            "index": index_name,
            "k": k,
            "emb": input_embedding,
            "eid": entity_id,
        }
        rows, _ = db.cypher_query(cypher, params)
        return [(row[0], float(row[1])) for row in rows]

    low, high = desired_count, max_k
    best_hits = None

    try:
        while low <= high:
            mid = (low + high) // 2
            hits = _query(mid)
            if len(hits) < desired_count:
                low = mid + 1
            else:
                best_hits = hits
                high = mid - 1

        final = best_hits or hits or []
        return final[:desired_count]

    except Exception as e:
        logger.error("Unexpected error in find_similar_text_by_embedding: %s", e, exc_info=True)
        return {"error": "Unexpected error occurred", "details": str(e)}

def find_colliding_definition_nodes():
    cypher_query = """
    MATCH (n:NeoDefinition)-[:IS_COLLIDING_WITH]->(m:NeoDefinition)
    RETURN {
        definition_1: m.definition,
        entity_id_1: m.entity_id,
        id_1: id(m),
        definition_2: n.definition,
        entity_id_2: n.entity_id,
        id_2: id(n)
    } as collision
    """

    results, _ = db.cypher_query(cypher_query)
    return results

def evaluate_deconfliction_status(similarity_results):

    if not similarity_results:
        return 'unique', None, None

    most_similar_text, highest_score = max(similarity_results, key=lambda x: x[1])

    logger.info(f"Most similar text: {most_similar_text}")
    if is_unique(highest_score):
        return 'unique', None, None
    if is_duplicate(highest_score):
        return 'duplicate', most_similar_text, highest_score
    if is_collision(highest_score):
        return 'collision', most_similar_text, highest_score
    else:
        return 'unique', None, None

def is_duplicate(similarity_score: float):
    return similarity_score >= 0.95

def is_collision(similarity_score: float):
    return 0.92 > similarity_score > 0.83

def is_unique(similarity_score: float):
    return similarity_score < 0.83
