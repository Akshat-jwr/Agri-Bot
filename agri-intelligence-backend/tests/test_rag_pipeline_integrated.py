import asyncio
import pytest
from app.tools.rag_core.query_classifier import query_classifier
from app.tools.vector_tools.semantic_search import search_tool
from app.tools.rag_core.rag_orchestrator import process_agricultural_query

classifier_cases = [
    ("Will heavy rain next week affect wheat yield in Punjab?", "weather_impact"),
    ("Best fertilizer dose for rice nitrogen application", "fertilizer_optimization"),
    ("What is the current mandi price for cotton?", "market_price_forecasting"),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("query,expected_primary", classifier_cases)
async def test_query_classifier_primary(query, expected_primary):
    c = await query_classifier.classify_query(query)
    assert c.primary_category == expected_primary
    assert 0.3 <= c.confidence <= 1.0

@pytest.mark.asyncio
async def test_semantic_search_summary_active():
    summary = await search_tool.get_document_summary()
    assert summary.get('database_status') == 'active'
    assert summary.get('total_documents', 0) >= 1

rag_queries = [
    "Punjab wheat irrigation schedule after rainfall",
    "Fertilizer recommendation for rice crop Tamil Nadu",
    "Pest control advice for cotton in Maharashtra",
]

@pytest.mark.asyncio
@pytest.mark.parametrize("q", rag_queries)
async def test_rag_orchestrator_end_to_end(q):
    res = await process_agricultural_query(q, {"state": "Punjab"})
    assert res['success'] is True
    assert 'response' in res and 'main_answer' in res['response']
    assert isinstance(res['tools_used'], list) and len(res['tools_used']) >= 1
    assert res.get('confidence_score') is not None
