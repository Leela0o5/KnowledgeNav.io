import uuid
from pathlib import Path

from src.config import settings
from evaluation.dataset import QAPair
from evaluation.metrics import MetricScore
from evaluation.report import EvalReport


async def run_ragas_evaluation(dataset: list[QAPair], corpus_id: str) -> EvalReport:
    from datasets import Dataset  # type: ignore[import-untyped]
    from ragas import evaluate  # type: ignore[import-untyped]
    from ragas.metrics import (  # type: ignore[import-untyped]
        answer_relevancy,
        context_precision,
        context_recall,
        faithfulness,
    )
    from agent.graph import build_rag_graph
    from sessions.context import build_conversation_context

    graph = build_rag_graph()
    thresholds = settings.ragas_thresholds()

    questions: list[str] = []
    answers: list[str] = []
    contexts: list[list[str]] = []
    ground_truths: list[str] = []

    for pair in dataset:
        initial_state = {
            "question": pair.question,
            "corpus_id": corpus_id,
            "session_id": str(uuid.uuid4()),
            "user_id": "eval",
            "conversation_context": "",
            "bm25_results": [],
            "vector_results": [],
            "fused_results": [],
            "reranked_chunks": [],
            "raw_answer": "",
            "validated_answer": None,
            "citation_attempts": 0,
            "trace_id": str(uuid.uuid4()),
            "error": None,
        }
        final_state = await graph.ainvoke(initial_state)
        validated = final_state.get("validated_answer")
        answer = validated.content if validated else ""
        chunk_texts = [c.chunk.text for c in final_state.get("reranked_chunks", [])]

        questions.append(pair.question)
        answers.append(answer)
        contexts.append(chunk_texts)
        ground_truths.append(pair.ground_truth)

    ragas_dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    })

    result = evaluate(
        dataset=ragas_dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    )

    scores = [
        MetricScore(name="faithfulness", score=float(result["faithfulness"]), threshold=thresholds["faithfulness"]),
        MetricScore(name="answer_relevancy", score=float(result["answer_relevancy"]), threshold=thresholds["answer_relevancy"]),
        MetricScore(name="context_precision", score=float(result["context_precision"]), threshold=thresholds["context_precision"]),
        MetricScore(name="context_recall", score=float(result["context_recall"]), threshold=thresholds["context_recall"]),
    ]

    return EvalReport(scores=scores, thresholds=thresholds)
