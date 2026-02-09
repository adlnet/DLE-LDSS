import os
from neomodel import config, db
import neo4j

def configure_neo4j(neo4j_host, neo4j_port, neo4j_user, neo4j_password, neo4j_database):

    neo4j_url = f"bolt://{neo4j_host}:{neo4j_port}"

    driver = neo4j.GraphDatabase.driver(
        neo4j_url, 
        auth=(neo4j_user, neo4j_password),
        max_connection_lifetime=3600,
        max_connection_pool_size=50,
        connection_acquisition_timeout=60
    )
    
    config.DRIVER = driver
    config.DATABASE_NAME = neo4j_database
   
    db.set_connection(driver=driver)

    return driver
