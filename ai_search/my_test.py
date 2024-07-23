import chromadb
chromadb_client = chromadb.PersistentClient(path="/home/data/ssd-1/zy/dooyeed/")
collection = chromadb_client.get_or_create_collection(name="AI_search")

result = collection.get(limit=10)
print(len(result['ids']))
# print(result)

