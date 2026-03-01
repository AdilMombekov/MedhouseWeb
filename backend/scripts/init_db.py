"""
Создание БД, компаний и первого администратора.
Запуск: из папки backend: python -m scripts.init_db
"""
import sys
from pathlib import Path

backend = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend))

from app.database import SessionLocal, engine
from app.models import Base, User, Company, ReportTemplate
from app.auth import get_password_hash

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Company).first():
            print("Компании уже созданы.")
        else:
            db.add(Company(code="medhouse", name="Медхаус", description="Дистрибьютор парафармации, 15 городов и регионов"))
            db.add(Company(code="swiss_energy", name="Свисс Энерджи", description="Контролирующая компания Swiss Group (Швейцария), производство UA/BG/CN, поставки в филиалы"))
            db.commit()
            print("Созданы компании: Медхаус, Свисс Энерджи.")

        if db.query(User).filter(User.email == "admin@medhouse.kz").first():
            print("Админ уже существует.")
        else:
            admin = User(
                email="admin@medhouse.kz",
                hashed_password=get_password_hash("admin123"),
                full_name="Администратор",
                role="admin",
            )
            db.add(admin)
            db.commit()
            print("Создан админ: admin@medhouse.kz / admin123")

        if db.query(ReportTemplate).first():
            print("Шаблоны уже есть.")
        else:
            templates_dir = backend / "templates"
            templates_dir.mkdir(exist_ok=True)
            template_path = templates_dir / "shablon_otcheta_medhouse.xlsx"
            if not template_path.exists():
                try:
                    from openpyxl import Workbook
                    from openpyxl.styles import Font, Alignment
                    wb = Workbook()
                    ws = wb.active
                    ws.title = "Отчёт"
                    ws.append(["Период", "Город/Филиал", "Товар", "Кол-во", "Сумма", "Примечание"])
                    for c in range(1, 7):
                        ws.cell(1, c).font = Font(bold=True)
                    ws.column_dimensions["A"].width = 12
                    ws.column_dimensions["B"].width = 20
                    ws.column_dimensions["C"].width = 40
                    wb.save(template_path)
                    print("Создан файл шаблона:", template_path)
                except Exception as e:
                    print("Не удалось создать xlsx:", e)
            t = ReportTemplate(
                name="Шаблон отчётности 1С (Медхаус)",
                description="Заполните по инструкции в 1С и загрузите отчёт на сайт.",
                file_name="shablon_otcheta_medhouse.xlsx",
                report_type="sales_monthly",
                company_id=1,
            )
            db.add(t)
            db.commit()
            print("Добавлен шаблон отчётности.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
