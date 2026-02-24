"""MCP tools for the cerebrum module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="cerebrum")
def query_knowledge_base(query: str, limit: int = 5) -> dict:
    """Perform semantic retrieval from the CaseBase.
    
    Args:
        query: The semantic concept or question to search for
        limit: Maximum number of cases to return
        
    Returns:
        Structured retrieval results containing matching cases.
    """
    from codomyrmex.cerebrum import CaseRetriever, CaseBase
    
    try:
        # Assuming a default initialization path
        base = CaseBase()
        retriever = CaseRetriever(base)
        
        # Searching by conceptual similarity (using query as a feature filter)
        results = retriever.retrieve({"concept": query}, k=limit)
        
        formatted_results = []
        for case, score in results:
            formatted_results.append({
                "id": case.id,
                "features": case.features,
                "solution": case.solution,
                "similarity_score": score
            })
            
        return {"status": "success", "results": formatted_results, "count": len(formatted_results)}
    except Exception as e:
        return {"status": "error", "message": f"Knowledge base query failed: {e}"}


@mcp_tool(category="cerebrum")
def add_case_reference(concept: str, solution: str) -> dict:
    """Store intelligence context directly into the CaseBase.
    
    Args:
        concept: The problem or concept feature string
        solution: The paired resolution or insight
        
    Returns:
        Confirmation of case storage.
    """
    from codomyrmex.cerebrum import CaseBase, Case
    
    try:
        base = CaseBase()
        case = Case(features={"concept": concept}, solution=solution)
        base.add_case(case)
        
        return {
            "status": "success", 
            "message": "Case stored successfully",
            "case_id": case.id
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to store case: {e}"}
