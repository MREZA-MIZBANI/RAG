from django.contrib import admin
from django.contrib import messages
from .models import Document, QAHistory
from rag_module.document_loader import process_docx_and_store, delete_doc_chunks_from_chroma

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_processed', 'uploaded_at')
    list_filter = ('is_processed', 'uploaded_at')
    search_fields = ('title', 'full_text')
    readonly_fields = ('full_text', 'is_processed', 'uploaded_at') 

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        if not obj.is_processed or (change and 'file' in form.changed_data):
            try:

                delete_doc_chunks_from_chroma(obj.pk)
                
                extracted_text = process_docx_and_store(obj.file.path, obj.pk)
                
                if extracted_text:
                    Document.objects.filter(pk=obj.pk).update(
                        full_text=extracted_text,
                        is_processed=True
                    )
                    self.message_user(
                        request, 
                        f"سند «{obj.title}» پردازش شد و چانک‌های آن در ChromaDB به‌روزرسانی شدند.", 
                        level=messages.SUCCESS
                    )
            except Exception as e:
                self.message_user(
                    request, 
                    f"خطا در پردازش و امبدینگ سند: {str(e)}", 
                    level=messages.ERROR
                )

    def delete_model(self, request, obj):
        delete_doc_chunks_from_chroma(obj.pk)
        title = obj.title
        super().delete_model(request, obj)
        self.message_user(
            request, 
            f"سند «{title}» و تمام چانک‌های مربوط به آن از سیستم پاک شدند.", 
            level=messages.SUCCESS
        )

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            delete_doc_chunks_from_chroma(obj.pk)
        super().delete_queryset(request, queryset)


@admin.register(QAHistory)
class QAHistoryAdmin(admin.ModelAdmin):
    list_display = ('question_preview', 'eval_score', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('question', 'answer')
    
    def get_readonly_fields(self, request, obj=None):
        if obj: 
            return ('question', 'answer', 'eval_score', 'created_at')
        return ('answer', 'eval_score', 'created_at')

    def save_model(self, request, obj, form, change):

        if not change:
            try:
                from rag_module.llm_chain import ask_question
                
                result = ask_question(obj.question, enable_eval=True)
                
                obj.answer = result.get('answer', 'پاسخی یافت نشد.')
                obj.eval_score = result.get('eval_score', None)
                
                self.message_user(
                    request, 
                    "پاسخ با موفقیت از مدل زبانی دریافت شد.", 
                    level=messages.SUCCESS
                )
            except Exception as e:
                obj.answer = f"خطا در تولید پاسخ: {str(e)}"
                self.message_user(
                    request, 
                    f"خطا در ارتباط با LLM: {str(e)}", 
                    level=messages.ERROR
                )
                

        super().save_model(request, obj, form, change)

    def question_preview(self, obj):
        return f"{obj.question[:60]}..." if obj.question else "-"
    question_preview.short_description = 'خلاصه پرسش'