import chromadb
import ollama
from retrieve import get_raw_content
import sys

url="https://raw.githubusercontent.com/knative/func/main/docs/function-templates/python.md"
url2="https://context7.com/knative/docs/llms.txt?topic=functions"
documents = [
    get_raw_content(url),
    get_raw_content(url2),
]

### 1) Generate embeddings
client = chromadb.Client()
collection = client.create_collection(name="docs")

for i, d in enumerate(documents):
    response = ollama.embed(model="mxbai-embed-large",input=d)
    embeddings = response["embeddings"]
    collection.add(
            ids=[str(i)],
            embeddings=embeddings,
            documents=[d]
            )

##### 2) Retrieve
### embed the prompt and retrieve the most relevant info
prompt = "How can I run my Function?"
resp = ollama.embed(model="mxbai-embed-large",input=prompt)

results = collection.query(
        query_embeddings=resp["embeddings"],
        n_results=1
        )

data = results['documents'][0][0]

### Generate
output = ollama.generate(
        model="llama3.2:3b",
        prompt=f"Using this data: {data}, respond to prompt: {prompt}"
        )

print(output['response'])
