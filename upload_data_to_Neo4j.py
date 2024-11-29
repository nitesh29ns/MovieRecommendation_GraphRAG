from neo4j import GraphDatabase

NEO4J_URI="neo4j+s://7fc49793.databases.neo4j.io"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="zwbt6NESBs9WeBfNbRiBgCp4GNJNblZ2_PcDv9UJuVM"


AUTH = (NEO4J_USERNAME, NEO4J_PASSWORD)
with GraphDatabase.driver(NEO4J_URI, auth=AUTH) as driver:
    driver.verify_connectivity()


driver.execute_query("""
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/nitesh29ns/MovieRecommendation_GraphRAG/refs/heads/main/input_data.csv' AS row
CREATE (m:Movie {
    imdbId: row.`imdb-id`,
    name: row.movie_name,
    yearOfRelease: toInteger(row.year_of_release),
    runtime: toInteger(row.runtime),
    imdbRating: toFloat(row.IMDB_rating),
    noOfVotes: toInteger(row.no_of_votes),
    plotDescription: row.plot_description
})
MERGE (d:Director {name: row.director})
MERGE (m)-[:DIRECTED_BY]->(d)
WITH m, row
UNWIND split(row.actors, ',') AS actorName
MERGE (a:Actor {name: trim(actorName)})
MERGE (m)-[:ACTED_IN]->(a);
                     """)