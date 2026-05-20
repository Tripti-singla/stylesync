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
  {
    id: "1",
    name: "Men Solid Polo Neck Pure Cotton White T-Shirt",
    brand: "Flipkart",
    price: 809,
    originalPrice: 1799,
    image: "https://rukminim2.flixcart.com/image/832/832/xif0q/t-shirt/b/s/p/-original-imagzwrsmryt7kzt.jpeg?q=70",
    description: "Premium solid white polo neck t-shirt in pure cotton fabric.",
    category: "men",
    subcategory: "tshirts",
    colors: ["#ffffff", "#cbd5e1"],
    rating: 4.3,
    reviews: 1240,
    badge: "SALE",
    sizes: ["S", "M", "L"]
  },
  {
    id: "2",
    name: "Men Henley Neck Black T-Shirt",
    brand: "Flipkart",
    price: 599,
    originalPrice: 1299,
    image: "https://rukminim2.flixcart.com/image/832/832/xif0q/t-shirt/z/1/b/m-askporob73523-ausk-original-imagq22gygupmzz2.jpeg?q=70",
    description: "Stylish black Henley neck t-shirt, perfect for casual outings.",
    category: "men",
    subcategory: "tshirts",
    colors: ["#1a202c", "#4a5568"],
    rating: 4.2,
    reviews: 645,
    sizes: ["S", "M", "L", "XL"]
  },
  {
    id: "3",
    name: "Men Classic Denim Shirt",
    brand: "Flipkart",
    price: 1199,
    originalPrice: 2499,
    image: "https://rukminim2.flixcart.com/image/832/832/xif0q/shirt/i/v/t/m-ud-denim-01-uc-box-original-imaghyfhkzex2ezy.jpeg?q=70",
    description: "Classic blue denim shirt with dual chest pockets and durable fabric.",
    category: "men",
    subcategory: "shirts",
    colors: ["#1a365d", "#2b6cb0"],
    rating: 4.4,
    reviews: 856,
    badge: "TRENDING",
    sizes: ["M", "L", "XL"]
  },
  {
    id: "4",
    name: "Men Checked Casual Shirt",
    brand: "Flipkart",
    price: 999,
    originalPrice: 1999,
    image: "https://rukminim2.flixcart.com/image/832/832/xif0q/shirt/g/d/y/m-db-1024-14-combraid-original-imagm9gzmhhwyuzn.jpeg?q=70",
    description: "Trendy checked casual shirt for a smart-casual look.",
    category: "men",
    subcategory: "shirts",
    colors: ["#c53030", "#2d3748"],
    rating: 4.1,
    reviews: 430,
    sizes: ["S", "M", "L"]
  },
  {
    id: "5",
    name: "Men Slim Fit Cotton Shirt",
    brand: "Flipkart",
    price: 899,
    originalPrice: 1899,
    image: "https://rukminim2.flixcart.com/image/832/832/xif0q/shirt/h/g/i/xxl-kcse-s-15-den-wht-killer-original-imagzhg9yphdwhgu.jpeg?q=70",
    description: "Stylish slim-fit cotton shirt in plain white, perfect for multi-layering.",
    category: "men",
    subcategory: "shirts",
    colors: ["#ffffff"],
    rating: 4.5,
    reviews: 780,
    sizes: ["S", "M", "L", "XL"]
  },
  {
    id: "6",
    name: "Men Arrow Formal Cotton Shirt",
    brand: "Arrow",
    price: 1899,
    originalPrice: 2999,
    image: "https://rukminim2.flixcart.com/image/832/832/xif0q/shirt/r/t/7/38-9006612-arrow-original-imaggf2hhqgyh84j.jpeg?q=70",
    description: "Premium formal cotton shirt by Arrow, tailored for professional business wear.",
    category: "men",
    subcategory: "shirts",
    colors: ["#ffffff", "#e2e8f0"],
    rating: 4.6,
    reviews: 1100,
    badge: "NEW",
    sizes: ["S", "M", "L", "XL"]
  },
  {
    id: "7",
    name: "Women Yellow Floral Summer Maxi Dress",
    brand: "Flipkart",
    price: 899,
    originalPrice: 1999,
    image: "https://rukminim2.flixcart.com/image/832/832/xif0q/dress/z/d/3/m-3037-yell-siril-original-imaghfnydphggygz.jpeg?q=70",
    description: "Flowing yellow maxi dress with beautiful floral print, perfect for summer outings.",
    category: "women",
    subcategory: "dresses",
    colors: ["#ecc94b", "#ffffff"],
    rating: 4.5,
    reviews: 890,
    badge: "NEW",
    sizes: ["S", "M", "L"]
  },
  {
    id: "8",
    name: "Women Georgette A-line Dress",
    brand: "Flipkart",
    price: 1299,
    originalPrice: 2499,
    image: "https://rukminim2.flixcart.com/image/832/832/xif0q/dress/t/h/g/m-aa-0120-d-dress-ananya-creation-original-imagznzzkuf4y7hu.jpeg?q=70",
    description: "Elegant georgette A-line dress in maroon, suitable for evening gatherings.",
    category: "women",
    subcategory: "dresses",
    colors: ["#742a2a", "#1a202c"],
    rating: 4.3,
    reviews: 520,
    sizes: ["S", "M", "L", "XL"]
  },
  {
    id: "9",
    name: "Women Embroidered Anarkali Kurta Set",
    brand: "Anubhutee",
    price: 1899,
    originalPrice: 3999,
    image: "https://rukminim2.flixcart.com/image/832/832/xif0q/ethnic-set/v/s/4/m-22fe07-anubhutee-original-imaghg7szjqyhsgk.jpeg?q=70",
    description: "Traditional cotton Anarkali kurta set with exquisite embroidery details.",
    category: "women",
    subcategory: "kurtas",
    colors: ["#44337a", "#ecc94b"],
    rating: 4.7,
    reviews: 1560,
    badge: "SALE",
    sizes: ["S", "M", "L"]
  },
  {
    id: "10",
    name: "Women Vasundhara Silk Blend Saree",
    brand: "Flipkart",
    price: 2499,
    originalPrice: 5999,
    image: "https://rukminim2.flixcart.com/image/832/832/xif0q/sari/v/e/q/free-vasundhara-dharini-original-imagg9zvyhzncgy8.jpeg?q=70",
    description: "Rich traditional silk blend saree with designer borders and zari work.",
    category: "women",
    subcategory: "sarees",
    colors: ["#c53030", "#ecc94b"],
    rating: 4.8,
    reviews: 560,
    badge: "TRENDING",
    sizes: ["Free Size"]
  },
  {
    id: "11",
    name: "Women Casual Denim Jacket",
    brand: "Flipkart",
    price: 1399,
    originalPrice: 2499,
    image: "https://rukminim2.flixcart.com/image/832/832/xif0q/jacket/i/y/l/xl-no-5463-jeans-jacket-shree-sharnam-creation-original-imaghs4w4jthq9yy.jpeg?q=70",
    description: "Rugged and fashionable women's blue denim jacket with front pockets.",
    category: "women",
    subcategory: "jackets",
    colors: ["#2b6cb0", "#1a365d"],
    rating: 4.4,
    reviews: 650,
    sizes: ["S", "M", "L"]
  },
  {
    id: "12",
    name: "Women Off-Shoulder Crop Top",
    brand: "Juneberry",
    price: 549,
    originalPrice: 1199,
    image: "https://rukminim2.flixcart.com/image/832/832/xif0q/top/h/r/e/m-top-347-yellow-juneberry-original-imagkhecmyczz3eh.jpeg?q=70",
    description: "Trendy yellow off-shoulder crop top for casual summer styling.",
    category: "women",
    subcategory: "tops",
    colors: ["#ecc94b", "#ffffff"],
    rating: 4.2,
    reviews: 310,
    sizes: ["S", "M", "L"]
  },
  {
    id: "13",
    name: "Women Levi's High Rise Jeans",
    brand: "Levi's",
    price: 1999,
    originalPrice: 2999,
    image: "https://rukminim2.flixcart.com/image/832/832/xif0q/jean/r/o/p/30-18298-0955-levi-s-original-imagg2pbfg7b5gzb.jpeg?q=70",
    description: "Authentic Levi's high-rise skinny jeans in classic dark blue denim.",
    category: "women",
    subcategory: "jeans",
    colors: ["#1a365d", "#2d3748"],
    rating: 4.6,
    reviews: 1850,
    sizes: ["28", "30", "32"]
  },
  {
    id: "14",
    name: "Men Pantaloons Chino Shorts",
    brand: "Pantaloons",
    price: 799,
    originalPrice: 1499,
    image: "https://rukminim2.flixcart.com/image/832/832/xif0q/short/w/s/4/32-205128001-pantaloons-original-imaghs4gzsnhkkyy.jpeg?q=70",
    description: "Comfortable cotton chino shorts by Pantaloons, ideal for warm weather.",
    category: "men",
    subcategory: "shorts",
    colors: ["#dd6b20", "#ecc94b"],
    rating: 4.0,
    reviews: 190,
    sizes: ["30", "32", "34"]
  },
  {
    id: "15",
    name: "Men Nike Revolution Running Shoes",
    brand: "Nike",
    price: 2499,
    originalPrice: 3999,
    image: "https://rukminim2.flixcart.com/image/832/832/xif0q/shoe/c/w/o/6-da8535-001nike-6-nike-black-original-imagkfy2mghygwbh.jpeg?q=70",
    description: "Nike Revolution athletic running shoes with soft foam cushioning.",
    category: "men",
    subcategory: "shoes",
    colors: ["#1a202c", "#ffffff"],
    rating: 4.6,
    reviews: 3200,
    badge: "TRENDING",
    sizes: ["6", "7", "8", "9"]
  }
];

export const categories = [
  { name: "Men", path: "/men", image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop" },
  { name: "Women", path: "/women", image: "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=300&h=400&fit=crop" },
  { name: "Wardrobe", path: "/wardrobe", image: "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=300&h=400&fit=crop" },
];

export function shuffleArray<T>(array: T[]): T[] {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}
