# سامانه پرسش از اسناد (RAG) با Django و LangChain

این پروژه یک سامانه هوشمند برای مدیریت و پرسش از اسناد (فرمت docx) با استفاده از مدل‌های زبانی بزرگ است.

## پیش‌نیازها
- Docker و Docker Compose
- ثبت نام در سایت OpenRouter و دریافت API Key

## مراحل راه‌اندازی

۱. ابتدا ریپازیتوری را Clone کرده یا از حالت فشرده خارج کنید.
۲. یک فایل `.env` در مسیر اصلی پروژه (کنار manage.py) ایجاد کنید و متغیرهای زیر را در آن قرار دهید:
   OPENROUTER_API_KEY=your_api_key_here
   SECRET_KEY=your_django_secret_key

۳. دستور زیر را برای بیلد و اجرای کانتینرها وارد کنید:
   docker-compose up --build -d

۴. مایگریشن‌های دیتابیس را اعمال کنید:
   docker-compose exec web python manage.py migrate

۵. یک کاربر ارشد (Superuser) برای ورود به پنل ادمین بسازید:
   docker-compose exec web python manage.py createsuperuser

۶. پروژه در آدرس `http://localhost:8000/admin` در دسترس خواهد بود.