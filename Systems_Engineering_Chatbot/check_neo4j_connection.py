import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "src/.env"))

class Neo4jConnectionChecker:
    def __init__(self):
        self.uri = os.environ.get("NEO4J_URI")
        self.user = os.environ.get("NEO4J_USERNAME")
        self.password = os.environ.get("NEO4J_PASSWORD")
        self.driver = None

    def check_connection_and_fetch_data(self):
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self.driver.verify_connectivity()
            print("Successfully connected to Neo4j.")
            
            with self.driver.session() as session:
                result = session.run("MATCH (n) RETURN n LIMIT 25")
                print("\n--- Data from Neo4j ---")
                for record in result:
                    node = record["n"]
                    print(f"Labels: {list(node.labels)}, Properties: {dict(node.items())}")
                print("-----------------------\n")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if self.driver is not None:
                self.driver.close()

if __name__ == "__main__":
    checker = Neo4jConnectionChecker()
    checker.check_connection_and_fetch_data()
