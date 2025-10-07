from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

embedding_model = OpenAIEmbeddings()
vectorstore = FAISS.load_local("full_index", embedding_model, allow_dangerous_deserialization=True)


def semantic_search(query: str, category: str, limit: int = 3) -> str:
    """
    Search for relevant documents inside a certain category based on the query.
    
    Args:
        query: The search query
        category: The category to filter results ("math", "science", "history", "literature" or "art")
        limit: Maximum number of documents to return (default: 3)
    
    Returns:
        Formatted string with relevant documents
    """
    try:
        results = vectorstore.similarity_search_with_score(
            query, 
            k=limit, 
            filter={"category": category}
        )
        
        if not results:
            return "No relevant documents found for your query."
        
        formatted_results = "**Relevant chunks:**\n\n"
        for i, (doc, score) in enumerate(results, 1):
            formatted_results += f"{i}. Source: {doc.metadata['source']}.\n"
            formatted_results += f"Category: {doc.metadata['category']}.\n"
            formatted_results += f"Score: {score})\n"
            formatted_results += f"Content:\n{doc.page_content}\n\n"
        
        return formatted_results
    except Exception as e:
        return f"Error searching {category} documents: {str(e)}"