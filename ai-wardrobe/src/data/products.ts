export interface Review {
  id: string;
  userName: string;
  userAvatar?: string;
  rating: number;
  comment: string;
  date: string;
  verified: boolean;
  helpful: number;
}

export interface Product {
  id: string;
  name: string;
  brand: string;
  price: number;
  originalPrice?: number;
  image: string;
  description?: string;
  sizes?: string[];
  category: "men" | "women" | "kids";
  subcategory: string;
  colors: string[];
  rating: number;
  reviews: number;
  reviewsData?: Review[];
  badge?: "NEW" | "SALE" | "TRENDING";
}

export const products: Product[] = [
  // Men's Collection
  { id: "1", name: "Classic Slim Fit Shirt", brand: "StyleCraft", price: 1299, originalPrice: 1999, image: "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=400&h=500&fit=crop&auto=format&q=80", category: "men", subcategory: "shirts", colors: ["#1a365d", "#f7fafc", "#c53030"], rating: 4.3, reviews: 1240, badge: "SALE",
    reviewsData: [
      { id: "r1", userName: "Rahul Sharma", rating: 5, comment: "Perfect fit and great quality! The fabric is comfortable and looks exactly like the picture.", date: "2026-03-15", verified: true, helpful: 12 },
      { id: "r2", userName: "Amit Patel", rating: 4, comment: "Good shirt but runs a bit small. Would recommend going one size up.", date: "2026-03-10", verified: true, helpful: 8 },
      { id: "r3", userName: "Priya Singh", rating: 5, comment: "Love the color and fit. Great for both office and casual wear.", date: "2026-03-08", verified: false, helpful: 15 }
    ]
  },
  { id: "2", name: "Oxford White Formal Shirt", brand: "Arrow", price: 1899, image: "https://images.unsplash.com/photo-1591047990635-8ddd4971f7da?w=400&h=500&fit=crop&auto=format&q=80", category: "men", subcategory: "shirts", colors: ["#f7fafc", "#1a202c"], rating: 4.4, reviews: 856, badge: "NEW" },
  { id: "3", name: "Casual Checkered Shirt", brand: "Roadster", price: 999, image: "https://images.unsplash.com/photo-1596521881695-b6252a3e0cd1?w=400&h=500&fit=crop&auto=format&q=80", category: "men", subcategory: "shirts", colors: ["#c53030", "#1a365d", "#744210"], rating: 4.2, reviews: 645, badge: "TRENDING" },
  { id: "4", name: "Casual Denim Jacket", brand: "Roadster", price: 2499, originalPrice: 3499, image: "https://images.unsplash.com/photo-1576995853950-3135dd27f172?w=400&h=500&fit=crop&auto=format&q=80", category: "men", subcategory: "jackets", colors: ["#2d3748", "#4a5568"], rating: 4.6, reviews: 2100, badge: "TRENDING",
    reviewsData: [
      { id: "r4", userName: "Vikram Singh", rating: 5, comment: "Amazing jacket! Perfect for layering and looks great with jeans. The denim quality is excellent.", date: "2026-03-12", verified: true, helpful: 23 },
      { id: "r5", userName: "Sneha Gupta", rating: 4, comment: "Love the fit and style. A bit pricey but worth it for the quality. Runs true to size.", date: "2026-03-08", verified: true, helpful: 18 },
      { id: "r6", userName: "Arjun Kumar", rating: 5, comment: "This jacket has become my go-to piece. Comfortable, stylish, and versatile. Highly recommend!", date: "2026-03-05", verified: false, helpful: 31 }
    ]
  },
  { id: "5", name: "Wool Blazer", brand: "Peter England", price: 3999, image: "https://images.unsplash.com/photo-1552062407-c0a02039baf1?w=400&h=500&fit=crop&auto=format&q=80", category: "men", subcategory: "jackets", colors: ["#1a202c", "#744210"], rating: 4.7, reviews: 1200 },
  { id: "6", name: "Leather Bomber Jacket", brand: "Hidesign", price: 5499, originalPrice: 7499, image: "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&h=500&fit=crop&auto=format&q=80", category: "men", subcategory: "jackets", colors: ["#744210", "#1a202c"], rating: 4.5, reviews: 890, badge: "SALE" },
  { id: "7", name: "Tailored Chinos", brand: "Allen Solly", price: 1799, image: "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=400&h=500&fit=crop&auto=format&q=80", category: "men", subcategory: "trousers", colors: ["#744210", "#2d3748", "#1a365d"], rating: 4.4, reviews: 780 },
  { id: "8", name: "Black Formal Trousers", brand: "Van Heusen", price: 1599, image: "https://images.unsplash.com/photo-1542272604-787c62d465d1?w=400&h=500&fit=crop&auto=format&q=80", category: "men", subcategory: "trousers", colors: ["#1a202c"], rating: 4.6, reviews: 1100 },
  { id: "9", name: "Casual Blue Jeans", brand: "Levi's", price: 2299, image: "https://images.unsplash.com/photo-1542272604-787c62d465d1?w=400&h=500&fit=crop&auto=format&q=80", category: "men", subcategory: "trousers", colors: ["#1a365d", "#2d3748"], rating: 4.5, reviews: 2300, badge: "TRENDING" },
  { id: "10", name: "Running Sneakers", brand: "Nike", price: 5999, image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=500&fit=crop&auto=format&q=80", category: "men", subcategory: "shoes", colors: ["#e53e3e", "#1a202c"], rating: 4.6, reviews: 3200, badge: "TRENDING" },
  { id: "11", name: "Casual Loafers", brand: "Allen Edmonds", price: 3499, image: "https://images.unsplash.com/photo-1543291026-56ceb5ee6887?w=400&h=500&fit=crop&auto=format&q=80", category: "men", subcategory: "shoes", colors: ["#744210", "#1a202c"], rating: 4.4, reviews: 670 },
  { id: "12", name: "Formal Oxford Shoes", brand: "Bata", price: 2199, image: "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400&h=500&fit=crop&auto=format&q=80", category: "men", subcategory: "shoes", colors: ["#1a202c", "#744210"], rating: 4.5, reviews: 850 },
  { id: "13", name: "Leather Belt", brand: "Hidesign", price: 1499, image: "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=500&fit=crop&auto=format&q=80", category: "men", subcategory: "accessories", colors: ["#1a202c", "#744210"], rating: 4.5, reviews: 670 },
  { id: "14", name: "Classic Watch", brand: "Titan", price: 4999, image: "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=400&h=500&fit=crop&auto=format&q=80", category: "men", subcategory: "accessories", colors: ["#744210", "#1a202c"], rating: 4.7, reviews: 1200 },
  { id: "15", name: "Sunglasses UV Protected", brand: "Ray-Ban", price: 3499, image: "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400&h=500&fit=crop&auto=format&q=80", category: "men", subcategory: "accessories", colors: ["#1a202c", "#8b5a3c"], rating: 4.6, reviews: 950, badge: "SALE" },
  
  // Women's Collection
  { id: "16", name: "Floral Summer Dress", brand: "Aurelia", price: 1899, image: "https://images.unsplash.com/photo-1595777707802-e176fc7f42b9?w=400&h=500&fit=crop&auto=format&q=80", category: "women", subcategory: "dresses", colors: ["#fbb6ce", "#f7fafc"], rating: 4.5, reviews: 890, badge: "NEW",
    reviewsData: [
      { id: "r7", userName: "Priya Sharma", rating: 5, comment: "Absolutely gorgeous dress! The floral print is beautiful and the fit is perfect. Got so many compliments!", date: "2026-03-14", verified: true, helpful: 15 },
      { id: "r8", userName: "Anjali Mehta", rating: 4, comment: "Love the design and fabric. Perfect for summer outings. The length is just right.", date: "2026-03-11", verified: true, helpful: 12 },
      { id: "r9", userName: "Kavita Rao", rating: 5, comment: "This dress exceeded my expectations. Great quality and the colors are vibrant. Will definitely buy again!", date: "2026-03-09", verified: false, helpful: 20 }
    ]
  },
  { id: "17", name: "Maxi Evening Gown", brand: "Sabyasachi", price: 6499, image: "https://images.unsplash.com/photo-1612336307429-8a88e8d08dbb?w=400&h=500&fit=crop&auto=format&q=80", category: "women", subcategory: "dresses", colors: ["#9b2c2c", "#f7fafc"], rating: 4.8, reviews: 450 },
  { id: "18", name: "Casual Midi Dress", brand: "FOREVER 21", price: 1299, originalPrice: 1899, image: "https://images.unsplash.com/photo-1589223707857-401a253ee828?w=400&h=500&fit=crop&auto=format&q=80", category: "women", subcategory: "dresses", colors: ["#1a365d", "#fbb6ce"], rating: 4.3, reviews: 650, badge: "SALE" },
  { id: "19", name: "Elegant Silk Saree", brand: "FabIndia", price: 4599, image: "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=400&h=500&fit=crop&auto=format&q=80", category: "women", subcategory: "sarees", colors: ["#9b2c2c", "#d69e2e"], rating: 4.8, reviews: 560 },
  { id: "20", name: "Cotton Casual Saree", brand: "Suta", price: 2499, image: "https://images.unsplash.com/photo-1609007755793-8015a029abb4?w=400&h=500&fit=crop&auto=format&q=80", category: "women", subcategory: "sarees", colors: ["#38a169", "#f7fafc"], rating: 4.4, reviews: 420, badge: "NEW" },
  { id: "21", name: "Embroidered Kurta Set", brand: "BIBA", price: 2199, originalPrice: 2999, image: "https://images.unsplash.com/photo-1605777712763-2e8e4df3ebb8?w=400&h=500&fit=crop&auto=format&q=80", category: "women", subcategory: "kurtas", colors: ["#553c9a", "#d69e2e"], rating: 4.7, reviews: 1560, badge: "SALE" },
  { id: "22", name: "Casual Cotton Kurta", brand: "Biba", price: 1499, image: "https://images.unsplash.com/photo-1611040626919-491cf4bbd1d3?w=400&h=500&fit=crop&auto=format&q=80", category: "women", subcategory: "kurtas", colors: ["#fbb6ce", "#38a169"], rating: 4.3, reviews: 780 },
  { id: "23", name: "Crop Top", brand: "H&M", price: 799, originalPrice: 1299, image: "https://images.unsplash.com/photo-1506629082632-41ad64bd3d66?w=400&h=500&fit=crop&auto=format&q=80", category: "women", subcategory: "tops", colors: ["#f7fafc", "#1a202c"], rating: 4.1, reviews: 430, badge: "SALE" },
  { id: "24", name: "Off-Shoulder Top", brand: "Zara", price: 1599, image: "https://images.unsplash.com/photo-1485872299829-c673f5194813?w=400&h=500&fit=crop&auto=format&q=80", category: "women", subcategory: "tops", colors: ["#c53030", "#f7fafc"], rating: 4.4, reviews: 650, badge: "TRENDING" },
  { id: "25", name: "High Waisted Jeans", brand: "Levi's", price: 2499, image: "https://images.unsplash.com/photo-1505034723556-1a580d36c56a?w=400&h=500&fit=crop&auto=format&q=80", category: "women", subcategory: "bottoms", colors: ["#1a365d", "#2d3748"], rating: 4.6, reviews: 1850 },
  { id: "26", name: "Casual Flowy Pants", brand: "Forever 21", price: 1199, image: "https://images.unsplash.com/photo-1506629082632-41ad64bd3d66?w=400&h=500&fit=crop&auto=format&q=80", category: "women", subcategory: "bottoms", colors: ["#f7fafc", "#1a202c"], rating: 4.2, reviews: 520 },
  { id: "27", name: "Heeled Sandals", brand: "Steve Madden", price: 2999, image: "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400&h=500&fit=crop&auto=format&q=80", category: "women", subcategory: "shoes", colors: ["#d69e2e", "#1a202c"], rating: 4.5, reviews: 780, badge: "NEW" },
  { id: "28", name: "Casual Sneakers", brand: "Skechers", price: 1999, image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=500&fit=crop&auto=format&q=80", category: "women", subcategory: "shoes", colors: ["#f7fafc", "#1a365d"], rating: 4.3, reviews: 1100 },
  { id: "29", name: "Embroidered Handbag", brand: "Baggit", price: 2199, image: "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400&h=500&fit=crop&auto=format&q=80", category: "women", subcategory: "accessories", colors: ["#9b2c2c", "#744210"], rating: 4.6, reviews: 650 },
  { id: "30", name: "Fashion Sunglasses", brand: "Prada", price: 3999, image: "https://images.unsplash.com/photo-1556821552-a28e0152e735?w=400&h=500&fit=crop&auto=format&q=80", category: "women", subcategory: "accessories", colors: ["#1a202c", "#d69e2e"], rating: 4.7, reviews: 890, badge: "TRENDING" },
  
  // Kids Collection
  { id: "31", name: "Kids Cartoon T-Shirt", brand: "Max Kids", price: 499, originalPrice: 799, image: "https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?w=400&h=500&fit=crop&auto=format&q=80", category: "kids", subcategory: "tshirts", colors: ["#3182ce", "#e53e3e", "#38a169"], rating: 4.2, reviews: 340, badge: "SALE" },
  { id: "32", name: "Striped T-Shirt", brand: "Mothercare", price: 599, image: "https://images.unsplash.com/photo-1503944583220-79d8926ad5e2?w=400&h=500&fit=crop&auto=format&q=80", category: "kids", subcategory: "tshirts", colors: ["#1a202c", "#f7fafc"], rating: 4.0, reviews: 280 },
  { id: "33", name: "Graphic Print Tee", brand: "H&M Kids", price: 699, image: "https://images.unsplash.com/photo-1513621776144-e92529857d43?w=400&h=500&fit=crop&auto=format&q=80", category: "kids", subcategory: "tshirts", colors: ["#c53030", "#3182ce"], rating: 4.3, reviews: 420, badge: "NEW" },
  { id: "34", name: "Kids Party Frock", brand: "FirstCry", price: 1099, image: "https://images.unsplash.com/photo-1518831959646-742c3a14ebf7?w=400&h=500&fit=crop&auto=format&q=80", category: "kids", subcategory: "dresses", colors: ["#fbb6ce", "#f6e05e"], rating: 4.3, reviews: 220, badge: "NEW" },
  { id: "35", name: "Casual Summer Dress", brand: "Gini & Jony", price: 799, image: "https://images.unsplash.com/photo-1516192318233-f5b1c11cfe8d?w=400&h=500&fit=crop&auto=format&q=80", category: "kids", subcategory: "dresses", colors: ["#38a169", "#f7fafc"], rating: 4.1, reviews: 180 },
  { id: "36", name: "Boys Denim Shorts", brand: "Gini & Jony", price: 699, image: "https://images.unsplash.com/photo-1503944583220-79d8926ad5e2?w=400&h=500&fit=crop&auto=format&q=80", category: "kids", subcategory: "shorts", colors: ["#2d3748", "#4a5568"], rating: 4.0, reviews: 190 },
  { id: "37", name: "Khaki Cargo Shorts", brand: "Tommy Hilfiger", price: 899, image: "https://images.unsplash.com/photo-1542272604-787c62d465d1?w=400&h=500&fit=crop&auto=format&q=80", category: "kids", subcategory: "shorts", colors: ["#744210", "#38a169"], rating: 4.2, reviews: 310, badge: "TRENDING" },
  { id: "38", name: "Kids Sneakers", brand: "Skechers", price: 1299, image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=500&fit=crop&auto=format&q=80", category: "kids", subcategory: "shoes", colors: ["#3182ce", "#e53e3e"], rating: 4.4, reviews: 560 },
  { id: "39", name: "School Canvas Shoes", brand: "Bata", price: 799, image: "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400&h=500&fit=crop&auto=format&q=80", category: "kids", subcategory: "shoes", colors: ["#1a202c", "#f7fafc"], rating: 4.0, reviews: 420 },
  { id: "40", name: "Kids Backpack", brand: "Skybags", price: 1599, image: "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=500&fit=crop&auto=format&q=80", category: "kids", subcategory: "accessories", colors: ["#3182ce", "#f7fafc"], rating: 4.5, reviews: 680, badge: "SALE" },
];

export const categories = [
  { name: "Men", path: "/men", image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop" },
  { name: "Women", path: "/women", image: "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=300&h=400&fit=crop" },
  { name: "Wardrobe", path: "/wardrobe", image: "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=300&h=400&fit=crop" },
];

// Shuffle utility to randomize products on page reload
export function shuffleArray<T>(array: T[]): T[] {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

export interface WardrobeItem {
  id: string;
  image: string;
  name: string;
  category: "topwear" | "bottomwear" | "footwear" | "accessories" | "ethnic";
  color: string;
  pattern?: string;
  dateAdded: string;
}
