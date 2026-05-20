import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Shirt, Sparkles, Plus, X } from "lucide-react";
import { WardrobeItem } from "@/data/products";
import { products } from "@/data/products";
import { ProductCard } from "@/components/ProductCard";
import { api, mapProduct } from "@/lib/api";

const DUMMY_WARDROBE: WardrobeItem[] = [
  { id: "w1", image: "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=300&h=400&fit=crop", name: "Blue Oxford Shirt", category: "topwear", color: "#1a365d", dateAdded: "2026-03-20" },
  { id: "w2", image: "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=300&h=400&fit=crop", name: "Khaki Chinos", category: "bottomwear", color: "#744210", dateAdded: "2026-03-18" },
  { id: "w3", image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300&h=400&fit=crop", name: "Red Sneakers", category: "footwear", color: "#e53e3e", dateAdded: "2026-03-15" },
  { id: "w4", image: "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=400&fit=crop", name: "Black Leather Jacket", category: "topwear", color: "#1a202c", dateAdded: "2026-03-12" },
  { id: "w5", image: "https://images.unsplash.com/photo-1591047990635-8ddd4971f7da?w=300&h=400&fit=crop", name: "White Formal Shirt", category: "topwear", color: "#f7fafc", dateAdded: "2026-03-10" },
  { id: "w6", image: "https://images.unsplash.com/photo-1506629082632-41ad64bd3d66?w=300&h=400&fit=crop", name: "Black Crop Top", category: "topwear", color: "#1a202c", dateAdded: "2026-03-08" },
  { id: "w7", image: "https://images.unsplash.com/photo-1589223707857-401a253ee828?w=300&h=400&fit=crop", name: "Floral Midi Dress", category: "ethnic", color: "#fbb6ce", dateAdded: "2026-03-05" },
  { id: "w8", image: "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=300&h=400&fit=crop", name: "Silver Watch", category: "accessories", color: "#c0c0c0", dateAdded: "2026-03-03" },
  { id: "w9", image: "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=300&h=400&fit=crop", name: "Aviator Sunglasses", category: "accessories", color: "#1a202c", dateAdded: "2026-03-01" },
];

const categoryFilters: WardrobeItem["category"][] = ["topwear", "bottomwear", "footwear", "accessories", "ethnic"];
const USER_ID = "demo-user-1";
const occasionOptions = ["casual", "formal", "party", "business", "outing", "evening", "sports"];

const WardrobePage = () => {
  const [wardrobe, setWardrobe] = useState<WardrobeItem[]>(DUMMY_WARDROBE);
  const [selectedItem, setSelectedItem] = useState<WardrobeItem | null>(null);
  const [filter, setFilter] = useState<string>("all");
  const [occasion, setOccasion] = useState<string>("casual");
  const [isLoadingRecs, setIsLoadingRecs] = useState(false);
  const [isLoadingAIAdvice, setIsLoadingAIAdvice] = useState(false);
  const [apiRecs, setApiRecs] = useState<{ wardrobeMatches: WardrobeItem[]; productMatches: any[] } | null>(null);
  const [openAIAdvice, setOpenAIAdvice] = useState<string | null>(null);

  const filtered = filter === "all" ? wardrobe : wardrobe.filter((i) => i.category === filter);

  // Simple AI recommendation: suggest items from different categories + matching products
  const getRecommendations = (item: WardrobeItem) => {
    const otherItems = wardrobe.filter((w) => w.id !== item.id && w.category !== item.category);
    const matchingProducts = products.filter((p) => {
      if (item.category === "topwear") return p.subcategory === "trousers" || p.subcategory === "shorts";
      if (item.category === "bottomwear") return p.subcategory === "shirts" || p.subcategory === "tops";
      return true;
    }).slice(0, 4);
    return { wardrobeMatches: otherItems, productMatches: matchingProducts };
  };

  const handleUpload = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "image/*";
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const url = URL.createObjectURL(file);
        const newItem: WardrobeItem = {
          id: `w${Date.now()}`,
          image: url,
          name: file.name.replace(/\.[^.]+$/, ""),
          category: "topwear",
          color: "#666",
          dateAdded: new Date().toISOString().split("T")[0],
        };
        setWardrobe((prev) => [newItem, ...prev]);
        api.createWardrobeItem({
          user_id: USER_ID,
          image_url: "https://images.unsplash.com/photo-1445205170230-053b83016050?w=500&h=700&fit=crop",
          category: newItem.category,
          primary_color: newItem.color,
          occasion: [occasion],
          detected_tags: [newItem.category],
        }).catch(() => {
          // Keep UI responsive even if backend save fails.
        });
      }
    };
    input.click();
  };

  const loadRecommendations = async () => {
    if (!selectedItem) return;
    setIsLoadingRecs(true);
    try {
      const response = await api.getOutfitRecommendations({
        user_id: USER_ID,
        occasion,
        category: selectedItem.category,
        primary_color: selectedItem.color,
        tags: [selectedItem.category],
        limit: 6,
      });

      const wardrobeMatches = (response.wardrobe_matches || []).map((item: any) => ({
        id: item.id || `w-${Math.random().toString(36).slice(2, 9)}`,
        image: item.image_url || item.image || selectedItem.image,
        name: item.name || item.title || "Wardrobe Item",
        category: (item.category as WardrobeItem["category"]) || "topwear",
        color: item.primary_color || "#666",
        dateAdded: item.uploaded_at?.split("T")?.[0] || new Date().toISOString().split("T")[0],
      }));
      const productMatches = (response.external_matches || []).map(mapProduct);

      setApiRecs({ wardrobeMatches, productMatches });
    } catch {
      setApiRecs(null);
    } finally {
      setIsLoadingRecs(false);
    }
  };

  const loadOpenAIAdvice = async () => {
    if (!selectedItem) return;
    setIsLoadingAIAdvice(true);
    setOpenAIAdvice(null);
    try {
      const response = await api.getOpenAIRecommendations({
        user_id: USER_ID,
        wardrobe: wardrobe.map((item) => ({
          name: item.name,
          category: item.category,
          color: item.color,
          occasion: occasion,
        })),
        query: `Suggest a styling recommendation for ${selectedItem.name} for a ${occasion} look.`,
        occasion,
        gender: "unisex",
        style: "casual streetwear",
        limit: 1,
      });
      setOpenAIAdvice(response.recommendation || "No recommendation returned.");
    } catch {
      setOpenAIAdvice("Unable to fetch AI styling advice right now.");
    } finally {
      setIsLoadingAIAdvice(false);
    }
  };

  const recs = selectedItem ? (apiRecs || getRecommendations(selectedItem)) : null;

  return (
    <div className="container py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display text-3xl font-bold text-foreground">My Wardrobe</h1>
          <p className="text-muted-foreground mt-1">Upload clothes and get AI-powered outfit suggestions</p>
        </div>
        <button
          onClick={handleUpload}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg gradient-primary text-primary-foreground font-semibold text-sm hover:opacity-90 transition-opacity"
        >
          <Plus className="w-4 h-4" /> Add Item
        </button>
      </div>

      {/* Category filters */}
      <div className="flex gap-2 flex-wrap mb-6">
        <button
          onClick={() => setFilter("all")}
          className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
            filter === "all" ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground hover:bg-primary/10"
          }`}
        >
          All ({wardrobe.length})
        </button>
        {categoryFilters.map((cat) => (
          <button
            key={cat}
            onClick={() => setFilter(cat)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium capitalize transition-colors ${
              filter === cat ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground hover:bg-primary/10"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Wardrobe grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {filtered.map((item) => (
          <motion.div
            key={item.id}
            layout
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            onClick={() => setSelectedItem(item)}
            className={`cursor-pointer rounded-lg overflow-hidden shadow-product hover:shadow-product-hover transition-all ${
              selectedItem?.id === item.id ? "ring-2 ring-primary" : ""
            }`}
          >
            <div className="aspect-[3/4] overflow-hidden">
              <img src={item.image} alt={item.name} className="w-full h-full object-cover" />
            </div>
            <div className="p-2.5 bg-card">
              <p className="text-sm font-medium text-foreground truncate">{item.name}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className="w-3 h-3 rounded-full border border-border" style={{ backgroundColor: item.color }} />
                <span className="text-xs text-muted-foreground capitalize">{item.category}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {wardrobe.length === 0 && (
        <div className="text-center py-20">
          <Shirt className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">Your wardrobe is empty. Upload some clothes to get started!</p>
        </div>
      )}

      {/* AI Recommendations Panel */}
      <AnimatePresence>
        {selectedItem && recs && (
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 40 }}
            className="mt-12 bg-card rounded-2xl border border-border p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-primary" />
                <h2 className="font-display text-xl font-bold text-foreground">
                  AI Suggestions for "{selectedItem.name}"
                </h2>
              </div>
              <div className="flex items-center gap-2">
                <select
                  value={occasion}
                  onChange={(e) => setOccasion(e.target.value)}
                  className="px-3 py-1.5 rounded-md border border-border bg-background text-sm"
                >
                  {occasionOptions.map((value) => (
                    <option key={value} value={value}>
                      {value}
                    </option>
                  ))}
                </select>
                <button
                  onClick={loadRecommendations}
                  className="px-3 py-1.5 rounded-md bg-primary text-primary-foreground text-sm hover:bg-primary/90"
                  disabled={isLoadingRecs}
                >
                  {isLoadingRecs ? "Matching..." : "Match for Occasion"}
                </button>
                <button
                  onClick={loadOpenAIAdvice}
                  className="px-3 py-1.5 rounded-md bg-muted text-foreground text-sm hover:bg-muted/90"
                  disabled={isLoadingAIAdvice}
                >
                  {isLoadingAIAdvice ? "Styling..." : "AI Style Advice"}
                </button>
                <button onClick={() => setSelectedItem(null)} className="p-1.5 rounded-md hover:bg-muted">
                  <X className="w-5 h-5 text-muted-foreground" />
                </button>
              </div>
            </div>

            {recs.wardrobeMatches.length > 0 && (
              <div className="mb-8">
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">From Your Wardrobe</h3>
                <div className="flex gap-3 overflow-x-auto pb-2">
                  {recs.wardrobeMatches.map((item) => (
                    <div key={item.id} className="flex-shrink-0 w-28">
                      <div className="aspect-[3/4] rounded-lg overflow-hidden shadow-product">
                        <img src={item.image} alt={item.name} className="w-full h-full object-cover" />
                      </div>
                      <p className="text-xs mt-1.5 font-medium text-foreground truncate">{item.name}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {openAIAdvice && (
              <div className="mb-8 rounded-2xl border border-border bg-muted p-4">
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-2">AI Styling Advice</h3>
                <p className="text-sm leading-6 text-foreground">{openAIAdvice}</p>
              </div>
            )}

            <div>
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">Shop Matching Products</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {recs.productMatches.map((p, i) => (
                  <ProductCard key={p.id} product={p} index={i} />
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default WardrobePage;
