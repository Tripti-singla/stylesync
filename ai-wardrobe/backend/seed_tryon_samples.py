from services.supabase_service import seed_tryon_samples

SEED_SAMPLES = [
    {
        "sample_id": "seed-1",
        "user_id": "seed",
        "category": "tops",
        "occasion": "casual",
        "source": "seed",
        "body_image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=1024",
        "clothing_image_url": "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=1024",
    },
    {
        "sample_id": "seed-2",
        "user_id": "seed",
        "category": "shirts",
        "occasion": "business",
        "source": "seed",
        "body_image_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=1024",
        "clothing_image_url": "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=1024",
    },
    {
        "sample_id": "seed-3",
        "user_id": "seed",
        "category": "dresses",
        "occasion": "party",
        "source": "seed",
        "body_image_url": "https://images.unsplash.com/photo-1521119989659-a83eee488004?w=1024",
        "clothing_image_url": "https://images.unsplash.com/photo-1539533018447-63fcce2678e4?w=1024",
    },
    {
        "sample_id": "seed-4",
        "user_id": "seed",
        "category": "jackets",
        "occasion": "evening",
        "source": "seed",
        "body_image_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=1024",
        "clothing_image_url": "https://images.unsplash.com/photo-1445205170230-053b83016050?w=1024",
    },
    {
        "sample_id": "seed-5",
        "user_id": "seed",
        "category": "sports",
        "occasion": "sports",
        "source": "seed",
        "body_image_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=1024",
        "clothing_image_url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=1024",
    },
]


if __name__ == "__main__":
    result = seed_tryon_samples(SEED_SAMPLES)
    print(result)
