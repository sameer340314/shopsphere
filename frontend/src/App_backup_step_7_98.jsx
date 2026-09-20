import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [activeMenu, setActiveMenu] = useState("Dashboard");

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showAddForm, setShowAddForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [viewingProduct, setViewingProduct] = useState(null);

  // SEARCH & FILTER STATE
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [stockFilter, setStockFilter] = useState("All");

  // SORT STATE
  const [sortOption, setSortOption] = useState("default");

  // PAGINATION STATE
  const [currentPage, setCurrentPage] = useState(1);
  const [productsPerPage, setProductsPerPage] = useState(5);

  const [newProduct, setNewProduct] = useState({
    name: "",
    description: "",
    price: "",
    stock: "",
    category: "General",
  });

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/products`);

      if (!response.ok) {
        throw new Error("Failed to fetch products");
      }

      const data = await response.json();

      const productList = Array.isArray(data)
        ? data
        : data.products || [];

      setProducts(productList);
    } catch (err) {
      console.error(err);

      setError(
        "Backend se data load nahi ho raha. Check karo FastAPI server running hai ya nahi."
      );
    } finally {
      setLoading(false);
    }
  };

  // ==================================================
  // ADD PRODUCT
  // ==================================================

  const addProduct = async (event) => {
    event.preventDefault();

    try {
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

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail
            ? JSON.stringify(data.detail)
            : "Product creation failed"
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
      setCurrentPage(1);

      await fetchProducts();
    } catch (err) {
      console.error(err);

      setError(`Product add nahi hua: ${err.message}`);
    }
  };

  // ==================================================
  // UPDATE PRODUCT
  // ==================================================

  const updateProduct = async (event) => {
    event.preventDefault();

    if (!editingProduct) {
      return;
    }

    try {
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
            category: editingProduct.category || "General",
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail
            ? JSON.stringify(data.detail)
            : "Product update failed"
        );
      }

      setEditingProduct(null);

      await fetchProducts();
    } catch (err) {
      console.error(err);

      setError(`Product update nahi hua: ${err.message}`);
    }
  };

  // ==================================================
  // VIEW PRODUCT DETAILS
  // ==================================================

  const openProductDetails = (product) => {
    setViewingProduct(product);
  };

  const closeProductDetails = () => {
    setViewingProduct(null);
  };

  // ==================================================
  // DELETE PRODUCT
  // ==================================================

  const deleteProduct = async (productId) => {
    const confirmed = window.confirm(
      "Kya aap is product ko delete karna chahte ho?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");

      const response = await fetch(
        `${API_URL}/products/${productId}`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail
            ? JSON.stringify(data.detail)
            : "Product delete failed"
        );
      }

      await fetchProducts();
    } catch (err) {
      console.error(err);

      setError(`Product delete nahi hua: ${err.message}`);
    }
  };

  // ==================================================
  // DASHBOARD CALCULATIONS
  // ==================================================

  const totalProducts = products.length;

  const totalStock = products.reduce(
    (total, product) =>
      total + Number(product.stock || 0),
    0
  );

  const inventoryValue = products.reduce(
    (total, product) =>
      total +
      Number(product.price || 0) *
        Number(product.stock || 0),
    0
  );

  const mediumRiskProducts = products.filter((product) => {
    const stock = Number(product.stock || 0);

    return stock > 0 && stock <= 10;
  }).length;

  // ==================================================
  // HELPERS
  // ==================================================

  const formatCurrency = (value) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(value);
  };

  const getStatus = (stock) => {
    if (stock <= 0) return "Critical";
    if (stock <= 10) return "Medium";
    return "Healthy";
  };

  const getStatusClass = (stock) => {
    if (stock <= 0) return "critical";
    if (stock <= 10) return "medium";
    return "healthy";
  };

  // ==================================================
  // PRODUCT SEARCH & FILTER
  // ==================================================

  const categories = [
    "All",
    ...new Set(
      products
        .map((product) => product.category || "General")
        .filter(Boolean)
    ),
  ];

  const filteredProducts = products.filter((product) => {
    const name = (product.name || "").toLowerCase();
    const category = product.category || "General";
    const stock = Number(product.stock || 0);

    const matchesSearch =
      name.includes(searchTerm.toLowerCase());

    const matchesCategory =
      categoryFilter === "All" ||
      category === categoryFilter;

    let matchesStock = true;

    if (stockFilter === "Healthy") {
      matchesStock = stock > 10;
    }

    if (stockFilter === "Medium") {
      matchesStock = stock > 0 && stock <= 10;
    }

    if (stockFilter === "Critical") {
      matchesStock = stock <= 0;
    }

    return (
      matchesSearch &&
      matchesCategory &&
      matchesStock
    );
  });

  // ==================================================
  // PRODUCT SORTING
  // ==================================================

  const sortedProducts = [...filteredProducts].sort(
    (a, b) => {
      if (sortOption === "name-asc") {
        return (a.name || "").localeCompare(
          b.name || ""
        );
      }

      if (sortOption === "name-desc") {
        return (b.name || "").localeCompare(
          a.name || ""
        );
      }

      if (sortOption === "price-asc") {
        return (
          Number(a.price || 0) -
          Number(b.price || 0)
        );
      }

      if (sortOption === "price-desc") {
        return (
          Number(b.price || 0) -
          Number(a.price || 0)
        );
      }

      if (sortOption === "stock-asc") {
        return (
          Number(a.stock || 0) -
          Number(b.stock || 0)
        );
      }

      if (sortOption === "stock-desc") {
        return (
          Number(b.stock || 0) -
          Number(a.stock || 0)
        );
      }

      return 0;
    }
  );

  // ==================================================
  // PAGINATION
  // ==================================================

  const totalFilteredProducts =
    sortedProducts.length;

  const totalPages =
    Math.ceil(
      totalFilteredProducts /
        productsPerPage
    ) || 1;

  const safeCurrentPage = Math.min(
    currentPage,
    totalPages
  );

  const startIndex =
    (safeCurrentPage - 1) *
    productsPerPage;

  const endIndex =
    startIndex + productsPerPage;

  const paginatedProducts =
    sortedProducts.slice(
      startIndex,
      endIndex
    );

  const goToPreviousPage = () => {
    setCurrentPage((page) =>
      Math.max(page - 1, 1)
    );
  };

  const goToNextPage = () => {
    setCurrentPage((page) =>
      Math.min(page + 1, totalPages)
    );
  };

  const goToPage = (page) => {
    setCurrentPage(page);
  };

  const handleProductsPerPageChange = (event) => {
    setProductsPerPage(
      Number(event.target.value)
    );
    setCurrentPage(1);
  };

  // ==================================================
  // FILTER / SORT CHANGE HANDLERS
  // ==================================================

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
    setCurrentPage(1);
  };

  const handleCategoryChange = (event) => {
    setCategoryFilter(event.target.value);
    setCurrentPage(1);
  };

  const handleStockFilterChange = (event) => {
    setStockFilter(event.target.value);
    setCurrentPage(1);
  };

  const handleSortChange = (event) => {
    setSortOption(event.target.value);
    setCurrentPage(1);
  };

  const clearFilters = () => {
    setSearchTerm("");
    setCategoryFilter("All");
    setStockFilter("All");
    setCurrentPage(1);
  };

  const clearAllControls = () => {
    setSearchTerm("");
    setCategoryFilter("All");
    setStockFilter("All");
    setSortOption("default");
    setCurrentPage(1);
  };

  const filtersActive =
    searchTerm !== "" ||
    categoryFilter !== "All" ||
    stockFilter !== "All";

  const menuItems = [
    "Dashboard",
    "Products",
    "Inventory",
    "Low Stock",
    "Risk Analysis",
    "Reports",
  ];

  return (
    <div className="app-container">

      {/* SIDEBAR */}

      <aside className="sidebar">

        <div className="logo">

          <div className="logo-icon">
            S
          </div>

          <div>
            <h2>
              ShopSphere
            </h2>

            <span>
              DevOps Platform
            </span>
          </div>

        </div>

        <div className="menu-section">

          <p className="menu-title">
            MAIN MENU
          </p>

          {menuItems.map((item) => (

            <button
              key={item}
              className={`menu-item ${
                activeMenu === item
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                setActiveMenu(item)
              }
            >

              <span className="menu-icon">

                {item === "Dashboard" && "▣"}
                {item === "Products" && "◫"}
                {item === "Inventory" && "◈"}
                {item === "Low Stock" && "⚠"}
                {item === "Risk Analysis" && "◉"}
                {item === "Reports" && "▤"}

              </span>

              <span>
                {item}
              </span>

            </button>

          ))}

        </div>

        <div className="menu-section bottom-menu">

          <button className="menu-item">

            <span className="menu-icon">
              ⚙
            </span>

            <span>
              Settings
            </span>

          </button>

          <button className="menu-item">

            <span className="menu-icon">
              ↪
            </span>

            <span>
              Logout
            </span>

          </button>

        </div>

      </aside>

      {/* MAIN CONTENT */}

      <main className="main-content">

        {/* TOPBAR */}

        <header className="topbar">

          <div>

            <h1>
              {activeMenu}
            </h1>

            <p>
              ShopSphere inventory & DevOps management
            </p>

          </div>

          <div className="profile-area">

            <div className="notification">
              🔔
            </div>

            <div className="profile">

              <div className="profile-avatar">
                A
              </div>

              <div>

                <strong>
                  Admin
                </strong>

                <span>
                  Administrator
                </span>

              </div>

            </div>

          </div>

        </header>

        {/* ERROR */}

        {error && (

          <div className="error-box">
            ⚠️ {error}
          </div>

        )}

        {/* DASHBOARD */}

        {activeMenu === "Dashboard" && (

          <>

            {loading ? (

              <div className="loading-box">
                Loading real product data...
              </div>

            ) : (

              <>

                {/* STATS */}

                <section className="stats-grid">

                  <div className="stat-card">

                    <div className="stat-icon blue">
                      ▣
                    </div>

                    <div>

                      <span>
                        Total Products
                      </span>

                      <h2>
                        {totalProducts}
                      </h2>

                      <small>
                        Live database data
                      </small>

                    </div>

                  </div>

                  <div className="stat-card">

                    <div className="stat-icon green">
                      ◈
                    </div>

                    <div>

                      <span>
                        Total Stock
                      </span>

                      <h2>
                        {totalStock}
                      </h2>

                      <small>
                        Units in inventory
                      </small>

                    </div>

                  </div>

                  <div className="stat-card">

                    <div className="stat-icon purple">
                      ₹
                    </div>

                    <div>

                      <span>
                        Inventory Value
                      </span>

                      <h2>
                        {formatCurrency(
                          inventoryValue
                        )}
                      </h2>

                      <small>
                        Current stock value
                      </small>

                    </div>

                  </div>

                  <div className="stat-card">

                    <div className="stat-icon orange">
                      ⚠
                    </div>

                    <div>

                      <span>
                        Medium Risk
                      </span>

                      <h2>
                        {mediumRiskProducts}
                      </h2>

                      <small>
                        Needs monitoring
                      </small>

                    </div>

                  </div>

                </section>

                {/* INVENTORY + HEALTH */}

                <section className="dashboard-grid">

                  <div className="dashboard-card">

                    <div className="card-header">

                      <div>

                        <h3>
                          Inventory Overview
                        </h3>

                        <p>
                          Stock quantity by product
                        </p>

                      </div>

                    </div>

                    <div className="chart">

                      {products.length === 0 ? (

                        <div className="empty-state">
                          No products available
                        </div>

                      ) : (

                        products.map(
                          (product, index) => {

                            const stock =
                              Number(
                                product.stock || 0
                              );

                            const maxStock =
                              Math.max(
                                ...products.map(
                                  (p) =>
                                    Number(
                                      p.stock || 0
                                    )
                                ),
                                1
                              );

                            const height =
                              Math.max(
                                10,
                                (stock /
                                  maxStock) *
                                  180
                              );

                            return (

                              <div
                                className="bar-container"
                                key={
                                  product.id ||
                                  index
                                }
                              >

                                <div
                                  className="bar"
                                  style={{
                                    height:
                                      `${height}px`,
                                  }}
                                  title={`${product.name}: ${stock} units`}
                                />

                                <span className="bar-label">

                                  {product.name
                                    ? product.name.substring(
                                        0,
                                        10
                                      )
                                    : `P${index + 1}`}

                                </span>

                              </div>

                            );

                          }
                        )

                      )}

                    </div>

                  </div>

                  <div className="dashboard-card">

                    <div className="card-header">

                      <div>

                        <h3>
                          Inventory Health
                        </h3>

                        <p>
                          Current stock risk distribution
                        </p>

                      </div>

                    </div>

                    <div className="health-list">

                      {[
                        "Critical",
                        "High",
                        "Medium",
                        "Low",
                      ].map((risk) => {

                        let count = 0;

                        if (risk === "Critical") {

                          count =
                            products.filter(
                              (p) =>
                                Number(
                                  p.stock || 0
                                ) <= 0
                            ).length;

                        }

                        if (risk === "High") {

                          count =
                            products.filter(
                              (p) =>
                                Number(
                                  p.stock || 0
                                ) > 0 &&
                                Number(
                                  p.stock || 0
                                ) <= 5
                            ).length;

                        }

                        if (risk === "Medium") {

                          count =
                            products.filter(
                              (p) =>
                                Number(
                                  p.stock || 0
                                ) > 5 &&
                                Number(
                                  p.stock || 0
                                ) <= 10
                            ).length;

                        }

                        if (risk === "Low") {

                          count =
                            products.filter(
                              (p) =>
                                Number(
                                  p.stock || 0
                                ) > 10
                            ).length;

                        }

                        const percentage =
                          totalProducts > 0
                            ? (count /
                                totalProducts) *
                              100
                            : 0;

                        return (

                          <div
                            className="health-row"
                            key={risk}
                          >

                            <div className="health-info">

                              <span
                                className={`risk-dot ${risk.toLowerCase()}`}
                              />

                              <span>
                                {risk}
                              </span>

                            </div>

                            <div className="health-progress">

                              <div
                                className={`progress-bar ${risk.toLowerCase()}`}
                                style={{
                                  width:
                                    `${percentage}%`,
                                }}
                              />

                            </div>

                            <strong>

                              {percentage.toFixed(
                                1
                              )}

                              %

                            </strong>

                          </div>

                        );

                      })}

                    </div>

                  </div>

                </section>

                {/* RECENT PRODUCTS */}

                <section className="dashboard-card table-card">

                  <div className="card-header">

                    <div>

                      <h3>
                        Recent Products
                      </h3>

                      <p>
                        Live products from ShopSphere database
                      </p>

                    </div>

                    <button
                      className="refresh-button"
                      onClick={fetchProducts}
                    >
                      ↻ Refresh
                    </button>

                  </div>

                  <div className="table-wrapper">

                    <table>

                      <thead>

                        <tr>

                          <th>
                            Product
                          </th>

                          <th>
                            Price
                          </th>

                          <th>
                            Stock
                          </th>

                          <th>
                            Inventory Value
                          </th>

                          <th>
                            Status
                          </th>

                        </tr>

                      </thead>

                      <tbody>

                        {products.map(
                          (product) => {

                            const stock =
                              Number(
                                product.stock || 0
                              );

                            const price =
                              Number(
                                product.price || 0
                              );

                            const value =
                              stock * price;

                            return (

                              <tr
                                key={product.id}
                              >

                                <td>

                                  <strong>
                                    {product.name}
                                  </strong>

                                </td>

                                <td>

                                  {formatCurrency(
                                    price
                                  )}

                                </td>

                                <td>
                                  {stock}
                                </td>

                                <td>

                                  {formatCurrency(
                                    value
                                  )}

                                </td>

                                <td>

                                  <span
                                    className={`status ${getStatusClass(
                                      stock
                                    )}`}
                                  >

                                    {getStatus(
                                      stock
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

            )}

          </>

        )}

        {/* PRODUCTS PAGE */}

        {activeMenu === "Products" && (

          <section className="products-page">

            <div className="products-toolbar">

              <div>

                <h2>
                  Product Management
                </h2>

                <p>
                  Manage products directly from ShopSphere
                </p>

              </div>

              <button
                className="add-product-button"
                onClick={() =>
                  setShowAddForm(
                    !showAddForm
                  )
                }
              >

                + Add Product

              </button>

            </div>

            {/* SEARCH & FILTERS */}

            <div className="dashboard-card">

              <div className="card-header">

                <div>

                  <h3>
                    Search & Filters
                  </h3>

                  <p>
                    Find products quickly
                  </p>

                </div>

                {filtersActive && (

                  <button
                    className="refresh-button"
                    onClick={clearFilters}
                  >
                    ✕ Clear Filters
                  </button>

                )}

              </div>

              <div
                className="product-form"
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "2fr 1fr 1fr 1fr",
                  gap: "15px",
                  alignItems: "end",
                }}
              >

                <div className="form-group">

                  <label>
                    Search Product
                  </label>

                  <input
                    type="text"
                    placeholder="🔍 Search by product name..."
                    value={searchTerm}
                    onChange={handleSearchChange}
                  />

                </div>

                <div className="form-group">

                  <label>
                    Category
                  </label>

                  <select
                    value={categoryFilter}
                    onChange={handleCategoryChange}
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

                </div>

                <div className="form-group">

                  <label>
                    Stock Status
                  </label>

                  <select
                    value={stockFilter}
                    onChange={handleStockFilterChange}
                  >

                    <option value="All">
                      All Status
                    </option>

                    <option value="Healthy">
                      Healthy
                    </option>

                    <option value="Medium">
                      Medium Risk
                    </option>

                    <option value="Critical">
                      Critical
                    </option>

                  </select>

                </div>

                <div className="form-group">

                  <label>
                    Sort By
                  </label>

                  <select
                    value={sortOption}
                    onChange={handleSortChange}
                  >

                    <option value="default">
                      Default
                    </option>

                    <option value="name-asc">
                      Name: A → Z
                    </option>

                    <option value="name-desc">
                      Name: Z → A
                    </option>

                    <option value="price-asc">
                      Price: Low → High
                    </option>

                    <option value="price-desc">
                      Price: High → Low
                    </option>

                    <option value="stock-asc">
                      Stock: Low → High
                    </option>

                    <option value="stock-desc">
                      Stock: High → Low
                    </option>

                  </select>

                </div>

              </div>

            </div>

            {/* ADD PRODUCT FORM */}

            {showAddForm && (

              <div className="add-product-card">

                <h3>
                  Add New Product
                </h3>

                <form
                  onSubmit={addProduct}
                  className="product-form"
                >

                  <div className="form-group">

                    <label>
                      Product Name
                    </label>

                    <input
                      type="text"
                      placeholder="e.g. iPhone 17"
                      value={
                        newProduct.name
                      }
                      onChange={(e) =>
                        setNewProduct({
                          ...newProduct,
                          name: e.target.value,
                        })
                      }
                      required
                    />

                  </div>

                  <div className="form-group">

                    <label>
                      Description
                    </label>

                    <input
                      type="text"
                      placeholder="Product description"
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
                      required
                    />

                  </div>

                  <div className="form-row">

                    <div className="form-group">

                      <label>
                        Price
                      </label>

                      <input
                        type="number"
                        placeholder="79999"
                        min="0"
                        value={
                          newProduct.price
                        }
                        onChange={(e) =>
                          setNewProduct({
                            ...newProduct,
                            price: e.target.value,
                          })
                        }
                        required
                      />

                    </div>

                    <div className="form-group">

                      <label>
                        Stock
                      </label>

                      <input
                        type="number"
                        placeholder="10"
                        min="0"
                        value={
                          newProduct.stock
                        }
                        onChange={(e) =>
                          setNewProduct({
                            ...newProduct,
                            stock: e.target.value,
                          })
                        }
                        required
                      />

                    </div>

                  </div>

                  <div className="form-group">

                    <label>
                      Category
                    </label>

                    <input
                      type="text"
                      placeholder="e.g. Electronics"
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
                      required
                    />

                  </div>

                  <div className="form-actions">

                    <button
                      type="submit"
                      className="save-product-button"
                    >
                      Create Product
                    </button>

                    <button
                      type="button"
                      className="cancel-button"
                      onClick={() =>
                        setShowAddForm(false)
                      }
                    >
                      Cancel
                    </button>

                  </div>

                </form>

              </div>

            )}

            {/* EDIT PRODUCT FORM */}

            {editingProduct && (

              <div className="add-product-card">

                <h3>
                  Edit Product
                </h3>

                <form
                  onSubmit={updateProduct}
                  className="product-form"
                >

                  <div className="form-group">

                    <label>
                      Product Name
                    </label>

                    <input
                      type="text"
                      value={
                        editingProduct.name
                      }
                      onChange={(e) =>
                        setEditingProduct({
                          ...editingProduct,
                          name: e.target.value,
                        })
                      }
                      required
                    />

                  </div>

                  <div className="form-group">

                    <label>
                      Description
                    </label>

                    <input
                      type="text"
                      value={
                        editingProduct.description
                      }
                      onChange={(e) =>
                        setEditingProduct({
                          ...editingProduct,
                          description:
                            e.target.value,
                        })
                      }
                      required
                    />

                  </div>

                  <div className="form-row">

                    <div className="form-group">

                      <label>
                        Price
                      </label>

                      <input
                        type="number"
                        min="0"
                        value={
                          editingProduct.price
                        }
                        onChange={(e) =>
                          setEditingProduct({
                            ...editingProduct,
                            price:
                              e.target.value,
                          })
                        }
                        required
                      />

                    </div>

                    <div className="form-group">

                      <label>
                        Stock
                      </label>

                      <input
                        type="number"
                        min="0"
                        value={
                          editingProduct.stock
                        }
                        onChange={(e) =>
                          setEditingProduct({
                            ...editingProduct,
                            stock:
                              e.target.value,
                          })
                        }
                        required
                      />

                    </div>

                  </div>

                  <div className="form-group">

                    <label>
                      Category
                    </label>

                    <input
                      type="text"
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
                      required
                    />

                  </div>

                  <div className="form-actions">

                    <button
                      type="submit"
                      className="save-product-button"
                    >
                      Update Product
                    </button>

                    <button
                      type="button"
                      className="cancel-button"
                      onClick={() =>
                        setEditingProduct(null)
                      }
                    >
                      Cancel
                    </button>

                  </div>

                </form>

              </div>

            )}

            {/* PRODUCT TABLE */}

            <div className="dashboard-card table-card">

              <div className="card-header">

                <div>

                  <h3>
                    All Products
                  </h3>

                  <p>
                    Showing{" "}
                    {totalFilteredProducts === 0
                      ? 0
                      : startIndex + 1}{" "}
                    -{" "}
                    {Math.min(
                      endIndex,
                      totalFilteredProducts
                    )}{" "}
                    of{" "}
                    {totalFilteredProducts}{" "}
                    filtered /{" "}
                    {products.length} total products
                  </p>

                </div>

                <div
                  style={{
                    display: "flex",
                    gap: "10px",
                  }}
                >

                  {(filtersActive ||
                    sortOption !== "default") && (

                    <button
                      className="refresh-button"
                      onClick={
                        clearAllControls
                      }
                    >
                      ✕ Clear All
                    </button>

                  )}

                  <button
                    className="refresh-button"
                    onClick={fetchProducts}
                  >
                    ↻ Refresh
                  </button>

                </div>

              </div>

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "15px",
                  gap: "15px",
                  flexWrap: "wrap",
                }}
              >

                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                  }}
                >

                  <label
                    style={{
                      fontWeight: "600",
                    }}
                  >
                    Products per page:
                  </label>

                  <select
                    value={productsPerPage}
                    onChange={
                      handleProductsPerPageChange
                    }
                    style={{
                      padding: "8px 12px",
                      borderRadius: "6px",
                      border: "1px solid #ccc",
                    }}
                  >

                    <option value="5">
                      5
                    </option>

                    <option value="10">
                      10
                    </option>

                    <option value="20">
                      20
                    </option>

                  </select>

                </div>

                <div
                  style={{
                    fontWeight: "600",
                  }}
                >
                  Page {safeCurrentPage} of{" "}
                  {totalPages}
                </div>

              </div>

              <div className="table-wrapper">

                <table>

                  <thead>

                    <tr>

                      <th>
                        ID
                      </th>

                      <th>
                        Product
                      </th>

                      <th>
                        Description
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
                        Action
                      </th>

                    </tr>

                  </thead>

                  <tbody>

                    {paginatedProducts.length === 0 ? (

                      <tr>

                        <td
                          colSpan="8"
                          className="empty-table"
                        >
                          No products match your search or filters.
                        </td>

                      </tr>

                    ) : (

                      paginatedProducts.map(
                        (product) => {

                          const stock =
                            Number(
                              product.stock ||
                                0
                            );

                          return (

                            <tr
                              key={
                                product.id
                              }
                            >

                              <td>
                                #{product.id}
                              </td>

                              <td>

                                <strong>
                                  {
                                    product.name
                                  }
                                </strong>

                              </td>

                              <td>

                                {
                                  product.description ||
                                  "-"
                                }

                              </td>

                              <td>
                                {product.category ||
                                  "General"}
                              </td>

                              <td>

                                {formatCurrency(
                                  Number(
                                    product.price ||
                                      0
                                  )
                                )}

                              </td>

                              <td>
                                {stock}
                              </td>

                              <td>

                                <span
                                  className={`status ${getStatusClass(
                                    stock
                                  )}`}
                                >

                                  {getStatus(
                                    stock
                                  )}

                                </span>

                              </td>

                              <td>

                                <button
                                  className="refresh-button"
                                  onClick={() =>
                                    openProductDetails(product)
                                  }
                                >
                                  View
                                </button>

                                <button
                                  className="edit-button"
                                  onClick={() =>
                                    setEditingProduct({
                                      id: product.id,
                                      name:
                                        product.name ||
                                        "",
                                      description:
                                        product.description ||
                                        "",
                                      price:
                                        product.price ||
                                        "",
                                      stock:
                                        product.stock ||
                                        "",
                                      category:
                                        product.category ||
                                        "General",
                                    })
                                  }
                                >
                                  Edit
                                </button>

                                <button
                                  className="delete-button"
                                  onClick={() =>
                                    deleteProduct(
                                      product.id
                                    )
                                  }
                                >
                                  Delete
                                </button>

                              </td>

                            </tr>

                          );

                        }
                      )

                    )}

                  </tbody>

                </table>

              </div>

              {/* PAGINATION CONTROLS */}

              {totalPages > 1 && (

                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    gap: "8px",
                    marginTop: "20px",
                    flexWrap: "wrap",
                  }}
                >

                  <button
                    className="refresh-button"
                    onClick={
                      goToPreviousPage
                    }
                    disabled={
                      safeCurrentPage === 1
                    }
                  >
                    ← Previous
                  </button>

                  {Array.from(
                    {
                      length: totalPages,
                    },
                    (_, index) =>
                      index + 1
                  ).map((page) => (

                    <button
                      key={page}
                      className={
                        page ===
                        safeCurrentPage
                          ? "add-product-button"
                          : "refresh-button"
                      }
                      onClick={() =>
                        goToPage(page)
                      }
                    >
                      {page}
                    </button>

                  ))}

                  <button
                    className="refresh-button"
                    onClick={
                      goToNextPage
                    }
                    disabled={
                      safeCurrentPage ===
                      totalPages
                    }
                  >
                    Next →
                  </button>

                </div>

              )}

            </div>

          </section>

        )}

        {/* PRODUCT DETAILS MODAL */}

        {viewingProduct && (

          <div
            style={{
              position: "fixed",
              inset: 0,
              background: "rgba(0, 0, 0, 0.55)",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              zIndex: 1000,
              padding: "20px",
            }}
            onClick={closeProductDetails}
          >

            <div
              style={{
                width: "100%",
                maxWidth: "600px",
                background: "#ffffff",
                borderRadius: "14px",
                padding: "25px",
                boxShadow: "0 20px 50px rgba(0,0,0,0.25)",
              }}
              onClick={(event) =>
                event.stopPropagation()
              }
            >

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "20px",
                }}
              >

                <div>
                  <h2 style={{ margin: 0 }}>
                    Product Details
                  </h2>

                  <p
                    style={{
                      margin: "6px 0 0",
                      color: "#666",
                    }}
                  >
                    Complete product information
                  </p>
                </div>

                <button
                  className="cancel-button"
                  onClick={closeProductDetails}
                >
                  ✕ Close
                </button>

              </div>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "repeat(2, minmax(0, 1fr))",
                  gap: "15px",
                }}
              >

                <div className="stat-card">
                  <span>Product ID</span>
                  <h3>#{viewingProduct.id}</h3>
                </div>

                <div className="stat-card">
                  <span>Category</span>
                  <h3>
                    {viewingProduct.category ||
                      "General"}
                  </h3>
                </div>

                <div className="stat-card">
                  <span>Product Name</span>
                  <h3>{viewingProduct.name}</h3>
                </div>

                <div className="stat-card">
                  <span>Price</span>
                  <h3>
                    {formatCurrency(
                      Number(viewingProduct.price || 0)
                    )}
                  </h3>
                </div>

                <div className="stat-card">
                  <span>Stock</span>
                  <h3>
                    {Number(viewingProduct.stock || 0)} units
                  </h3>
                </div>

                <div className="stat-card">
                  <span>Status</span>
                  <h3>
                    <span
                      className={`status ${getStatusClass(
                        Number(viewingProduct.stock || 0)
                      )}`}
                    >
                      {getStatus(
                        Number(viewingProduct.stock || 0)
                      )}
                    </span>
                  </h3>
                </div>

              </div>

              <div
                style={{
                  marginTop: "15px",
                  padding: "15px",
                  borderRadius: "10px",
                  background: "#f7f7f7",
                }}
              >
                <strong>Description</strong>

                <p
                  style={{
                    margin: "8px 0 0",
                    color: "#555",
                  }}
                >
                  {viewingProduct.description ||
                    "No description available."}
                </p>
              </div>

            </div>

          </div>

        )}

        {/* OTHER MODULES */}

        {[
          "Inventory",
          "Low Stock",
          "Risk Analysis",
          "Reports",
        ].includes(activeMenu) && (

          <section className="module-placeholder">

            <div className="placeholder-icon">
              🚀
            </div>

            <h2>
              {activeMenu}
            </h2>

            <p>
              This ShopSphere module will be
              connected to the existing FastAPI
              analytics APIs in upcoming steps.
            </p>

            <button
              onClick={() =>
                setActiveMenu("Dashboard")
              }
              className="back-button"
            >
              ← Back to Dashboard
            </button>

          </section>

        )}

      </main>

    </div>
  );
}

export default App;