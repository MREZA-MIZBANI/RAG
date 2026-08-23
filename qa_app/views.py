from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import QAHistory, Document

@csrf_exempt
def query_document_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'فقط متد POST برای این API مجاز است.'}, status=405)

    try:
        if not request.body:
            return JsonResponse({'error': 'بدنه درخواست (Body) خالی است.'}, status=400)

        data = json.loads(request.body)
        question = data.get('question', '').strip()
        enable_eval = data.get('enable_eval', False)

        if not question:
            return JsonResponse({'error': 'پرسش ارسال نشده است.'}, status=400)

        from rag_module.llm_chain import ask_question

        result = ask_question(question, enable_eval=enable_eval)

        if isinstance(result, dict):
            final_answer = result.get('answer', 'پاسخی یافت نشد.')
            eval_dict = result.get('evaluation', {})
            eval_score = eval_dict.get('faithfulness') if isinstance(eval_dict, dict) else None
        else:
            final_answer = str(result)
            eval_score = None

        qa_record = QAHistory.objects.create(
            question=question,
            answer=final_answer,
            eval_score=eval_score
        )

        return JsonResponse({
            'id': qa_record.id,
            'question': question,
            'answer': final_answer,
            'eval_score': eval_score
        }, status=200, json_dumps_params={'ensure_ascii': False})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'فرمت JSON ارسالی معتبر نیست.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'خطای سرور: {str(e)}'}, status=500)


@csrf_exempt
def upload_document_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'فقط متد POST مجاز است.'}, status=405)

    if 'file' not in request.FILES:
        return JsonResponse({'error': 'فایلی ارسال نشده است.'}, status=400)

    file_obj = request.FILES['file']

    if not file_obj.name.endswith('.docx'):
        return JsonResponse({'error': 'فقط فایل‌های با پسوند docx. پشتیبانی می‌شوند.'}, status=400)

    try:
        doc = Document.objects.create(
            title=file_obj.name,
            file=file_obj
        )

        from rag_module.document_loader import process_docx_and_store

        full_text = process_docx_and_store(doc.file.path, doc.id)

        doc.full_text = full_text
        doc.is_processed = True
        doc.save()

        return JsonResponse({
            'message': 'سند با موفقیت بارگذاری و امبد شد.',
            'document_id': doc.id,
            'title': doc.title
        }, status=201, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        return JsonResponse({'error': f'خطا در پردازش سند: {str(e)}'}, status=500)
    
    
def get_qa_history_api(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'فقط متد GET مجاز است.'}, status=405)
        
    try:
        history = QAHistory.objects.all().order_by('-created_at')[:10]
        data = [
            {
                'id': item.id,
                'question': item.question,
                'answer': item.answer,
                'eval_score': item.eval_score,
                'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for item in history
        ]
        return JsonResponse({'history': data}, status=200, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({'error': f'خطا در دریافت تاریخچه: {str(e)}'}, status=500)