from app.services.search import ensure_index
if __name__ == "__main__":
    ensure_index()
    print("SearchGrid Elasticsearch index is ready.")
