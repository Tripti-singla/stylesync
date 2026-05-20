from services.supabase_service import seed_products

if __name__ == "__main__":
    result = seed_products()
    print(result)
