import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

const RISK_API =
  "/products/inventory-dashboard-risk-ranking-distribution-action-plan-ranking-details-summary-report-ranking-details";

function App() {
  const [activeMenu, setActiveMenu] = useState("Dashboard");

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [riskAnalysis, setRiskAnalysis] = useState(null);
  const [riskAnalysisLoading, setRiskAnalysisLoading] = useState(false);
  const [riskAnalysisError, setRiskAnalysisError] = useState("");

  const [showAddForm, setShowAddForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [viewingProduct, setViewingProduct] = useState(null);

  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [stockFilter, setStockFilter] = useState("All");
  const [sortBy, setSortBy] = useState("id");
  const [sortOrder, setSortOrder] = useState("asc");
  const [currentPage, setCurrentPage] = useState(1);

  const itemsPerPage = 8;

  const [newProduct, setNewProduct] = useState({
    name: "",
    description: "",
    price: "",
    stock: "",
    category: "General",
  });

  // =========================
  // INITIAL DATA LOAD
  // =========================

  useEffect(() => {
    fetchProducts();
    fetchRiskAnalysis();
  }, []);

  useEffect(() => {
    setCurrentPage(1);
  }, [
    searchTerm,
    categoryFilter,
    stockFilter,
    sortBy,
    sortOrder,
  ]);

  // =========================
  // FETCH PRODUCTS
  // =========================

  const fetchProducts = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/products`);

      if (!response.ok) {
        throw new Error("Failed to fetch products");
      }

      const data = await response.json();

      if (Array.isArray(data)) {
        setProducts(data);
      } else if (Array.isArray(data.products)) {
        setProducts(data.products);
      } else {
        setProducts([]);
      }
    } catch (err) {
      console.error(err);

      setError(
        "Products load nahi ho rahe. Check karo FastAPI server running hai ya nahi."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // FETCH RISK ANALYSIS
  // =========================

  const fetchRiskAnalysis = async () => {
    try {
      setRiskAnalysisLoading(true);
      setRiskAnalysisError("");

      const response = await fetch(`${API_URL}${RISK_API}`);

      if (!response.ok) {
        throw new Error("Failed to fetch risk analysis");
      }

      const data = await response.json();

      setRiskAnalysis(data);
    } catch (err) {
      console.error(err);

      setRiskAnalysisError(
        "Risk Analysis data load nahi ho raha. Check karo FastAPI server running hai ya nahi."
      );
    } finally {
      setRiskAnalysisLoading(false);
    }
  };

  // =========================
  // ADD PRODUCT
  // =========================

  const addProduct = async (e) => {
    e.preventDefault();

    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/products`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: newProduct.name,
          description: newProduct.description,
          price: Number(newProduct.price),
          stock: Number(newProduct.stock),
          category: newProduct.category || "General",
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail || "Failed to add product"
        );
      }

      setNewProduct({
        name: "",
        description: "",
        price: "",
        stock: "",
        category: "General",
      });

      setShowAddForm(false);

      await fetchProducts();
      await fetchRiskAnalysis();
    } catch (err) {
      console.error(err);

      setError(
        err.message || "Product add nahi ho raha."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // UPDATE PRODUCT
  // =========================

  const updateProduct = async (e) => {
    e.preventDefault();

    if (!editingProduct) {
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        `${API_URL}/products/${editingProduct.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: editingProduct.name,
            description: editingProduct.description,
            price: Number(editingProduct.price),
            stock: Number(editingProduct.stock),
            category:
              editingProduct.category || "General",
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail || "Failed to update product"
        );
      }

      setEditingProduct(null);

      await fetchProducts();
      await fetchRiskAnalysis();
    } catch (err) {
      console.error(err);

      setError(
        err.message || "Product update nahi ho raha."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // DELETE PRODUCT
  // =========================

  const deleteProduct = async (id) => {
    const confirmed = window.confirm(
      "Kya aap is product ko delete karna chahte ho?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        `${API_URL}/products/${id}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail || "Failed to delete product"
        );
      }

      await fetchProducts();
      await fetchRiskAnalysis();
    } catch (err) {
      console.error(err);

      setError(
        err.message || "Product delete nahi ho raha."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // HELPERS
  // =========================

  const formatCurrency = (value) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 2,
    }).format(Number(value || 0));
  };

  const getStatus = (stock) => {
    const value = Number(stock || 0);

    if (value <= 0) {
      return "Critical";
    }

    if (value <= 10) {
      return "Medium";
    }

    return "Healthy";
  };

  const getStatusClass = (stock) => {
    const value = Number(stock || 0);

    if (value <= 0) {
      return "critical";
    }

    if (value <= 10) {
      return "medium";
    }

    return "healthy";
  };

  const getRiskClass = (riskLevel) => {
    const value = String(
      riskLevel || ""
    ).toLowerCase();

    if (value === "critical") {
      return "critical";
    }

    if (value === "high") {
      return "high";
    }

    if (value === "medium") {
      return "medium";
    }

    if (value === "low") {
      return "low";
    }

    return "";
  };

  // =========================
  // CATEGORIES
  // =========================

  const categories = useMemo(() => {
    const uniqueCategories = [
      ...new Set(
        products
          .map((product) => product.category)
          .filter((category) => category)
      ),
    ];

    return [
      "All",
      ...uniqueCategories.sort(),
    ];
  }, [products]);

  // =========================
  // FILTER + SORT
  // =========================

  const filteredProducts = useMemo(() => {
    let result = [...products];

    // Search
    if (searchTerm.trim()) {
      const search = searchTerm.toLowerCase();

      result = result.filter((product) => {
        return (
          String(product.name || "")
            .toLowerCase()
            .includes(search) ||
          String(product.description || "")
            .toLowerCase()
            .includes(search) ||
          String(product.category || "")
            .toLowerCase()
            .includes(search)
        );
      });
    }

    // Category
    if (categoryFilter !== "All") {
      result = result.filter(
        (product) =>
          product.category === categoryFilter
      );
    }

    // Stock
    if (stockFilter !== "All") {
      result = result.filter((product) => {
        const stock = Number(
          product.stock || 0
        );

        if (stockFilter === "Out of Stock") {
          return stock <= 0;
        }

        if (stockFilter === "Low Stock") {
          return stock > 0 && stock <= 5;
        }

        if (stockFilter === "Medium Stock") {
          return stock > 5 && stock <= 10;
        }

        if (stockFilter === "Healthy") {
          return stock > 10;
        }

        return true;
      });
    }

    // Sorting
    result.sort((a, b) => {
      let first;
      let second;

      if (sortBy === "price") {
        first = Number(a.price || 0);
        second = Number(b.price || 0);
      } else if (sortBy === "stock") {
        first = Number(a.stock || 0);
        second = Number(b.stock || 0);
      } else if (sortBy === "name") {
        first = String(
          a.name || ""
        ).toLowerCase();

        second = String(
          b.name || ""
        ).toLowerCase();
      } else {
        first = Number(a.id || 0);
        second = Number(b.id || 0);
      }

      if (first < second) {
        return sortOrder === "asc" ? -1 : 1;
      }

      if (first > second) {
        return sortOrder === "asc" ? 1 : -1;
      }

      return 0;
    });

    return result;
  }, [
    products,
    searchTerm,
    categoryFilter,
    stockFilter,
    sortBy,
    sortOrder,
  ]);

  // =========================
  // PAGINATION
  // =========================

  const totalPages = Math.max(
    1,
    Math.ceil(
      filteredProducts.length /
        itemsPerPage
    )
  );

  const paginatedProducts =
    filteredProducts.slice(
      (currentPage - 1) *
        itemsPerPage,
      currentPage * itemsPerPage
    );

  // =========================
  // DASHBOARD CALCULATIONS
  // =========================

  const totalProducts = products.length;

  const totalStock = products.reduce(
    (sum, product) =>
      sum +
      Number(product.stock || 0),
    0
  );

  const inventoryValue = products.reduce(
    (sum, product) =>
      sum +
      Number(product.price || 0) *
        Number(product.stock || 0),
    0
  );

  const lowStockProducts =
    products.filter(
      (product) =>
        Number(product.stock || 0) <= 10
    );

  const mediumRiskProducts =
    products.filter((product) => {
      const stock = Number(
        product.stock || 0
      );

      return stock > 0 && stock <= 10;
    });

  const outOfStockProducts =
    products.filter(
      (product) =>
        Number(product.stock || 0) <= 0
    );

  const healthyProducts =
    products.filter(
      (product) =>
        Number(product.stock || 0) > 10
    );

  // =========================
  // RISK DATA
  // =========================

  const riskDetails =
    riskAnalysis?.risk_ranking_details ||
    [];

  const riskSummary =
    riskAnalysis?.ranking_details_summary_report ||
    {};

  // =========================
  // CHART
  // =========================

  const maxInventoryBarValue =
    Math.max(
      inventoryValue,
      ...products.map(
        (product) =>
          Number(product.price || 0) *
          Number(product.stock || 0)
      ),
      1
    );

  const handleSortChange = (value) => {
    if (sortBy === value) {
      setSortOrder((previous) =>
        previous === "asc"
          ? "desc"
          : "asc"
      );
    } else {
      setSortBy(value);
      setSortOrder("asc");
    }
  };

  // =========================
  // DASHBOARD
  // =========================

  const renderDashboard = () => (
    <>
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>

          <p>
            ShopSphere inventory and
            product management overview.
          </p>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="stats-grid">

        <div className="stat-card">
          <div className="stat-card-icon">
            📦
          </div>

          <div>
            <p>Total Products</p>
            <h2>{totalProducts}</h2>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-icon">
            📊
          </div>

          <div>
            <p>Total Stock</p>
            <h2>{totalStock}</h2>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-icon">
            💰
          </div>

          <div>
            <p>Inventory Value</p>

            <h2>
              {formatCurrency(
                inventoryValue
              )}
            </h2>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-icon">
            ⚠️
          </div>

          <div>
            <p>Medium Risk Products</p>
            <h2>
              {mediumRiskProducts.length}
            </h2>
          </div>
        </div>

      </div>

      <div className="dashboard-grid">

        <section className="dashboard-card">

          <div className="section-header">
            <div>
              <h2>
                Inventory Overview
              </h2>

              <p>
                Inventory value by
                product.
              </p>
            </div>
          </div>

          {products.length === 0 ? (
            <div className="empty-state">
              No products available.
            </div>
          ) : (
            <div className="bar-chart">

              {products
                .slice(0, 8)
                .map((product) => {

                  const value =
                    Number(
                      product.price || 0
                    ) *
                    Number(
                      product.stock || 0
                    );

                  const width =
                    Math.max(
                      4,
                      (value /
                        maxInventoryBarValue) *
                        100
                    );

                  return (
                    <div
                      className="bar-row"
                      key={product.id}
                    >
                      <div
                        className="bar-label"
                        title={
                          product.name
                        }
                      >
                        {product.name}
                      </div>

                      <div className="bar-track">

                        <div
                          className="bar-fill"
                          style={{
                            width: `${width}%`,
                          }}
                        />

                      </div>

                      <div className="bar-value">
                        {formatCurrency(
                          value
                        )}
                      </div>
                    </div>
                  );
                })}

            </div>
          )}

        </section>

        <section className="dashboard-card">

          <div className="section-header">
            <div>
              <h2>
                Inventory Health
              </h2>

              <p>
                Current stock-risk
                distribution.
              </p>
            </div>
          </div>

          <div className="health-list">

            <div className="health-item">

              <span className="health-dot critical" />

              <span>
                Critical / Out of Stock
              </span>

              <strong>
                {outOfStockProducts.length}
              </strong>

            </div>

            <div className="health-item">

              <span className="health-dot medium" />

              <span>
                Medium Risk
              </span>

              <strong>
                {mediumRiskProducts.length}
              </strong>

            </div>

            <div className="health-item">

              <span className="health-dot healthy" />

              <span>
                Healthy
              </span>

              <strong>
                {healthyProducts.length}
              </strong>

            </div>

          </div>

          <div className="health-summary">

            <div>
              <span>Low Stock</span>

              <strong>
                {lowStockProducts.length}
              </strong>
            </div>

            <div>
              <span>Total</span>

              <strong>
                {totalProducts}
              </strong>
            </div>

          </div>

        </section>

      </div>

      <section className="dashboard-card recent-products">

        <div className="section-header">

          <div>
            <h2>
              Recent Products
            </h2>

            <p>
              Latest products
              available in ShopSphere.
            </p>
          </div>

          <button
            className="primary-button"
            onClick={() =>
              setActiveMenu(
                "Products"
              )
            }
          >
            View Products
          </button>

        </div>

        <ProductTable
          products={products.slice(
            0,
            5
          )}
          onView={setViewingProduct}
          onEdit={setEditingProduct}
          onDelete={deleteProduct}
        />

      </section>
    </>
  );

  // =========================
  // PRODUCTS
  // =========================

  const renderProducts = () => (
    <>
      <div className="page-header">

        <div>
          <h1>Products</h1>

          <p>
            Manage ShopSphere
            products and inventory.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={() =>
            setShowAddForm(
              (previous) =>
                !previous
            )
          }
        >
          {showAddForm
            ? "Close Form"
            : "+ Add Product"}
        </button>

      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {showAddForm && (
        <section className="form-card">

          <div className="section-header">

            <div>
              <h2>
                Add Product
              </h2>

              <p>
                Create a new
                ShopSphere product.
              </p>
            </div>

          </div>

          <form
            onSubmit={addProduct}
            className="product-form"
          >

            <div className="form-group">
              <label>
                Product Name
              </label>

              <input
                required
                value={
                  newProduct.name
                }
                onChange={(e) =>
                  setNewProduct({
                    ...newProduct,
                    name:
                      e.target.value,
                  })
                }
                placeholder="Samsung Galaxy S25"
              />
            </div>

            <div className="form-group">

              <label>
                Category
              </label>

              <input
                value={
                  newProduct.category
                }
                onChange={(e) =>
                  setNewProduct({
                    ...newProduct,
                    category:
                      e.target.value,
                  })
                }
                placeholder="Electronics"
              />

            </div>

            <div className="form-group">

              <label>
                Price
              </label>

              <input
                required
                type="number"
                min="0"
                step="0.01"
                value={
                  newProduct.price
                }
                onChange={(e) =>
                  setNewProduct({
                    ...newProduct,
                    price:
                      e.target.value,
                  })
                }
                placeholder="79999"
              />

            </div>

            <div className="form-group">

              <label>
                Stock
              </label>

              <input
                required
                type="number"
                min="0"
                value={
                  newProduct.stock
                }
                onChange={(e) =>
                  setNewProduct({
                    ...newProduct,
                    stock:
                      e.target.value,
                  })
                }
                placeholder="10"
              />

            </div>

            <div className="form-group full-width">

              <label>
                Description
              </label>

              <textarea
                value={
                  newProduct.description
                }
                onChange={(e) =>
                  setNewProduct({
                    ...newProduct,
                    description:
                      e.target.value,
                  })
                }
                placeholder="Product description"
                rows="4"
              />

            </div>

            <div className="form-actions full-width">

              <button
                type="submit"
                className="primary-button"
              >
                Add Product
              </button>

              <button
                type="button"
                className="secondary-button"
                onClick={() =>
                  setShowAddForm(false)
                }
              >
                Cancel
              </button>

            </div>

          </form>

        </section>
      )}

      <section className="table-card">

        <div className="filters-row">

          <input
            className="search-input"
            value={searchTerm}
            onChange={(e) =>
              setSearchTerm(
                e.target.value
              )
            }
            placeholder="Search products..."
          />

          <select
            value={categoryFilter}
            onChange={(e) =>
              setCategoryFilter(
                e.target.value
              )
            }
          >
            {categories.map(
              (category) => (
                <option
                  key={category}
                  value={category}
                >
                  {category}
                </option>
              )
            )}
          </select>

          <select
            value={stockFilter}
            onChange={(e) =>
              setStockFilter(
                e.target.value
              )
            }
          >
            <option value="All">
              All Stock
            </option>

            <option value="Out of Stock">
              Out of Stock
            </option>

            <option value="Low Stock">
              Low Stock (1-5)
            </option>

            <option value="Medium Stock">
              Medium Stock (6-10)
            </option>

            <option value="Healthy">
              Healthy (&gt;10)
            </option>

          </select>

          <select
            value={sortBy}
            onChange={(e) =>
              handleSortChange(
                e.target.value
              )
            }
          >
            <option value="id">
              Sort: ID
            </option>

            <option value="name">
              Sort: Name
            </option>

            <option value="price">
              Sort: Price
            </option>

            <option value="stock">
              Sort: Stock
            </option>

          </select>

          <button
            className="secondary-button"
            onClick={() =>
              setSortOrder(
                (previous) =>
                  previous === "asc"
                    ? "desc"
                    : "asc"
              )
            }
          >
            {sortOrder === "asc"
              ? "↑ Asc"
              : "↓ Desc"}
          </button>

        </div>

        {loading && (
          <div className="loading-message">
            Loading...
          </div>
        )}

        <ProductTable
          products={
            paginatedProducts
          }
          onView={setViewingProduct}
          onEdit={setEditingProduct}
          onDelete={deleteProduct}
        />

        <div className="pagination">

          <button
            className="secondary-button"
            disabled={
              currentPage <= 1
            }
            onClick={() =>
              setCurrentPage(
                (page) =>
                  Math.max(
                    1,
                    page - 1
                  )
              )
            }
          >
            ← Previous
          </button>

          <span>
            Page {currentPage} of{" "}
            {totalPages}
          </span>

          <button
            className="secondary-button"
            disabled={
              currentPage >=
              totalPages
            }
            onClick={() =>
              setCurrentPage(
                (page) =>
                  Math.min(
                    totalPages,
                    page + 1
                  )
              )
            }
          >
            Next →
          </button>

        </div>

      </section>
    </>
  );

  // =========================
  // INVENTORY
  // =========================

  const renderInventory = () => (
    <>
      <div className="page-header">

        <div>
          <h1>Inventory</h1>

          <p>
            Live inventory summary
            from the ShopSphere
            backend.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={fetchProducts}
        >
          ↻ Refresh
        </button>

      </div>

      <div className="stats-grid">

        <div className="stat-card">
          <div className="stat-card-icon">
            📦
          </div>

          <div>
            <p>Total Products</p>
            <h2>
              {totalProducts}
            </h2>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-icon">
            📊
          </div>

          <div>
            <p>Total Stock</p>
            <h2>
              {totalStock}
            </h2>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-icon">
            💰
          </div>

          <div>
            <p>Inventory Value</p>

            <h2>
              {formatCurrency(
                inventoryValue
              )}
            </h2>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-icon">
            ⚠️
          </div>

          <div>
            <p>Low Stock</p>

            <h2>
              {lowStockProducts.length}
            </h2>
          </div>
        </div>

      </div>

      <section className="table-card">

        <div className="section-header">

          <div>
            <h2>
              Inventory Details
            </h2>

            <p>
              Product-level stock
              and inventory value.
            </p>
          </div>

        </div>

        <div className="table-scroll">

          <table className="product-table">

            <thead>
              <tr>
                <th>ID</th>
                <th>Product</th>
                <th>Category</th>
                <th>Price</th>
                <th>Stock</th>
                <th>
                  Inventory Value
                </th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>

              {products.map(
                (product) => {

                  const value =
                    Number(
                      product.price || 0
                    ) *
                    Number(
                      product.stock || 0
                    );

                  return (
                    <tr
                      key={product.id}
                    >
                      <td>
                        #{product.id}
                      </td>

                      <td>
                        {product.name}
                      </td>

                      <td>
                        {product.category ||
                          "General"}
                      </td>

                      <td>
                        {formatCurrency(
                          product.price
                        )}
                      </td>

                      <td>
                        {product.stock}
                      </td>

                      <td>
                        {formatCurrency(
                          value
                        )}
                      </td>

                      <td>
                        <span
                          className={`status ${getStatusClass(
                            product.stock
                          )}`}
                        >
                          {getStatus(
                            product.stock
                          )}
                        </span>
                      </td>

                    </tr>
                  );
                }
              )}

            </tbody>

          </table>

        </div>

      </section>
    </>
  );

  // =========================
  // LOW STOCK
  // =========================

  const renderLowStock = () => (
    <>
      <div className="page-header">

        <div>
          <h1>Low Stock</h1>

          <p>
            Products requiring
            inventory attention.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={fetchProducts}
        >
          ↻ Refresh
        </button>

      </div>

      <div className="stats-grid">

        <div className="stat-card">

          <div className="stat-card-icon">
            ⚠️
          </div>

          <div>
            <p>
              Low Stock Products
            </p>

            <h2>
              {lowStockProducts.length}
            </h2>
          </div>

        </div>

        <div className="stat-card">

          <div className="stat-card-icon">
            🚨
          </div>

          <div>
            <p>Out of Stock</p>

            <h2>
              {outOfStockProducts.length}
            </h2>
          </div>

        </div>

      </div>

      <section className="table-card">

        <div className="section-header">

          <div>
            <h2>
              Low Stock Products
            </h2>

            <p>
              Products with stock
              of 10 or less.
            </p>
          </div>

        </div>

        {lowStockProducts.length ===
        0 ? (
          <div className="empty-state">
            No low-stock products
            found.
          </div>
        ) : (
          <ProductTable
            products={[
              ...lowStockProducts,
            ].sort(
              (a, b) =>
                Number(
                  a.stock || 0
                ) -
                Number(
                  b.stock || 0
                )
            )}
            onView={
              setViewingProduct
            }
            onEdit={
              setEditingProduct
            }
            onDelete={
              deleteProduct
            }
          />
        )}

      </section>
    </>
  );

  // =========================
  // RISK ANALYSIS
  // =========================

  const renderRiskAnalysis = () => (
    <>
      <div className="page-header">

        <div>
          <h1>
            Risk Analysis
          </h1>

          <p>
            Backend-powered
            inventory risk ranking
            and action plan.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={
            fetchRiskAnalysis
          }
          disabled={
            riskAnalysisLoading
          }
        >
          {riskAnalysisLoading
            ? "Loading..."
            : "↻ Refresh Risk"}
        </button>

      </div>

      {riskAnalysisError && (
        <div className="error-message">
          {riskAnalysisError}
        </div>
      )}

      {riskAnalysisLoading &&
        !riskAnalysis && (
          <div className="loading-message">
            Loading Risk Analysis...
          </div>
        )}

      {riskAnalysis && (
        <>
          <div className="stats-grid">

            <div className="stat-card">

              <div className="stat-card-icon">
                📦
              </div>

              <div>
                <p>
                  Total Products
                </p>

                <h2>
                  {
                    riskSummary.total_products ??
                    0
                  }
                </h2>
              </div>

            </div>

            <div className="stat-card">

              <div className="stat-card-icon">
                📊
              </div>

              <div>
                <p>
                  Total Stock
                </p>

                <h2>
                  {
                    riskSummary.total_stock ??
                    0
                  }
                </h2>
              </div>

            </div>

            <div className="stat-card">

              <div className="stat-card-icon">
                💰
              </div>

              <div>
                <p>
                  Inventory Value
                </p>

                <h2>
                  {formatCurrency(
                    riskSummary.total_inventory_value
                  )}
                </h2>
              </div>

            </div>

            <div className="stat-card">

              <div className="stat-card-icon">
                🚨
              </div>

              <div>
                <p>
                  Overall Priority
                </p>

                <h2>
                  {
                    riskSummary.overall_priority ||
                    "N/A"
                  }
                </h2>
              </div>

            </div>

          </div>

          <section className="dashboard-card">

            <div className="section-header">

              <div>
                <h2>
                  Overall Action
                </h2>

                <p>
                  {
                    riskSummary.overall_reason ||
                    "No reason provided."
                  }
                </p>
              </div>

              <span
                className={`status ${getRiskClass(
                  riskSummary.overall_priority
                )}`}
              >
                {
                  riskSummary.overall_priority ||
                  "N/A"
                }
              </span>

            </div>

            <div className="risk-action-box">

              <strong>
                {
                  riskSummary.overall_action ||
                  "No immediate action"
                }
              </strong>

              <p>
                This action is
                generated from the
                current inventory
                risk distribution.
              </p>

            </div>

          </section>

          <section className="table-card">

            <div className="section-header">

              <div>
                <h2>
                  Risk Ranking Details
                </h2>

                <p>
                  Risk buckets returned
                  directly by the
                  FastAPI analytics
                  endpoint.
                </p>
              </div>

            </div>

            <div className="table-scroll">

              <table className="product-table risk-table">

                <thead>

                  <tr>
                    <th>Rank</th>
                    <th>Risk Level</th>
                    <th>Products</th>
                    <th>Percentage</th>
                    <th>Total Stock</th>
                    <th>
                      Inventory Value
                    </th>
                    <th>Priority</th>
                    <th>Action</th>
                    <th>
                      Recommended Step
                    </th>
                  </tr>

                </thead>

                <tbody>

                  {riskDetails.map(
                    (item) => (
                      <tr
                        key={`${item.rank}-${item.risk_level}`}
                      >

                        <td>
                          #{item.rank}
                        </td>

                        <td>

                          <span
                            className={`status ${getRiskClass(
                              item.risk_level
                            )}`}
                          >
                            {
                              item.risk_level
                            }
                          </span>

                        </td>

                        <td>
                          {
                            item.product_count
                          }
                        </td>

                        <td>
                          {
                            item.percentage
                          }%
                        </td>

                        <td>
                          {
                            item.total_stock
                          }
                        </td>

                        <td>
                          {formatCurrency(
                            item.inventory_value
                          )}
                        </td>

                        <td>
                          {
                            item.priority
                          }
                        </td>

                        <td>
                          {
                            item.action
                          }
                        </td>

                        <td>
                          {
                            item.recommended_step
                          }
                        </td>

                      </tr>
                    )
                  )}

                </tbody>

              </table>

            </div>

          </section>
        </>
      )}
    </>
  );

  // =========================
  // REPORTS
  // =========================

  const renderReports = () => (
    <>
      <div className="page-header">

        <div>
          <h1>Reports</h1>

          <p>
            ShopSphere inventory
            analytics and
            operational reports.
          </p>
        </div>

      </div>

      <div className="dashboard-grid">

        <section className="dashboard-card">

          <h2>
            Inventory Risk Report
          </h2>

          <p>
            Open the Risk Analysis
            module to view the
            latest backend
            risk-ranking report.
          </p>

          <button
            className="primary-button"
            onClick={() =>
              setActiveMenu(
                "Risk Analysis"
              )
            }
          >
            Open Risk Analysis
          </button>

        </section>

        <section className="dashboard-card">

          <h2>
            Inventory Summary
          </h2>

          <div className="report-summary">

            <div>
              <span>
                Total Products
              </span>

              <strong>
                {totalProducts}
              </strong>
            </div>

            <div>
              <span>
                Total Stock
              </span>

              <strong>
                {totalStock}
              </strong>
            </div>

            <div>
              <span>
                Inventory Value
              </span>

              <strong>
                {formatCurrency(
                  inventoryValue
                )}
              </strong>
            </div>

            <div>
              <span>
                Low Stock
              </span>

              <strong>
                {
                  lowStockProducts.length
                }
              </strong>
            </div>

          </div>

        </section>

      </div>
    </>
  );

  // =========================
  // MAIN UI
  // =========================

  return (
    <div className="app">

      {/* SIDEBAR */}

      <aside className="sidebar">

        <div className="logo-area">

          <div className="logo-icon">
            S
          </div>

          <div>
            <h2>
              ShopSphere
            </h2>

            <span>
              Cloud DevOps Store
            </span>
          </div>

        </div>

        <nav className="sidebar-nav">

          <p className="nav-title">
            MAIN MENU
          </p>

          {[
            "Dashboard",
            "Products",
            "Inventory",
            "Low Stock",
            "Risk Analysis",
            "Reports",
          ].map((menu) => (
            <button
              key={menu}
              className={`nav-item ${
                activeMenu === menu
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                setActiveMenu(menu)
              }
            >

              <span className="nav-icon">

                {menu ===
                  "Dashboard" &&
                  "⌂"}

                {menu ===
                  "Products" &&
                  "📦"}

                {menu ===
                  "Inventory" &&
                  "📊"}

                {menu ===
                  "Low Stock" &&
                  "⚠️"}

                {menu ===
                  "Risk Analysis" &&
                  "🚨"}

                {menu ===
                  "Reports" &&
                  "📄"}

              </span>

              {menu}

            </button>
          ))}

        </nav>

        <div className="sidebar-footer">

          <div className="devops-badge">

            <strong>
              DevOps Project
            </strong>

            <span>
              FastAPI + React
            </span>

          </div>

        </div>

      </aside>

      {/* MAIN CONTENT */}

      <main className="main-content">

        <header className="topbar">

          <div>

            <span className="breadcrumb">
              ShopSphere
            </span>

            <strong>
              {" "}
              / {activeMenu}
            </strong>

          </div>

          <div className="topbar-status">

            <span className="online-dot" />

            API Connected

          </div>

        </header>

        <div className="content-area">

          {activeMenu ===
            "Dashboard" &&
            renderDashboard()}

          {activeMenu ===
            "Products" &&
            renderProducts()}

          {activeMenu ===
            "Inventory" &&
            renderInventory()}

          {activeMenu ===
            "Low Stock" &&
            renderLowStock()}

          {activeMenu ===
            "Risk Analysis" &&
            renderRiskAnalysis()}

          {activeMenu ===
            "Reports" &&
            renderReports()}

        </div>

      </main>

      {/* VIEW PRODUCT MODAL */}

      {viewingProduct && (
        <div
          className="modal-overlay"
          onClick={() =>
            setViewingProduct(null)
          }
        >

          <div
            className="modal-card"
            onClick={(e) =>
              e.stopPropagation()
            }
          >

            <div className="modal-header">

              <div>

                <h2>
                  Product Details
                </h2>

                <p>
                  Product #
                  {
                    viewingProduct.id
                  }
                </p>

              </div>

              <button
                className="modal-close"
                onClick={() =>
                  setViewingProduct(
                    null
                  )
                }
              >
                ×
              </button>

            </div>

            <div className="product-detail-grid">

              <div>
                <span>Name</span>

                <strong>
                  {
                    viewingProduct.name
                  }
                </strong>
              </div>

              <div>
                <span>
                  Category
                </span>

                <strong>
                  {
                    viewingProduct.category ||
                    "General"
                  }
                </strong>
              </div>

              <div>
                <span>Price</span>

                <strong>
                  {formatCurrency(
                    viewingProduct.price
                  )}
                </strong>
              </div>

              <div>
                <span>Stock</span>

                <strong>
                  {
                    viewingProduct.stock
                  }
                </strong>
              </div>

              <div className="full-width">

                <span>
                  Description
                </span>

                <strong>
                  {
                    viewingProduct.description ||
                    "No description available."
                  }
                </strong>

              </div>

            </div>

            <div className="modal-footer">

              <button
                className="secondary-button"
                onClick={() =>
                  setViewingProduct(
                    null
                  )
                }
              >
                Close
              </button>

              <button
                className="primary-button"
                onClick={() => {
                  setEditingProduct(
                    viewingProduct
                  );

                  setViewingProduct(
                    null
                  );
                }}
              >
                Edit Product
              </button>

            </div>

          </div>

        </div>
      )}

      {/* EDIT PRODUCT MODAL */}

      {editingProduct && (
        <div
          className="modal-overlay"
          onClick={() =>
            setEditingProduct(null)
          }
        >

          <div
            className="modal-card"
            onClick={(e) =>
              e.stopPropagation()
            }
          >

            <div className="modal-header">

              <div>

                <h2>
                  Edit Product
                </h2>

                <p>
                  Update product #
                  {
                    editingProduct.id
                  }
                </p>

              </div>

              <button
                className="modal-close"
                onClick={() =>
                  setEditingProduct(
                    null
                  )
                }
              >
                ×
              </button>

            </div>

            <form
              onSubmit={updateProduct}
              className="product-form"
            >

              <div className="form-group">

                <label>
                  Product Name
                </label>

                <input
                  required
                  value={
                    editingProduct.name ||
                    ""
                  }
                  onChange={(e) =>
                    setEditingProduct({
                      ...editingProduct,
                      name:
                        e.target.value,
                    })
                  }
                />

              </div>

              <div className="form-group">

                <label>
                  Category
                </label>

                <input
                  value={
                    editingProduct.category ||
                    "General"
                  }
                  onChange={(e) =>
                    setEditingProduct({
                      ...editingProduct,
                      category:
                        e.target.value,
                    })
                  }
                />

              </div>

              <div className="form-group">

                <label>
                  Price
                </label>

                <input
                  required
                  type="number"
                  min="0"
                  step="0.01"
                  value={
                    editingProduct.price ??
                    ""
                  }
                  onChange={(e) =>
                    setEditingProduct({
                      ...editingProduct,
                      price:
                        e.target.value,
                    })
                  }
                />

              </div>

              <div className="form-group">

                <label>
                  Stock
                </label>

                <input
                  required
                  type="number"
                  min="0"
                  value={
                    editingProduct.stock ??
                    ""
                  }
                  onChange={(e) =>
                    setEditingProduct({
                      ...editingProduct,
                      stock:
                        e.target.value,
                    })
                  }
                />

              </div>

              <div className="form-group full-width">

                <label>
                  Description
                </label>

                <textarea
                  rows="4"
                  value={
                    editingProduct.description ||
                    ""
                  }
                  onChange={(e) =>
                    setEditingProduct({
                      ...editingProduct,
                      description:
                        e.target.value,
                    })
                  }
                />

              </div>

              <div className="form-actions full-width">

                <button
                  type="submit"
                  className="primary-button"
                >
                  Save Changes
                </button>

                <button
                  type="button"
                  className="secondary-button"
                  onClick={() =>
                    setEditingProduct(
                      null
                    )
                  }
                >
                  Cancel
                </button>

              </div>

            </form>

          </div>

        </div>
      )}

    </div>
  );
}

// =====================================================
// PRODUCT TABLE COMPONENT
// =====================================================

function ProductTable({
  products,
  onView,
  onEdit,
  onDelete,
}) {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat(
      "en-IN",
      {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2,
      }
    ).format(
      Number(value || 0)
    );
  };

  const getStatus = (stock) => {
    const value = Number(
      stock || 0
    );

    if (value <= 0) {
      return "Critical";
    }

    if (value <= 10) {
      return "Medium";
    }

    return "Healthy";
  };

  const getStatusClass = (stock) => {
    const value = Number(
      stock || 0
    );

    if (value <= 0) {
      return "critical";
    }

    if (value <= 10) {
      return "medium";
    }

    return "healthy";
  };

  if (
    !products ||
    products.length === 0
  ) {
    return (
      <div className="empty-state">
        No products found.
      </div>
    );
  }

  return (
    <div className="table-scroll">

      <table className="product-table">

        <thead>

          <tr>

            <th>ID</th>

            <th>
              Product
            </th>

            <th>
              Category
            </th>

            <th>
              Price
            </th>

            <th>
              Stock
            </th>

            <th>
              Status
            </th>

            <th>
              Actions
            </th>

          </tr>

        </thead>

        <tbody>

          {products.map(
            (product) => (
              <tr
                key={product.id}
              >

                <td>
                  #{product.id}
                </td>

                <td>

                  <div className="product-name-cell">

                    <strong>
                      {
                        product.name
                      }
                    </strong>

                    <span>
                      {product.description
                        ? String(
                            product.description
                          ).slice(
                            0,
                            45
                          )
                        : "No description"}
                    </span>

                  </div>

                </td>

                <td>
                  {
                    product.category ||
                    "General"
                  }
                </td>

                <td>
                  {formatCurrency(
                    product.price
                  )}
                </td>

                <td>
                  {
                    product.stock
                  }
                </td>

                <td>

                  <span
                    className={`status ${getStatusClass(
                      product.stock
                    )}`}
                  >
                    {
                      getStatus(
                        product.stock
                      )
                    }
                  </span>

                </td>

                <td>

                  <div className="action-buttons">

                    <button
                      className="icon-button"
                      title="View"
                      onClick={() =>
                        onView(
                          product
                        )
                      }
                    >
                      👁
                    </button>

                    <button
                      className="icon-button"
                      title="Edit"
                      onClick={() =>
                        onEdit(
                          product
                        )
                      }
                    >
                      ✏️
                    </button>

                    <button
                      className="icon-button delete"
                      title="Delete"
                      onClick={() =>
                        onDelete(
                          product.id
                        )
                      }
                    >
                      🗑
                    </button>

                  </div>

                </td>

              </tr>
            )
          )}

        </tbody>

      </table>

    </div>
  );
}

export default App;