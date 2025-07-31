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

### 2) Retrieve
prompt = "What is the Knative Python Function?"
output = ollama.generate(
        model="llama3.2:3b",
        prompt=prompt
        )

print(output['response'])
