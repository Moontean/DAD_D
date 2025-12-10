import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { ShoppingCart, User, LogOut, Star, Mail, Search } from 'lucide-react';
import './App.css';

const API_URL = 'http://localhost:8000';

// Main App Component
function App() {
    const [user, setUser] = useState(null);
    const [cart, setCart] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');

    const handleLogout = () => setUser(null);

    const addToCart = async (productId, quantity = 1) => {
        if (!user) return false;
        try {
            const resp = await fetch(`${API_URL}/cart/${user.user_id}/add`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product_id: productId, quantity })
            });
            const data = await resp.json();
            if (resp.ok) {
                setCart(data.cart || []);
                return true;
            }
        } catch (e) {
            console.error('Add to cart error:', e);
        }
        return false;
    };

    return (
        <Router>
            <Navbar user={user} cartCount={cart.length} onLogout={handleLogout} searchQuery={searchQuery} setSearchQuery={setSearchQuery} />
            <main className="container">
                <Routes>
                    <Route path="/" element={<Home onAddToCart={addToCart} user={user} searchQuery={searchQuery} />} />
                    <Route path="/cart" element={<CartPage user={user} setCart={setCart} />} />
                    <Route path="/orders" element={<OrdersPage user={user} />} />
                    <Route path="/login" element={<LoginPage setUser={setUser} />} />
                    <Route path="/register" element={<RegisterPage />} />
                </Routes>
            </main>
        </Router>
    );
}

// Navbar Component
function Navbar({ user, onLogout, cartCount, searchQuery, setSearchQuery }) {
    return (
        <nav className="navbar">
            <div className="container nav-content">
                <Link to="/" className="logo">ElectroShop</Link>
                <div className="tabs">
                    <Link to="/" className="tab-link">Shop</Link>
                    <Link to="/" className="tab-link">Inside the Tin</Link>
                    <Link to="/" className="tab-link">Beyond the Tin</Link>
                </div>
                <div className="nav-links">
                    <div className="search">
                        <Search size={18} />
                        <input placeholder="Search" value={searchQuery} onChange={(e)=> setSearchQuery(e.target.value)} />
                    </div>
                    {user && <Link to="/orders" className="nav-link">Orders</Link>}
                    {user ? (
                        <>
                            <Link to="/cart" className="nav-link">
                                <ShoppingCart size={20} />
                                <span>Cart ({cartCount})</span>
                            </Link>
                            <div className="user-info">
                                <User size={20} />
                                <span>{user.username}</span>
                            </div>
                            <button onClick={onLogout} className="nav-link-btn">
                                <LogOut size={20} />
                            </button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="btn-secondary">Login</Link>
                            <Link to="/register" className="btn-primary">Register</Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
}

// Product List Component
function Home({ onAddToCart, user, searchQuery }) {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeProduct, setActiveProduct] = useState(null);
    const [reviews, setReviews] = useState([]);
    const [reviewText, setReviewText] = useState('');
    const [reviewError, setReviewError] = useState('');
    const [reviewSuccess, setReviewSuccess] = useState('');
    
    useEffect(() => {
        fetch(`${API_URL}/products`)
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(data => {
                setProducts(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Error fetching products:", err);
                setLoading(false);
            });
    }, []);

    const openReview = async (product) => {
        setActiveProduct(product);
        setReviewText('');
        setReviewError('');
        setReviewSuccess('');
        try {
            const resp = await fetch(`${API_URL}/reviews/${product.id}`);
            const data = await resp.json();
            setReviews(Array.isArray(data) ? data : []);
        } catch (err) {
            console.error('Reviews load error:', err);
            setReviews([]);
        }
    };

    const submitReview = async () => {
        if (!user) { setReviewError('Войдите, чтобы оставить комментарий'); return; }
        if (!reviewText.trim()) { setReviewError('Комментарий пустой'); return; }
        setReviewError('');
        try {
            const resp = await fetch(`${API_URL}/reviews`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product_id: activeProduct.id, comment: reviewText })
            });
            const data = await resp.json();
            if (!resp.ok) {
                setReviewError(data.detail || 'Не удалось отправить комментарий');
                return;
            }
            setReviewSuccess('Комментарий отправлен');
            setReviews(prev => [...prev, { comment: reviewText }]);
            setReviewText('');
        } catch {
            setReviewError('Ошибка сети');
        }
    };

    if (loading) return <div className="page-title">Loading products...</div>;
    if (products.length === 0) return <div className="page-title">No products found. Check console for errors.</div>;

    return (
        <div>
            <h1 className="page-title">Featured Products</h1>
                        <div className="product-grid">
                                {products
                                    .filter(p => !searchQuery || p.name.toLowerCase().includes(searchQuery.toLowerCase()))
                                    .map(product => (
                    <div key={product.id} className="product-card">
                        <div className="product-image">
                            <img src={`/images/product-${product.id}.jpg`} alt={product.name} onError={(e) => {
                                e.target.style.display = 'none';
                                e.target.nextSibling.style.display = 'block';
                            }} />
                            <div className="placeholder-image" style={{display: 'none'}}>
                                <span>📱</span>
                            </div>
                        </div>
                        <div className="product-info">
                            <h3 className="product-name">{product.name}</h3>
                            <div className="price-container">
                                <span className="old-price">{(product.price * 1.25).toFixed(0)} лей</span>
                                <span className="new-price">{product.price.toFixed(0)} лей</span>
                            </div>
                            <div className="product-actions">
                                <button className="add-to-cart-btn" onClick={async () => {
                                    if (!user) {
                                        alert('Please login to add items to cart');
                                        return;
                                    }
                                    const ok = await onAddToCart(product.id, 1);
                                    if (ok) {
                                        // simple feedback
                                    }
                                }}>
                                    <span className="cart-icon">🛒</span>
                                    <span>Add to Cart</span>
                                </button>
                                <button className="review-btn" title="Оставить комментарий" onClick={() => openReview(product)}>
                                    <Mail size={16} />
                                    <span>Comment</span>
                                </button>
                            </div>
                        </div>
                    </div>
                    ))}
            </div>

            {activeProduct && (
                <div className="modal-backdrop" onClick={() => setActiveProduct(null)}>
                    <div className="modal" onClick={e => e.stopPropagation()}>
                        <h3>Комментарии: {activeProduct.name}</h3>
                        <ul className="reviews-list">
                            {reviews.length === 0 ? (
                                <li>Пока нет комментариев</li>
                            ) : reviews.map((r, i) => (
                                <li key={i}>• {r.comment}</li>
                            ))}
                        </ul>
                        {reviewError && <p className="error-msg" style={{marginTop:'.5rem'}}>{reviewError}</p>}
                        {reviewSuccess && <p className="success-msg" style={{marginTop:'.5rem'}}>{reviewSuccess}</p>}
                        <textarea
                            rows={3}
                            style={{width:'100%',marginTop:'.75rem',padding:'10px',borderRadius:'8px',border:'1px solid var(--border-color)'}}
                            placeholder="Ваш комментарий"
                            value={reviewText}
                            onChange={e => setReviewText(e.target.value)}
                        />
                        <div style={{display:'flex',gap:'.5rem',justifyContent:'flex-end',marginTop:'.75rem'}}>
                            <button className="btn-secondary" onClick={() => setActiveProduct(null)}>Закрыть</button>
                            <button className="btn-primary" onClick={submitReview}>Отправить</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

// Register Page Component
function RegisterPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();
        setError('');
        setMessage('');
        try {
            const response = await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'Registration failed');
            }
            setMessage(data.message || 'Registration successful! Redirecting to login...');
            setTimeout(() => navigate('/login'), 2000);
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="login-container">
            <form onSubmit={handleRegister} className="login-form">
                <h2>Register</h2>
                {error && <p className="error-msg">{error}</p>}
                {message && <p className="success-msg">{message}</p>}
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <button type="submit" className="btn-primary">Register</button>
            </form>
        </div>
    );
}

// Login Page Component
function LoginPage({ setUser }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
            if (!response.ok) throw new Error('Login failed');
            const data = await response.json();
            setUser(data);
            navigate('/');
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="login-container">
            <form onSubmit={handleLogin} className="login-form">
                <h2>Login</h2>
                {error && <p className="error-msg">{error}</p>}
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <button type="submit" className="btn-primary">Login</button>
            </form>
        </div>
    );
}

export default App;
// Orders Page Component
function OrdersPage({ user }) {
    const [orders, setOrders] = useState([]);
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        if (!user) { navigate('/login'); return; }
        // fetch orders
        fetch(`${API_URL}/orders/${user.user_id}`)
            .then(res => res.json())
            .then(data => { setOrders(Array.isArray(data)? data:[]); setLoading(false); })
            .catch(() => { setError('Failed to load orders'); setLoading(false); });
        // fetch products for name/price lookup
        fetch(`${API_URL}/products`).then(res=>res.json()).then(setProducts).catch(()=>{});
    }, [user]);

    if (loading) return <div className="page-title">Loading orders...</div>;
    return (
        <div className="cart-container">
            <h1 className="page-title">Your Orders</h1>
            {error && <p className="error-msg">{error}</p>}
            <div className="cart-list">
                {orders.length === 0 ? (
                    <p>No orders yet.</p>
                ) : orders.map((o, i) => (
                    <div className="cart-item" key={i}>
                        <div style={{flex:1}}>
                            <div>Order: {o.order_id} — {o.status}</div>
                            <ul style={{marginTop:'.5rem'}}>
                                {(Array.isArray(o.items)? o.items: []).map((it, idx) => {
                                    const p = products.find(pp => pp.id === it.product_id);
                                    const name = p ? p.name : `Product #${it.product_id}`;
                                    const price = p ? p.price : 0;
                                    return (
                                        <li key={idx}>{name} — {price.toFixed(2)} лей × {it.quantity}</li>
                                    );
                                })}
                            </ul>
                        </div>
                        <div>Total: {Number(o.total_amount).toFixed(2)} лей</div>
                    </div>
                ))}
            </div>
        </div>
    );
}

// Cart Page Component
function CartPage({ user, setCart }) {
    const [items, setItems] = useState([]);
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [message, setMessage] = useState('');
    const [showModal, setShowModal] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        if (!user) {
            navigate('/login');
            return;
        }
        // Load cart
        fetch(`${API_URL}/cart/${user.user_id}`)
            .then(res => res.json())
            .then(data => {
                console.log('Cart items loaded:', data);
                setItems(data || []);
                setLoading(false);
            })
            .catch(err => {
                setError('Failed to load cart');
                setLoading(false);
            });
        // Load products for item details and prices
        fetch(`${API_URL}/products`)
            .then(res => res.json())
            .then(data => {
                setProducts(data || []);
            })
            .catch(() => {});
    }, [user]);

    // Helper: find product info
    const getProduct = (id) => products.find(p => p.id === id);
    const total = items.reduce((sum, it) => {
        const p = getProduct(it.product_id);
        const price = p ? p.price : 0;
        return sum + it.quantity * price;
    }, 0);

    const handleCheckout = async () => {
        setError('');
        setMessage('');
        try {
            const resp = await fetch(`${API_URL}/orders`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: user.user_id,
                    items: items,
                    total_amount: total
                })
            });
            const data = await resp.json();
            if (resp.ok) {
                setMessage(`Order confirmed! ID: ${data.order_id}`);
                setShowModal(true);
                // clear cart in backend and local state, then redirect
                try { await fetch(`${API_URL}/cart/${user.user_id}/clear`, { method: 'DELETE' }); } catch {}
                setCart([]);
                setTimeout(() => {
                    setShowModal(false);
                    navigate('/');
                }, 1500);
            } else {
                setError(data.detail || 'Checkout failed');
            }
        } catch (e) {
            setError('Checkout failed');
        }
    };

    if (!user) return null;
    if (loading) return <div className="page-title">Loading cart...</div>;

    return (
        <div className="cart-container">
            <h1 className="page-title">Your Cart</h1>
            {error && <p className="error-msg">{error}</p>}
            {message && <p className="success-msg">{message}</p>}
            {showModal && (
                <div className="modal-backdrop">
                    <div className="modal">
                        <h3>Покупка завершена</h3>
                        <p>Спасибо за заказ! Возвращаем на главную...</p>
                    </div>
                </div>
            )}
            <div className="cart-list">
                {items.length === 0 ? (
                    <p>No items in cart.</p>
                ) : (
                    items.map((it, idx) => (
                        <div key={idx} className="cart-item">
                            <div>
                                {(() => {
                                    const p = getProduct(it.product_id);
                                    if (!p) return `Product #${it.product_id}`;
                                    return `${p.name} — ${(p.price).toFixed(2)} лей`;
                                })()}
                            </div>
                            <div>Qty: {it.quantity}</div>
                        </div>
                    ))
                )}
            </div>
            <div className="cart-summary">
                <div>Total: {total.toFixed(2)} лей</div>
                <button className="btn-primary" onClick={handleCheckout}>Checkout</button>
            </div>
        </div>
    );
}
