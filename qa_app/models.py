import os
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

class Document(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان سند")
    file = models.FileField(upload_to='documents/', verbose_name="فایل سند (docx)")
    full_text = models.TextField(blank=True, null=True, verbose_name="متن کامل استخراج شده")
    is_processed = models.BooleanField(default=False, verbose_name="پردازش و امبد شده در ChromaDB")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ بارگذاری")

    class Meta:
        verbose_name = "سند"
        verbose_name_plural = "اسناد"
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title


class QAHistory(models.Model):
    question = models.TextField(verbose_name="پرسش")
    answer = models.TextField(verbose_name="پاسخ مدل زبانی")
    eval_score = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="نمره ارزیابی Ragas (Faithfulness)"
    )
    is_verified = models.BooleanField(
        default=True, 
        verbose_name="تایید شده توسط حد آستانه"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ پرسش")

    class Meta:
        verbose_name = "تاریخچه پرسش"
        verbose_name_plural = "تاریخچه پرسش‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return f"پرسش: {self.question[:50]}..."




@receiver(post_delete, sender=Document)
def auto_delete_file_on_delete(sender, instance, **kwargs):

    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

@receiver(pre_save, sender=Document)
def auto_delete_file_on_change(sender, instance, **kwargs):

    if not instance.pk:
        return False

    try:
        old_file = Document.objects.get(pk=instance.pk).file
    except Document.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if old_file and os.path.isfile(old_file.path):
            os.remove(old_file.path)