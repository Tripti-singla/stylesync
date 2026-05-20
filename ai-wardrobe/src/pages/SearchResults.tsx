import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { ArrowRight, Search, Loader } from "lucide-react";
import { ProductCard } from "@/components/ProductCard";
import { api } from "@/lib/api";

const SearchResults = () => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get("q")?.trim() || "";
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!query) {
      setResults([]);
      return;
    }

    const fetchResults = async () => {
      try {
        setLoading(true);
        const data = await api.getProducts({ search: query, limit: 100 });
        setResults(data);
        setError(null);
      } catch (err) {
        console.error("Search failed:", err);
        setError((err as Error).message);
        setResults([]);
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [query]);

  return (
    <div className="container py-10">
      <div className="mb-6 sm:mb-8">
        <div className="flex flex-col gap-2">
          <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-primary text-xs sm:text-sm font-semibold">
            <Search className="w-3 h-3 sm:w-4 sm:h-4" />
            Search results for "{query || "..."}"
          </div>
          <h1 className="text-2xl sm:text-3xl font-display font-bold text-foreground">Find what you need</h1>
          <p className="text-muted-foreground text-sm sm:text-base max-w-2xl">
            Search across products by name, brand, category, and subcategory.
          </p>
        </div>
      </div>

      {!query ? (
        <div className="rounded-3xl border border-border bg-card p-10 text-center text-muted-foreground">
          Enter a search term in the navbar to find products.
        </div>
      ) : loading ? (
        <div className="flex justify-center items-center h-96">
          <Loader className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : error ? (
        <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-destructive">
          Search failed: {error}
        </div>
      ) : results.length === 0 ? (
        <div className="rounded-3xl border border-border bg-card p-10 text-center">
          <p className="text-lg font-medium text-foreground mb-2">No products found for "{query}".</p>
          <p className="text-sm text-muted-foreground mb-4">Try another keyword or browse our categories.</p>
          <Link to="/" className="inline-flex items-center gap-2 px-5 py-2 rounded-full border border-border text-sm font-semibold hover:bg-muted transition-colors">
            Browse home <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          {results.map((product, index) => (
            <ProductCard key={product.id} product={product} index={index} />
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchResults;
