from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import time
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
embedding_text1 = model.encode("this is a new text")
embedding_text2 = model.encode("this is a new text")
# print(embedding_text)
start1 = time.time()
print(cosine_similarity([embedding_text1], [embedding_text2])[0][0])
start2 = time.time()
print("程序执行时间", start2 - start1)
