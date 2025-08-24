#!/usr/bin/env python3

from app.features.interviews.services.categories_service import CategoriesService
from app.shared.database import get_session


def test_companies():
    session_gen = get_session()
    session = next(session_gen)
    try:
        service = CategoriesService(session)
        companies = service.get_top_companies(limit=5)
        print(f"Found {len(companies)} companies:")
        for company in companies:
            print(f"  {company.name}: {company.count}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        try:
            next(session_gen)  # Close session
        except StopIteration:
            pass


if __name__ == "__main__":
    test_companies()
