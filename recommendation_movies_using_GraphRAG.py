import argparse
from neo4j import GraphDatabase
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq


def parse_arguments():
    parser = argparse.ArgumentParser(description ='movie.')
    parser.add_argument('-movie',
                    type = str,
                    help ='folder containing pdf files.')
    return parser.parse_args()


groq_api_key = "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"

NEO4J_URI="neo4j+s://7fc49793.databases.neo4j.io"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="zwbt6NESBs9WeBfNbRiBgCp4GNJNblZ2_PcDv9UJuVM"

llm=ChatGroq(groq_api_key=groq_api_key,model_name="Gemma2-9b-It")
llm

# Connect to Neo4j
driver = GraphDatabase.driver(uri=NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# Function to get recommendations
def get_similar_movies(tx, movie_name):
    query ="""
    MATCH (m:Movie {name: $movie_name})-[:`ACTED_IN`]->(a:Actor)<-[:`ACTED_IN`]->(rec:Movie)
    WHERE rec.name <> $movie_name
    RETURN DISTINCT rec.name AS name, rec.plotDescription AS description, rec.imdbRating AS rating
    ORDER BY rating DESC limit 5
    """
    
    result = tx.run(query, movie_name=movie_name)
    return [record.data() for record in result]


class GraphRAGRecommendation:
    def __init__(self, neo4j_driver, llm):
        self.neo4j_driver = neo4j_driver
        self.llm = llm

    def get_graph_recommendations(self, movie_name):
        with self.neo4j_driver.session() as session:
            return session.read_transaction(get_similar_movies, movie_name)

    def generate_recommendations(self, movie_name):
        # Step 1: Graph-based retrieval
        recommendations = self.get_graph_recommendations(movie_name)
        #print(recommendations)
        
        # Step 2: Use LLM for final output
        context = f"Recommendations just movie names from {recommendations}"
        PROMPT_TEMPLATE = """
        Answer the question based only on the following context:

        {context}

        ---


        Answer the question based on the above context: {question}
        """
        prompt_tamplate = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_tamplate.format(context=context, question="recommend 3 movies based on the context.")
        
        return self.llm.invoke(context)

# Initialize the pipeline
def Initiate_pipeline(args):
    pipeline = GraphRAGRecommendation(
        neo4j_driver=driver,
        llm=llm
        )

    result = pipeline.generate_recommendations(args)
    return result.content

if __name__ == "__main__":
    args = parse_arguments()
    res = Initiate_pipeline(args.movie)
    print(res)



# Get recommendations for a movie
#result = pipeline.generate_recommendations("Angaaray")
#print("Final Recommendations:", result.content)

