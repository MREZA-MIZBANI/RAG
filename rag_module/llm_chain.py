import os
import sys
from unittest.mock import MagicMock
sys.modules['langchain_community.chat_models.vertexai'] = MagicMock()
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from .vector_store import get_retriever

from dotenv import load_dotenv

load_dotenv()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def ask_question(question: str, enable_eval: bool = False):
    api_key = "sk-or-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set in the environment variables.")

    generator_llm = ChatOpenAI(
        model="poolside/laguna-s-2.1:free",
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.2
    )
    
    prompt = ChatPromptTemplate.from_template("""
    پاسخ را دقیقاً بر اساس مستندات زیر ارائه بده. اگر پاسخ در متن نیست، صریحاً بگو در اسناد یافت نشد.

    مستندات:
    {context}

    سوال:
    {question}
    """)

    retriever = get_retriever()
    retrieved_docs = retriever.invoke(question)
    contexts = [doc.page_content for doc in retrieved_docs]

    chain = prompt | generator_llm | StrOutputParser()
    answer = chain.invoke({
        "context": format_docs(retrieved_docs),
        "question": question
    })

    evaluation_metrics = {}
    
    if enable_eval:
        try:
            evaluator_llm = ChatOpenAI(
                model="poolside/laguna-s-2.1:free",
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                temperature=0.0 
            )

            data = {
                "question": [question],
                "answer": [answer],
                "contexts": [contexts] 
            }
            dataset = Dataset.from_dict(data)

            result = evaluate(
                dataset=dataset,
                metrics=[faithfulness, answer_relevancy],
                llm=evaluator_llm,
                raise_exceptions=False
            )
            
            evaluation_metrics = {
                "faithfulness": result.get("faithfulness"),
                "answer_relevancy": result.get("answer_relevancy")
            }
            
        except Exception as e:
            print(f"[Warning] Ragas Evaluation failed: {e}")
            evaluation_metrics = {"error": str(e)}

    return {
        "answer": answer,
        "source_documents": contexts,
        "evaluation": evaluation_metrics
    }