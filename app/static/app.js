// FlashCart Quick Commerce Single Page Application Engine

const state = {
  products: [],
  totalProducts: 0,
  page: 1,
  limit: 24,
  totalPages: 1,
  currentCategory: "all",
  currentSubcategory: "all",
  searchQuery: "",
  sortBy: "popular",
  inStockOnly: false,
  minPrice: null,
  maxPrice: null,
  
  cartItems: [],
  cartMap: {}, // productId -> quantity
  cartBill: {},
  currentTip: 0,
  couponCode: "",

  wishlistIds: new Set(),
  
  walletBalance: 650.0,
  walletTransactions: [],
  
  user: null,
  addresses: [],
  selectedAddressId: null,
  
  activeOrder: null,
  trackingTimer: null
};

// Web Audio API Sound Effects
const audioCtx = window.AudioContext ? new AudioContext() : null;
function playSound(type) {
  if (!audioCtx) return;
  try {
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    
    if (type === 'pop') {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(450, audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(800, audioCtx.currentTime + 0.08);
      gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
      gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.08);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.08);
    } else if (type === 'chime') {
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(523.25, audioCtx.currentTime); // C5
      osc.frequency.setValueAtTime(659.25, audioCtx.currentTime + 0.1); // E5
      osc.frequency.setValueAtTime(783.99, audioCtx.currentTime + 0.2); // G5
      gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
      gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.35);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.35);
    }
  } catch (e) {
    // audio failure silent
  }
}

// Toast Notifications
function showToast(message, type = "success") {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  const bgColor = type === "error" ? "bg-rose-600" : "bg-slate-900";
  toast.className = `${bgColor} text-white px-4 py-3 rounded-2xl shadow-xl text-xs font-bold flex items-center gap-2 pointer-events-auto toast-slide transition-all`;
  
  const icon = type === "error" ? "alert-circle" : "check-circle-2";
  toast.innerHTML = `<i data-lucide="${icon}" class="w-4 h-4 text-emerald-400"></i><span>${message}</span>`;
  container.appendChild(toast);
  lucide.createIcons();
  
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ================= INITIALIZATION =================
// NOTE: The app no longer starts automatically on DOMContentLoaded.
// It now waits behind the Firebase login/sign-up gate (see auth.js), which
// calls window.startFlashCartApp() exactly once after a successful sign-in.
window.startFlashCartApp = async function startFlashCartApp() {
  await loadQcStatus();
  await loadUserProfile();
  await loadCategories();
  await loadWishlist();
  await loadCart();
  await loadWallet();
  await loadProducts();

  setupSearchListener();
  lucide.createIcons();
};

// ================= DATA FETCHING =================
async function loadCategories() {
  try {
    const res = await fetch("/api/categories");
    const data = await res.json();
    state.categories = data;
    renderCategoryCapsules();
  } catch (err) {
    console.error("Failed to load categories", err);
  }
}

async function loadProducts() {
  const grid = document.getElementById("productsGrid");
  grid.innerHTML = `
    <div class="col-span-full py-16 text-center text-slate-600 text-xs font-bold flex items-center justify-center gap-2">
      <i data-lucide="loader-2" class="w-5 h-5 animate-spin text-brand-green"></i> Loading 1,000+ catalog items...
    </div>
  `;
  lucide.createIcons();

  const params = new URLSearchParams({
    page: state.page,
    limit: state.limit,
    category: state.currentCategory,
    subcategory: state.currentSubcategory,
    search: state.searchQuery,
    sort_by: state.sortBy,
    in_stock_only: state.inStockOnly ? "true" : "false"
  });
  if (state.minPrice !== null) params.set("min_price", state.minPrice);
  if (state.maxPrice !== null) params.set("max_price", state.maxPrice);

  try {
    const res = await fetch(`/api/products?${params.toString()}`);
    const data = await res.json();
    state.products = data.items;
    state.totalProducts = data.total;
    state.totalPages = data.total_pages;

    renderProductsGrid();
    renderPagination();
    updateCategoryHeaderInfo();
  } catch (err) {
    console.error("Failed to load products", err);
  }
}

async function loadCart() {
  try {
    const params = new URLSearchParams();
    if (state.couponCode) params.set("coupon", state.couponCode);
    if (state.currentTip) params.set("tip", state.currentTip);

    const res = await fetch(`/api/cart?${params.toString()}`);
    const data = await res.json();
    state.cartItems = data.items;
    state.cartBill = data.bill;

    // update cart map
    state.cartMap = {};
    for (const item of data.items) {
      state.cartMap[item.id] = item.quantity;
    }

    updateCartUI();
  } catch (err) {
    console.error("Failed to load cart", err);
  }
}

async function loadWishlist() {
  try {
    const res = await fetch("/api/wishlist");
    const data = await res.json();
    state.wishlistIds = new Set(data.items.map(i => i.id));
    updateWishlistBadge();
    renderWishlistDrawerItems(data.items);
  } catch (err) {
    console.error("Failed to load wishlist", err);
  }
}

async function loadWallet() {
  try {
    const res = await fetch("/api/wallet");
    const data = await res.json();
    state.walletBalance = data.balance;
    state.walletTransactions = data.transactions;
    updateWalletUI();
  } catch (err) {
    console.error("Failed to load wallet", err);
  }
}

async function loadUserProfile() {
  try {
    const res = await fetch("/api/user/profile");
    const data = await res.json();
    state.user = data.user;
    state.addresses = data.addresses;
    
    // Select default address
    const def = data.addresses.find(a => a.is_default) || data.addresses[0];
    if (def) {
      state.selectedAddressId = def.id;
      document.getElementById("headerAddressTag").innerText = def.tag;
      document.getElementById("headerAddressLine").innerText = `${def.address_line}, ${def.city}`;
      document.getElementById("cartDeliveryTag").innerText = def.tag;
    }
    
    if (data.user) {
      document.getElementById("navUserName").innerText = data.user.name.split(" ")[0];
      const initials = data.user.name.split(" ").map(n => n[0]).join("").slice(0, 2);
      document.getElementById("navUserAvatar").innerText = initials;
      document.getElementById("profileNameInput").value = data.user.name;
      document.getElementById("profilePhoneInput").value = data.user.phone;
      document.getElementById("profileEmailInput").value = data.user.email || "";
    }
    
    renderAddressesList();
  } catch (err) {
    console.error("Failed to load user profile", err);
  }
}

// ================= RENDER FUNCTIONS =================

function renderCategoryCapsules() {
  const container = document.getElementById("categoryCapsulesContainer");
  const isAll = state.currentCategory === "all";
  
  let html = `
    <button onclick="selectCategory('all')" class="shrink-0 px-3.5 py-1.5 rounded-full text-xs font-bold transition flex items-center gap-1.5 ${isAll ? 'bg-brand-green text-white shadow-xs' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}">
      <i data-lucide="layout-grid" class="w-3.5 h-3.5"></i>
      <span>All Categories</span>
    </button>
  `;

  const categoryIcons = {
    "Fresh Fruits & Vegetables": "apple",
    "Dairy, Bread & Eggs": "milk",
    "Snacks & Munchies": "cookie",
    "Instant & Frozen Food": "flame",
    "Cold Drinks & Juices": "cup-soda",
    "Bakery & Biscuits": "cake-slice",
    "Tea, Coffee & Beverages": "coffee",
    "Atta, Rice & Dals": "wheat",
    "Masalas & Dry Fruits": "sparkles",
    "Cleaning & Household": "spray-can",
    "Personal Care": "smile",
    "Baby Care": "baby",
    "Pet Supplies": "dog",
    "Pharma & Wellness": "cross"
  };

  for (const cat of state.categories) {
    const isSelected = state.currentCategory === cat.name;
    const iconName = categoryIcons[cat.name] || "shopping-bag";
    html += `
      <button onclick="selectCategory('${cat.name.replace(/'/g, "\\'")}')" class="shrink-0 px-3.5 py-1.5 rounded-full text-xs font-bold transition flex items-center gap-1.5 ${isSelected ? 'bg-brand-green text-white shadow-xs' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}">
        <i data-lucide="${iconName}" class="w-3.5 h-3.5"></i>
        <span>${cat.name}</span>
        <span class="text-[10px] opacity-75 font-semibold">(${cat.total_items})</span>
      </button>
    `;
  }
  container.innerHTML = html;
  lucide.createIcons();
}

function updateCategoryHeaderInfo() {
  const title = document.getElementById("currentCategoryTitle");
  const count = document.getElementById("totalProductsCount");
  
  title.innerText = state.currentCategory === "all" ? "All Products" : state.currentCategory;
  count.innerText = `${state.totalProducts.toLocaleString()} items`;

  // Render subcategory pills
  const subContainer = document.getElementById("subcategoryPills");
  if (state.currentCategory === "all") {
    subContainer.innerHTML = "";
    return;
  }

  const catObj = state.categories.find(c => c.name === state.currentCategory);
  if (!catObj) return;

  const isAllSub = state.currentSubcategory === "all";
  let html = `
    <button onclick="selectSubcategory('all')" class="px-2.5 py-1 rounded-lg text-[11px] font-extrabold transition ${isAllSub ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}">
      All
    </button>
  `;

  for (const sub of catObj.subcategories) {
    const isSelected = state.currentSubcategory === sub.name;
    html += `
      <button onclick="selectSubcategory('${sub.name.replace(/'/g, "\\'")}')" class="px-2.5 py-1 rounded-lg text-[11px] font-bold transition ${isSelected ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}">
        ${sub.name} <span class="opacity-60 text-[10px]">(${sub.count})</span>
      </button>
    `;
  }
  subContainer.innerHTML = html;
}

function renderProductsGrid() {
  const grid = document.getElementById("productsGrid");
  const empty = document.getElementById("emptyState");

  if (!state.products || state.products.length === 0) {
    grid.innerHTML = "";
    empty.classList.remove("hidden");
    return;
  }

  empty.classList.add("hidden");

  let html = "";
  for (const p of state.products) {
    const inCartQty = state.cartMap[p.id] || 0;
    const isWishlisted = state.wishlistIds.has(p.id);

    html += `
      <div class="product-card bg-white rounded-2xl border border-slate-200/80 p-3 sm:p-3.5 flex flex-col justify-between relative group">
        
        <!-- Top Tags: Discount & QuickCommerce Platform SLA -->
        <div class="flex items-center justify-between gap-1 mb-2">
          <div class="flex items-center gap-1 flex-wrap">
            ${p.discount_pct > 0 
              ? `<span class="bg-amber-100 text-amber-900 font-extrabold text-[10px] px-1.5 py-0.5 rounded-md">${p.discount_pct}% OFF</span>`
              : ''
            }
            ${p.badge ? `<span class="bg-purple-50 border border-purple-200 text-purple-800 font-black text-[9px] px-1.5 py-0.5 rounded-md">${p.badge}</span>` : ''}
          </div>
          
          <button onclick="toggleWishlist(${p.id})" class="p-1 rounded-full hover:bg-rose-50 text-slate-600 hover:text-rose-500 transition" title="Save to Wishlist">
            <i data-lucide="heart" class="w-4 h-4 ${isWishlisted ? 'fill-rose-500 text-rose-500' : ''}"></i>
          </button>
        </div>

        <!-- Product Image -->
        <div class="relative w-full aspect-square bg-slate-50 rounded-xl overflow-hidden mb-2.5 cursor-pointer flex items-center justify-center" onclick="openProductQuickView(${p.id})">
          <img 
            src="${p.image_url}" 
            alt="${p.name}" 
            class="w-full h-full object-cover group-hover:scale-105 transition duration-300"
            loading="lazy"
            onerror="this.src='https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=400&q=80'"
          >
          <span class="absolute bottom-1.5 left-1.5 bg-slate-900/80 backdrop-blur-xs text-white text-[9px] font-black px-1.5 py-0.5 rounded flex items-center gap-1">
            <i data-lucide="clock" class="w-2.5 h-2.5 text-amber-400"></i> ${p.delivery_eta}
          </span>
        </div>

        <!-- Info -->
        <div class="flex-1 flex flex-col justify-between">
          <div>
            <div class="text-[10px] font-bold text-slate-600 uppercase tracking-wider">${p.brand || 'Quick Fresh'}</div>
            <h4 class="text-xs font-bold text-slate-900 line-clamp-2 leading-tight mt-0.5 cursor-pointer hover:text-brand-green" onclick="openProductQuickView(${p.id})">
              ${p.name}
            </h4>
            <div class="text-[11px] font-semibold text-slate-600 mt-1">${p.unit}</div>
          </div>

          <!-- Price & Action Button -->
          <div class="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between gap-1">
            <div>
              <div class="text-sm font-black text-slate-900">₹${p.price.toFixed(2)}</div>
              ${p.mrp > p.price 
                ? `<div class="text-[10px] text-slate-600 line-through">₹${p.mrp.toFixed(2)}</div>` 
                : ''
              }
            </div>

            <!-- Add to Cart / Stepper Control -->
            <div id="product-action-${p.id}">
              ${renderCartButton(p.id, inCartQty, p.in_stock)}
            </div>
          </div>
        </div>

      </div>
    `;
  }
  grid.innerHTML = html;
  lucide.createIcons();
}

function renderCartButton(productId, qty, inStock) {
  if (!inStock) {
    return `<span class="text-[10px] font-bold text-slate-600 bg-slate-100 px-2 py-1 rounded-lg">Out of stock</span>`;
  }

  if (qty > 0) {
    return `
      <div class="flex items-center rounded-xl bg-brand-green text-white font-extrabold text-xs shadow-xs">
        <button onclick="updateCartQuantity(${productId}, ${qty - 1})" class="px-2 py-1 hover:bg-emerald-700 rounded-l-xl transition">
          -
        </button>
        <span class="px-2 py-1 text-xs font-black min-w-[20px] text-center">${qty}</span>
        <button onclick="updateCartQuantity(${productId}, ${qty + 1})" class="px-2 py-1 hover:bg-emerald-700 rounded-r-xl transition">
          +
        </button>
      </div>
    `;
  } else {
    return `
      <button onclick="addToCart(${productId})" class="px-3 py-1.5 rounded-xl border-2 border-brand-green text-brand-green hover:bg-brand-green hover:text-white font-black text-xs transition transform active:scale-95 flex items-center gap-1">
        <span>ADD</span>
      </button>
    `;
  }
}

function renderPagination() {
  const container = document.getElementById("paginationContainer");
  if (state.totalPages <= 1) {
    container.innerHTML = "";
    return;
  }

  let html = `
    <button onclick="goToPage(${state.page - 1})" ${state.page <= 1 ? 'disabled class="opacity-40 cursor-not-allowed"' : ''} class="px-3 py-2 rounded-xl bg-white border border-slate-200 text-xs font-bold text-slate-700 hover:bg-slate-100 transition flex items-center gap-1">
      <i data-lucide="chevron-left" class="w-4 h-4"></i> Prev
    </button>
    <div class="flex items-center gap-1 px-3 text-xs font-bold text-slate-700">
      Page <span class="text-brand-green font-extrabold mx-1">${state.page}</span> of ${state.totalPages}
    </div>
    <button onclick="goToPage(${state.page + 1})" ${state.page >= state.totalPages ? 'disabled class="opacity-40 cursor-not-allowed"' : ''} class="px-3 py-2 rounded-xl bg-white border border-slate-200 text-xs font-bold text-slate-700 hover:bg-slate-100 transition flex items-center gap-1">
      Next <i data-lucide="chevron-right" class="w-4 h-4"></i>
    </button>
  `;
  container.innerHTML = html;
  lucide.createIcons();
}

function updateCartUI() {
  const bill = state.cartBill || {};
  const totalCount = bill.item_count || 0;
  const finalAmount = bill.final_amount || 0;

  // Header Cart Pill
  const countBadge = document.getElementById("cartCountBadge");
  const itemLabel = document.getElementById("cartItemLabel");
  const totalLabel = document.getElementById("cartTotalLabel");
  
  if (totalCount > 0) {
    countBadge.classList.remove("hidden");
    countBadge.innerText = totalCount;
    itemLabel.innerText = `${totalCount} item${totalCount > 1 ? 's' : ''}`;
    totalLabel.innerText = `₹${finalAmount.toFixed(2)}`;
  } else {
    countBadge.classList.add("hidden");
    itemLabel.innerText = "0 items";
    totalLabel.innerText = "₹0.00";
  }

  // Floating Cart Bar (Mobile)
  const floatingBar = document.getElementById("floatingCartBar");
  if (totalCount > 0) {
    floatingBar.classList.remove("hidden");
    document.getElementById("floatingCartCount").innerText = `${totalCount} Items in Bag`;
    document.getElementById("floatingCartTotal").innerText = `₹${finalAmount.toFixed(2)}`;
  } else {
    floatingBar.classList.add("hidden");
  }

  // Drawer UI
  document.getElementById("drawerCartCountBadge").innerText = `${totalCount} items`;
  
  const freeDeliveryText = document.getElementById("freeDeliveryText");
  if (bill.free_delivery_needed > 0) {
    freeDeliveryText.innerHTML = `Add <strong>₹${bill.free_delivery_needed.toFixed(2)}</strong> more for <strong>FREE Delivery!</strong>`;
  } else if (totalCount > 0) {
    freeDeliveryText.innerHTML = `🎉 Congratulations! You have unlocked <strong>FREE Delivery!</strong>`;
  } else {
    freeDeliveryText.innerText = "Free Delivery on orders above ₹199!";
  }

  // Items List
  const itemsContainer = document.getElementById("cartItemsList");
  const emptyState = document.getElementById("cartEmptyState");
  const cartFooter = document.getElementById("cartFooter");

  if (totalCount === 0) {
    itemsContainer.innerHTML = "";
    emptyState.classList.remove("hidden");
    cartFooter.classList.add("hidden");
  } else {
    emptyState.classList.add("hidden");
    cartFooter.classList.remove("hidden");

    let itemsHtml = "";
    for (const item of state.cartItems) {
      itemsHtml += `
        <div class="flex items-center justify-between gap-3 p-3 rounded-2xl bg-slate-50 border border-slate-200">
          <img src="${item.image_url}" alt="${item.name}" class="w-14 h-14 rounded-xl object-cover bg-white shrink-0 border border-slate-100">
          <div class="flex-1 min-w-0">
            <h5 class="text-xs font-bold text-slate-900 truncate">${item.name}</h5>
            <div class="text-[11px] text-slate-600 font-medium">${item.unit} · ₹${item.price.toFixed(2)}</div>
            <div class="text-xs font-black text-slate-900 mt-1">₹${(item.price * item.quantity).toFixed(2)}</div>
          </div>
          <div class="flex items-center rounded-xl bg-brand-green text-white font-black text-xs">
            <button onclick="updateCartQuantity(${item.id}, ${item.quantity - 1})" class="px-2 py-1 hover:bg-emerald-700 rounded-l-xl transition">-</button>
            <span class="px-2 py-1 min-w-[20px] text-center">${item.quantity}</span>
            <button onclick="updateCartQuantity(${item.id}, ${item.quantity + 1})" class="px-2 py-1 hover:bg-emerald-700 rounded-r-xl transition">+</button>
          </div>
        </div>
      `;
    }
    itemsContainer.innerHTML = itemsHtml;

    // Bill Details
    document.getElementById("billItemTotal").innerText = `₹${bill.item_total.toFixed(2)}`;
    document.getElementById("billDeliveryFee").innerText = bill.delivery_fee === 0 ? "FREE" : `₹${bill.delivery_fee.toFixed(2)}`;
    document.getElementById("billHandlingFee").innerText = `₹${bill.handling_fee.toFixed(2)}`;
    
    // Tip
    const tipRow = document.getElementById("billTipRow");
    if (bill.tip > 0) {
      tipRow.classList.remove("hidden");
      document.getElementById("billTip").innerText = `₹${bill.tip.toFixed(2)}`;
    } else {
      tipRow.classList.add("hidden");
    }

    // Coupon Discount
    const discRow = document.getElementById("billDiscountRow");
    if (bill.coupon_discount > 0) {
      discRow.classList.remove("hidden");
      document.getElementById("billDiscount").innerText = `-₹${bill.coupon_discount.toFixed(2)}`;
    } else {
      discRow.classList.add("hidden");
    }

    document.getElementById("billFinalAmount").innerText = `₹${bill.final_amount.toFixed(2)}`;
    document.getElementById("checkoutTotalLabel").innerText = `₹${bill.final_amount.toFixed(2)}`;
    document.getElementById("checkoutAmountDisplay").innerText = `₹${bill.final_amount.toFixed(2)}`;
    
    const savingsBanner = document.getElementById("billSavingsBanner");
    if (bill.total_savings > 0) {
      savingsBanner.classList.remove("hidden");
      savingsBanner.innerText = `🎉 You saved ₹${bill.total_savings.toFixed(2)} on this order!`;
    } else {
      savingsBanner.classList.add("hidden");
    }
  }

  // Update buttons on the active product cards
  for (const p of state.products) {
    const el = document.getElementById(`product-action-${p.id}`);
    if (el) {
      el.innerHTML = renderCartButton(p.id, state.cartMap[p.id] || 0, p.in_stock);
    }
  }
}

function updateWishlistBadge() {
  const badge = document.getElementById("wishlistBadge");
  const count = state.wishlistIds.size;
  if (count > 0) {
    badge.classList.remove("hidden");
    badge.innerText = count;
  } else {
    badge.classList.add("hidden");
  }
  document.getElementById("wishlistCountBadge").innerText = count;
}

function renderWishlistDrawerItems(items) {
  const container = document.getElementById("wishlistItemsList");
  if (!items || items.length === 0) {
    container.innerHTML = `
      <div class="py-16 text-center text-slate-600">
        <i data-lucide="heart" class="w-12 h-12 mx-auto text-slate-300 mb-2"></i>
        <p class="text-xs font-bold">Your wishlist is empty</p>
        <p class="text-[11px] text-slate-600 mt-0.5">Tap the heart on any product to save it here</p>
      </div>
    `;
    lucide.createIcons();
    return;
  }

  let html = "";
  for (const item of items) {
    html += `
      <div class="flex items-center justify-between gap-3 p-3 rounded-2xl bg-slate-50 border border-slate-200">
        <img src="${item.image_url}" alt="${item.name}" class="w-14 h-14 rounded-xl object-cover bg-white shrink-0 border border-slate-100">
        <div class="flex-1 min-w-0">
          <h5 class="text-xs font-bold text-slate-900 truncate">${item.name}</h5>
          <div class="text-[11px] text-slate-600">${item.unit}</div>
          <div class="text-xs font-black text-slate-900 mt-1">₹${item.price.toFixed(2)}</div>
        </div>
        <div class="flex flex-col gap-1.5 items-end">
          <button onclick="moveToCartFromWishlist(${item.id})" class="px-3 py-1 bg-brand-green hover:bg-brand-greenDark text-white text-[11px] font-bold rounded-lg transition">
            Move to Cart
          </button>
          <button onclick="toggleWishlist(${item.id})" class="text-[10px] text-slate-600 hover:text-rose-600 font-bold">
            Remove
          </button>
        </div>
      </div>
    `;
  }
  container.innerHTML = html;
  lucide.createIcons();
}

function updateWalletUI() {
  const balanceStr = `₹${state.walletBalance.toFixed(2)}`;
  document.getElementById("navWalletBalance").innerText = balanceStr;
  document.getElementById("drawerWalletBalance").innerText = balanceStr;
  document.getElementById("checkoutWalletBalance").innerText = balanceStr;

  const container = document.getElementById("walletTransactionsList");
  if (!state.walletTransactions || state.walletTransactions.length === 0) {
    container.innerHTML = `<div class="text-xs text-slate-600 py-4 text-center">No transactions yet</div>`;
    return;
  }

  let html = "";
  for (const tx of state.walletTransactions) {
    const isCredit = tx.type === "credit";
    html += `
      <div class="flex items-center justify-between p-3 rounded-xl bg-white border border-slate-200 text-xs">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg ${isCredit ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'} flex items-center justify-center font-bold">
            <i data-lucide="${isCredit ? 'arrow-down-left' : 'arrow-up-right'}" class="w-4 h-4"></i>
          </div>
          <div>
            <div class="font-bold text-slate-900">${tx.title}</div>
            <div class="text-[10px] text-slate-600 font-mono">${tx.reference_id || ''} · ${tx.created_at ? tx.created_at.slice(0, 16).replace('T', ' ') : 'Just now'}</div>
          </div>
        </div>
        <div class="font-black text-sm ${isCredit ? 'text-brand-green' : 'text-slate-900'}">
          ${isCredit ? '+' : '-'}₹${tx.amount.toFixed(2)}
        </div>
      </div>
    `;
  }
  container.innerHTML = html;
  lucide.createIcons();
}

// ================= CART & WISHLIST ACTIONS =================

async function addToCart(productId) {
  playSound('pop');
  try {
    const res = await fetch("/api/cart/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, quantity: 1 })
    });
    if (res.ok) {
      await loadCart();
      showToast("Item added to cart!");
    } else {
      const err = await res.json();
      showToast(err.detail || "Could not add to cart", "error");
    }
  } catch (err) {
    console.error(err);
  }
}

async function updateCartQuantity(productId, newQty) {
  playSound('pop');
  try {
    const res = await fetch("/api/cart/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, quantity: newQty })
    });
    if (res.ok) {
      await loadCart();
    }
  } catch (err) {
    console.error(err);
  }
}

async function toggleWishlist(productId) {
  try {
    const res = await fetch("/api/wishlist/toggle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId })
    });
    const data = await res.json();
    if (data.is_wishlisted) {
      state.wishlistIds.add(productId);
      showToast("Saved to wishlist!");
    } else {
      state.wishlistIds.delete(productId);
      showToast("Removed from wishlist");
    }
    updateWishlistBadge();
    await loadWishlist();
    renderProductsGrid();
  } catch (err) {
    console.error(err);
  }
}

async function moveToCartFromWishlist(productId) {
  playSound('pop');
  try {
    const res = await fetch("/api/wishlist/move-to-cart", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId })
    });
    if (res.ok) {
      await loadWishlist();
      await loadCart();
      showToast("Moved item to cart!");
    }
  } catch (err) {
    console.error(err);
  }
}

function setTip(amount) {
  state.currentTip = amount;
  document.querySelectorAll(".tip-btn").forEach(btn => {
    if (parseInt(btn.dataset.tip) === amount) {
      btn.className = "tip-btn px-2.5 py-1 text-xs font-black rounded-lg border-2 border-brand-green bg-emerald-50 text-brand-green";
    } else {
      btn.className = "tip-btn px-2.5 py-1 text-xs font-bold rounded-lg border border-slate-200 bg-white text-slate-700";
    }
  });
  loadCart();
}

function applyCoupon() {
  const code = document.getElementById("couponInput").value.trim().toUpperCase();
  if (!code) return;
  state.couponCode = code;
  loadCart().then(() => {
    const msgEl = document.getElementById("couponStatusMessage");
    msgEl.classList.remove("hidden");
    if (state.cartBill.coupon_code) {
      msgEl.className = "text-[11px] font-bold text-brand-green";
      msgEl.innerText = `✓ ${state.cartBill.coupon_message}`;
      showToast("Coupon Applied Successfully!");
    } else {
      msgEl.className = "text-[11px] font-bold text-rose-600";
      msgEl.innerText = `✕ ${state.cartBill.coupon_message || 'Invalid Coupon'}`;
    }
  });
}

// ================= CHECKOUT & 10-MIN TRACKING =================

function openCheckoutModal() {
  closeCartDrawer();
  const modal = document.getElementById("checkoutModal");
  modal.classList.remove("hidden");

  // Render addresses in checkout
  const addrContainer = document.getElementById("checkoutAddressOptions");
  let html = "";
  for (const addr of state.addresses) {
    const isSelected = state.selectedAddressId === addr.id;
    html += `
      <label class="flex items-center justify-between p-3 rounded-2xl border ${isSelected ? 'border-brand-green bg-emerald-50/40' : 'border-slate-200 bg-white'} cursor-pointer transition">
        <div class="flex items-center gap-3">
          <input type="radio" name="checkout_addr" value="${addr.id}" ${isSelected ? 'checked' : ''} onchange="state.selectedAddressId = ${addr.id}" class="text-brand-green focus:ring-brand-green">
          <div>
            <div class="font-bold text-xs text-slate-900">${addr.tag}</div>
            <div class="text-[11px] text-slate-600">${addr.address_line}, ${addr.city}</div>
          </div>
        </div>
        ${addr.is_default ? `<span class="text-[10px] font-extrabold text-brand-green bg-emerald-100 px-2 py-0.5 rounded">Default</span>` : ''}
      </label>
    `;
  }
  addrContainer.innerHTML = html;
  lucide.createIcons();
}

function closeCheckoutModal() {
  document.getElementById("checkoutModal").classList.add("hidden");
}

async function submitOrderCheckout() {
  const selectedPayment = document.querySelector('input[name="payment_method"]:checked')?.value || "wallet";
  const btn = document.getElementById("payNowBtn");
  btn.disabled = true;
  btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Processing...`;
  lucide.createIcons();

  try {
    const payload = {
      address_id: state.selectedAddressId,
      payment_method: selectedPayment,
      tip: state.currentTip,
      coupon_code: state.couponCode
    };

    const res = await fetch("/api/orders/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (res.ok) {
      playSound('chime');
      closeCheckoutModal();
      await loadCart();
      await loadWallet();
      
      // Start Live 10-Minute Delivery Tracking
      openLiveTracking(data.order_id);
      showToast("Order placed! Your 10-min delivery has started.");
    } else {
      showToast(data.detail || "Checkout failed", "error");
    }
  } catch (err) {
    console.error(err);
    showToast("Network error during checkout", "error");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span>Place Order</span><i data-lucide="zap" class="w-4 h-4 fill-white"></i>`;
    lucide.createIcons();
  }
}

function openLiveTracking(orderId) {
  const modal = document.getElementById("trackingModal");
  modal.classList.remove("hidden");
  
  // Clear any prior timer
  if (state.trackingTimer) clearInterval(state.trackingTimer);

  const fetchTracking = async () => {
    try {
      const res = await fetch(`/api/orders/${orderId}/tracking`);
      if (!res.ok) return;
      const data = await res.json();

      document.getElementById("trackStageTitle").innerText = data.stage_text;
      document.getElementById("trackSubText").innerText = data.sub_text;
      document.getElementById("trackOrderNum").innerText = data.order_number;
      document.getElementById("trackAddressText").innerText = data.delivery_address;
      
      // Countdown
      const remainingSeconds = Math.max(0, 600 - data.elapsed_seconds);
      const mins = Math.floor(remainingSeconds / 60).toString().padStart(2, '0');
      const secs = (remainingSeconds % 60).toString().padStart(2, '0');
      document.getElementById("trackEtaDisplay").innerText = `${mins}m ${secs}s`;

      // Progress bar & animated scooter
      const pct = data.progress_pct;
      document.getElementById("trackProgressBar").style.width = `${pct}%`;
      document.getElementById("trackScooterMarker").style.left = `${Math.min(96, Math.max(4, pct))}%`;

      // Rider details
      document.getElementById("trackRiderName").innerText = data.rider.name;
      document.getElementById("trackRiderRating").innerText = data.rider.rating;
      document.getElementById("trackRiderVehicle").innerText = data.rider.vehicle;

      // 4 Milestone Stages
      const milestonesContainer = document.getElementById("trackMilestonesContainer");
      let mHtml = "";
      for (const s of data.stages) {
        const isDone = s.done;
        const isCurrent = s.current;
        mHtml += `
          <div class="flex flex-col items-center">
            <div class="w-6 h-6 rounded-full flex items-center justify-center font-bold mb-1 ${isDone ? 'bg-emerald-500 text-white' : isCurrent ? 'bg-amber-400 text-slate-900 ring-4 ring-amber-400/20' : 'bg-slate-800 text-slate-600'}">
              ${isDone ? '✓' : '•'}
            </div>
            <div class="font-bold leading-tight ${isCurrent ? 'text-amber-400' : isDone ? 'text-white' : 'text-slate-600'}">${s.title}</div>
          </div>
        `;
      }
      milestonesContainer.innerHTML = mHtml;

    } catch (err) {
      console.error(err);
    }
  };

  fetchTracking();
  state.trackingTimer = setInterval(fetchTracking, 3000);
}

function closeTrackingModal() {
  if (state.trackingTimer) clearInterval(state.trackingTimer);
  document.getElementById("trackingModal").classList.add("hidden");
}

// ================= WALLET =================

function openWalletDrawer() {
  document.getElementById("walletDrawer").classList.remove("hidden");
}
function closeWalletDrawer() {
  document.getElementById("walletDrawer").classList.add("hidden");
}

function setTopUpAmount(amt) {
  document.getElementById("topupInput").value = amt;
}

async function submitWalletTopUp() {
  const amt = parseFloat(document.getElementById("topupInput").value);
  if (!amt || amt <= 0) {
    showToast("Please enter a valid amount", "error");
    return;
  }

  try {
    const res = await fetch("/api/wallet/topup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount: amt, payment_channel: "UPI Instant" })
    });
    const data = await res.json();
    if (res.ok) {
      playSound('chime');
      await loadWallet();
      showToast(data.message);
    } else {
      showToast(data.detail || "Top-up failed", "error");
    }
  } catch (err) {
    console.error(err);
  }
}

// ================= PRODUCT QUICK VIEW =================

async function openProductQuickView(productId) {
  const modal = document.getElementById("productQuickModal");
  const container = document.getElementById("productQuickModalContent");
  modal.classList.remove("hidden");
  
  container.innerHTML = `
    <div class="p-8 text-center text-xs font-bold text-slate-600 flex items-center justify-center gap-2">
      <i data-lucide="loader-2" class="w-5 h-5 animate-spin text-brand-green"></i> Loading item details...
    </div>
  `;
  lucide.createIcons();

  try {
    const res = await fetch(`/api/products/${productId}`);
    const data = await res.json();
    const p = data.product;
    const inCartQty = state.cartMap[p.id] || 0;
    const isWishlisted = state.wishlistIds.has(p.id);

    container.innerHTML = `
      <div class="relative bg-slate-100 aspect-video flex items-center justify-center overflow-hidden">
        <img src="${p.image_url}" alt="${p.name}" class="w-full h-full object-cover">
        <button onclick="closeProductQuickView()" class="absolute top-3 right-3 p-2 rounded-full bg-white/80 backdrop-blur-xs text-slate-700 hover:bg-white transition">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
        <span class="absolute bottom-3 left-3 bg-slate-900/80 backdrop-blur-xs text-white text-xs font-black px-2.5 py-1 rounded-lg flex items-center gap-1">
          <i data-lucide="clock" class="w-3.5 h-3.5 text-amber-400"></i> ${p.delivery_eta} Delivery
        </span>
      </div>

      <div class="p-6 space-y-4">
        <div class="flex items-start justify-between gap-3">
          <div>
            <div class="text-xs font-extrabold text-brand-green uppercase tracking-wider">${p.category} · ${p.subcategory}</div>
            <h3 class="text-lg font-black text-slate-900 mt-0.5">${p.name}</h3>
            <div class="text-xs font-semibold text-slate-600 mt-1">${p.unit}</div>
          </div>
          <button onclick="toggleWishlist(${p.id})" class="p-2 rounded-xl bg-slate-100 hover:bg-rose-50 text-slate-600 hover:text-rose-500 transition">
            <i data-lucide="heart" class="w-5 h-5 ${isWishlisted ? 'fill-rose-500 text-rose-500' : ''}"></i>
          </button>
        </div>

        <p class="text-xs text-slate-600 leading-relaxed">${p.description}</p>

        <!-- Rating & Quality badge -->
        <div class="flex items-center gap-3 text-xs">
          <span class="bg-amber-100 text-amber-900 font-extrabold px-2 py-0.5 rounded flex items-center gap-1">
            ★ ${p.rating} (${p.rating_count} ratings)
          </span>
          <span class="text-slate-600 font-medium">Brand: <strong class="text-slate-800">${p.brand}</strong></span>
        </div>

        <div class="pt-4 border-t border-slate-100 flex items-center justify-between">
          <div>
            <div class="text-2xl font-black text-slate-900">₹${p.price.toFixed(2)}</div>
            ${p.mrp > p.price ? `<div class="text-xs text-slate-600 line-through">MRP: ₹${p.mrp.toFixed(2)} (${p.discount_pct}% OFF)</div>` : ''}
          </div>

          <div class="flex items-center gap-2">
            ${renderCartButton(p.id, inCartQty, p.in_stock)}
          </div>
        </div>
      </div>
    `;
    lucide.createIcons();
  } catch (err) {
    console.error(err);
  }
}

function closeProductQuickView() {
  document.getElementById("productQuickModal").classList.add("hidden");
}

// ================= SETTINGS & PROFILE =================

function openSettingsModal(tab = 'profile') {
  document.getElementById("settingsModal").classList.remove("hidden");
  switchSettingsTab(tab);
}

function closeSettingsModal() {
  document.getElementById("settingsModal").classList.add("hidden");
}

function switchSettingsTab(tab) {
  document.querySelectorAll(".settings-tab-btn").forEach(btn => {
    if (btn.dataset.tab === tab) {
      btn.className = "settings-tab-btn px-4 py-3 text-xs font-extrabold border-b-2 border-brand-green text-brand-green";
    } else {
      btn.className = "settings-tab-btn px-4 py-3 text-xs font-bold border-b-2 border-transparent text-slate-600 hover:text-slate-800";
    }
  });

  document.getElementById("tabContentProfile").classList.toggle("hidden", tab !== "profile");
  document.getElementById("tabContentAddresses").classList.toggle("hidden", tab !== "addresses");
  document.getElementById("tabContentOrders").classList.toggle("hidden", tab !== "orders");

  if (tab === "orders") loadPastOrders();
}

async function saveProfileChanges() {
  const name = document.getElementById("profileNameInput").value.trim();
  const email = document.getElementById("profileEmailInput").value.trim();

  try {
    const res = await fetch("/api/user/profile", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email })
    });
    if (res.ok) {
      await loadUserProfile();
      showToast("Profile updated successfully!");
    }
  } catch (err) {
    console.error(err);
  }
}

function renderAddressesList() {
  const container = document.getElementById("settingsAddressesList");
  if (!container) return;

  let html = "";
  for (const addr of state.addresses) {
    html += `
      <div class="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-xl bg-white border border-slate-200 flex items-center justify-center font-black text-brand-green">
            <i data-lucide="${addr.tag === 'Home' ? 'home' : addr.tag === 'Work' ? 'briefcase' : 'map-pin'}" class="w-4 h-4"></i>
          </div>
          <div>
            <div class="font-black text-slate-900 flex items-center gap-2">
              <span>${addr.tag}</span>
              ${addr.is_default ? `<span class="bg-emerald-100 text-brand-green text-[10px] px-1.5 py-0.2 rounded font-extrabold">Default</span>` : ''}
            </div>
            <div class="text-slate-600 font-medium">${addr.address_line}, ${addr.city} - ${addr.pincode}</div>
          </div>
        </div>
        <div class="flex items-center gap-2">
          ${!addr.is_default ? `<button onclick="setDefaultAddress(${addr.id})" class="text-[11px] font-bold text-brand-green hover:underline">Make Default</button>` : ''}
          <button onclick="deleteAddress(${addr.id})" class="text-slate-600 hover:text-rose-600 p-1">
            <i data-lucide="trash-2" class="w-4 h-4"></i>
          </button>
        </div>
      </div>
    `;
  }
  container.innerHTML = html;
  lucide.createIcons();
}

function toggleNewAddressForm() {
  const form = document.getElementById("newAddressForm");
  form.classList.toggle("hidden");
}

async function saveNewAddress() {
  const tag = document.getElementById("newAddrTag").value;
  const address_line = document.getElementById("newAddrLine").value.trim();
  const landmark = document.getElementById("newAddrLandmark").value.trim();
  const pincode = document.getElementById("newAddrPincode").value.trim();

  if (!address_line) {
    showToast("Please enter an address line", "error");
    return;
  }

  try {
    const res = await fetch("/api/user/addresses", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tag, address_line, landmark, pincode, city: "Bhubaneswar", is_default: false })
    });
    if (res.ok) {
      toggleNewAddressForm();
      await loadUserProfile();
      showToast("Address saved!");
    }
  } catch (err) {
    console.error(err);
  }
}

async function setDefaultAddress(id) {
  try {
    const res = await fetch(`/api/user/addresses/${id}/default`, { method: "PUT" });
    if (res.ok) {
      await loadUserProfile();
      showToast("Default address updated");
    }
  } catch (err) {
    console.error(err);
  }
}

async function deleteAddress(id) {
  try {
    const res = await fetch(`/api/user/addresses/${id}`, { method: "DELETE" });
    if (res.ok) {
      await loadUserProfile();
      showToast("Address removed");
    }
  } catch (err) {
    console.error(err);
  }
}

async function loadPastOrders() {
  const container = document.getElementById("tabContentOrders");
  container.innerHTML = `
    <div class="py-12 text-center text-xs text-slate-600 font-bold flex items-center justify-center gap-2">
      <i data-lucide="loader-2" class="w-4 h-4 animate-spin text-brand-green"></i> Loading orders...
    </div>
  `;
  lucide.createIcons();

  try {
    const res = await fetch("/api/orders");
    const data = await res.json();
    
    if (!data.orders || data.orders.length === 0) {
      container.innerHTML = `
        <div class="py-12 text-center text-slate-600">
          <i data-lucide="package" class="w-10 h-10 mx-auto text-slate-300 mb-2"></i>
          <p class="text-xs font-bold">No past orders yet</p>
        </div>
      `;
      lucide.createIcons();
      return;
    }

    let html = "";
    for (const ord of data.orders) {
      html += `
        <div class="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
          <div class="flex items-center justify-between text-xs">
            <div>
              <span class="font-extrabold text-slate-900">${ord.order_number}</span>
              <span class="text-slate-600 text-[11px] block">${ord.created_at ? ord.created_at.slice(0, 16).replace('T', ' ') : ''}</span>
            </div>
            <div class="text-right">
              <span class="font-black text-sm text-slate-900">₹${ord.total_amount.toFixed(2)}</span>
              <span class="block text-[10px] font-extrabold uppercase text-emerald-700 bg-emerald-100 px-1.5 py-0.2 rounded">Delivered</span>
            </div>
          </div>
          
          <div class="text-[11px] text-slate-600 border-t border-slate-200/60 pt-2 line-clamp-1">
            ${ord.items ? ord.items.map(i => `${i.product_name} (${i.quantity})`).join(", ") : ''}
          </div>

          <div class="flex items-center justify-between pt-1">
            <button onclick="openLiveTracking(${ord.id})" class="text-xs font-bold text-brand-green hover:underline flex items-center gap-1">
              <i data-lucide="map-pin" class="w-3.5 h-3.5"></i> Track / View Invoice
            </button>
            <button onclick="reorderItems(${ord.id})" class="px-3 py-1 bg-white border border-slate-300 hover:border-brand-green text-slate-800 text-xs font-bold rounded-xl transition">
              Reorder All
            </button>
          </div>
        </div>
      `;
    }
    container.innerHTML = html;
    lucide.createIcons();
  } catch (err) {
    console.error(err);
  }
}

async function reorderItems(orderId) {
  try {
    const res = await fetch(`/api/orders/${orderId}`);
    const data = await res.json();
    for (const itm of data.order.items) {
      await fetch("/api/cart/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_id: itm.product_id, quantity: itm.quantity })
      });
    }
    await loadCart();
    closeSettingsModal();
    openCartDrawer();
    showToast("Reordered items added to your cart!");
  } catch (err) {
    console.error(err);
  }
}

// ================= AUTH / LOGIN =================

function openLoginModal() {
  document.getElementById("loginModal").classList.remove("hidden");
}
function closeLoginModal() {
  document.getElementById("loginModal").classList.add("hidden");
}
function autofillDemoOtp() {
  document.getElementById("loginOtpInput").value = "1234";
}

async function submitLogin() {
  const phone = document.getElementById("loginPhoneInput").value.trim();
  const otp = document.getElementById("loginOtpInput").value.trim();

  if (phone.length < 10) {
    showToast("Please enter a valid 10-digit number", "error");
    return;
  }

  try {
    const res = await fetch("/api/user/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone, otp })
    });
    const data = await res.json();
    if (res.ok) {
      playSound('chime');
      closeLoginModal();
      await loadUserProfile();
      showToast(data.message);
    } else {
      showToast(data.detail || "Login failed", "error");
    }
  } catch (err) {
    console.error(err);
  }
}

// ================= DRAWER TOGGLES =================

function openCartDrawer() {
  document.getElementById("cartDrawer").classList.remove("hidden");
}
function closeCartDrawer() {
  document.getElementById("cartDrawer").classList.add("hidden");
}

function openWishlistDrawer() {
  document.getElementById("wishlistDrawer").classList.remove("hidden");
}
function closeWishlistDrawer() {
  document.getElementById("wishlistDrawer").classList.add("hidden");
}

// ================= FILTERS & NAVIGATION =================

function selectCategory(catName) {
  state.currentCategory = catName;
  state.currentSubcategory = "all";
  state.page = 1;
  renderCategoryCapsules();
  loadProducts();
}

function selectSubcategory(subName) {
  state.currentSubcategory = subName;
  state.page = 1;
  updateCategoryHeaderInfo();
  loadProducts();
}

function handleSortChange(val) {
  state.sortBy = val;
  state.page = 1;
  loadProducts();
}

function handleInStockFilter(isChecked) {
  state.inStockOnly = isChecked;
  state.page = 1;
  loadProducts();
}

function parsePriceInput(id) {
  const raw = document.getElementById(id).value.trim();
  if (raw === "") return null;
  const n = parseFloat(raw);
  return Number.isFinite(n) && n >= 0 ? n : null;
}

function syncPriceUI() {
  const minEl = document.getElementById("minPriceInput");
  const maxEl = document.getElementById("maxPriceInput");
  minEl.value = state.minPrice === null ? "" : state.minPrice;
  maxEl.value = state.maxPrice === null ? "" : state.maxPrice;

  const active = state.minPrice !== null || state.maxPrice !== null;
  const clearBtn = document.getElementById("clearPriceBtn");
  clearBtn.classList.toggle("hidden", !active);
  clearBtn.classList.toggle("inline-flex", active);

  document.querySelectorAll("#pricePresets .price-chip").forEach((chip) => {
    const cMin = chip.dataset.min === "" ? null : Number(chip.dataset.min);
    const cMax = chip.dataset.max === "" ? null : Number(chip.dataset.max);
    const on = cMin === state.minPrice && cMax === state.maxPrice;
    chip.classList.toggle("bg-brand-green", on);
    chip.classList.toggle("text-white", on);
    chip.classList.toggle("border-brand-green", on);
    chip.classList.toggle("bg-white", !on);
    chip.classList.toggle("text-slate-700", !on);
  });
}

function applyPriceFilter() {
  let min = parsePriceInput("minPriceInput");
  let max = parsePriceInput("maxPriceInput");
  if (min !== null && max !== null && min > max) [min, max] = [max, min];
  state.minPrice = min;
  state.maxPrice = max;
  state.page = 1;
  syncPriceUI();
  loadProducts();
}

function setPricePreset(min, max) {
  // Clicking the active preset again clears it
  if (state.minPrice === min && state.maxPrice === max) {
    clearPriceFilter();
    return;
  }
  state.minPrice = min;
  state.maxPrice = max;
  state.page = 1;
  syncPriceUI();
  loadProducts();
}

function clearPriceFilter() {
  state.minPrice = null;
  state.maxPrice = null;
  state.page = 1;
  syncPriceUI();
  loadProducts();
}

function goToPage(p) {
  if (p < 1 || p > state.totalPages) return;
  state.page = p;
  loadProducts();
  window.scrollTo({ top: 400, behavior: "smooth" });
}

function setupSearchListener() {
  const input = document.getElementById("searchInput");
  const clearBtn = document.getElementById("clearSearchBtn");
  let timeout = null;

  input.addEventListener("input", (e) => {
    const val = e.target.value;
    clearBtn.classList.toggle("hidden", !val);

    clearTimeout(timeout);
    timeout = setTimeout(() => {
      state.searchQuery = val;
      state.page = 1;
      
      const banner = document.getElementById("searchFilterBanner");
      if (val) {
        banner.classList.remove("hidden");
        document.getElementById("searchQueryText").innerText = `"${val}"`;
      } else {
        banner.classList.add("hidden");
      }

      loadProducts();
    }, 280);
  });
}

function clearSearch() {
  const input = document.getElementById("searchInput");
  input.value = "";
  document.getElementById("clearSearchBtn").classList.add("hidden");
  document.getElementById("searchFilterBanner").classList.add("hidden");
  state.searchQuery = "";
  state.page = 1;
  loadProducts();
}

function resetFilters() {
  state.currentCategory = "all";
  state.currentSubcategory = "all";
  state.searchQuery = "";
  state.sortBy = "popular";
  state.inStockOnly = false;
  state.minPrice = null;
  state.maxPrice = null;
  state.page = 1;
  syncPriceUI();
  
  document.getElementById("searchInput").value = "";
  document.getElementById("clearSearchBtn").classList.add("hidden");
  document.getElementById("searchFilterBanner").classList.add("hidden");
  document.getElementById("inStockCheckbox").checked = false;
  document.getElementById("sortBySelect").value = "popular";

  renderCategoryCapsules();
  loadProducts();
}

// ================= QUICKCOMMERCE API INTEGRATION =================

async function loadQcStatus() {
  try {
    const res = await fetch("/api/qc/status");
    const data = await res.json();
    state.qcStatus = data;

    const credits = data.credits?.summary?.total_available ?? "Active";
    const navPill = document.getElementById("navQcCredits");
    if (navPill) {
      navPill.innerText = `${credits} Credits`;
    }

    const modalCredits = document.getElementById("modalQcCredits");
    if (modalCredits) {
      modalCredits.innerText = credits;
    }

    const modalKey = document.getElementById("modalQcApiKey");
    if (modalKey && data.masked_api_key) {
      modalKey.innerText = data.masked_api_key;
    }

    const modalSynced = document.getElementById("modalQcSyncedCount");
    if (modalSynced) {
      modalSynced.innerText = data.total_products_synced || 0;
    }
  } catch (err) {
    console.error("Failed to load QuickCommerce API status", err);
  }
}

function openQcModal() {
  loadQcStatus();
  document.getElementById("qcApiModal").classList.remove("hidden");
  lucide.createIcons();
}

function closeQcModal() {
  document.getElementById("qcApiModal").classList.add("hidden");
}

async function refreshQcStatus() {
  await loadQcStatus();
  showToast("QuickCommerce API credits & status refreshed!");
}

async function executeLiveQcSearch() {
  const query = document.getElementById("qcSearchInput").value.trim();
  const platform = document.getElementById("qcSearchPlatform").value;
  const feedback = document.getElementById("qcLiveFeedback");
  const btn = document.getElementById("btnLiveQcSearch");

  if (!query) {
    showToast("Please enter a product search query", "error");
    return;
  }

  btn.disabled = true;
  btn.innerHTML = `<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i> Sourcing...`;
  feedback.classList.remove("hidden");
  feedback.innerHTML = `
    <div class="flex items-center gap-2 text-purple-700 font-bold">
      <i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i>
      <span>Querying ${platform} dark store in real-time via QuickCommerce API...</span>
    </div>
  `;
  lucide.createIcons();

  try {
    const params = new URLSearchParams({ q: query, platform: platform });
    const res = await fetch(`/api/qc/search?${params.toString()}`);
    const data = await res.json();

    if (res.ok) {
      playSound('chime');
      feedback.innerHTML = `
        <div class="text-emerald-700 font-black flex items-center gap-1.5">
          <i data-lucide="check-circle" class="w-4 h-4"></i>
          <span>Found ${data.total_results} items on ${platform}!</span>
        </div>
        <div class="text-[11px] text-slate-600 font-medium">
          Added ${data.saved_to_catalog} new SKUs to your active catalog. Credits remaining: <strong>${data.credits_remaining ?? 'Active'}</strong>.
        </div>
      `;
      lucide.createIcons();
      showToast(`Added live products from ${platform}!`);

      // Refresh catalog and categories
      await loadQcStatus();
      await loadCategories();
      await loadProducts();
    } else {
      feedback.innerHTML = `
        <div class="text-rose-600 font-bold flex items-center gap-1">
          <i data-lucide="alert-triangle" class="w-4 h-4"></i>
          <span>${data.detail || 'API Query Failed'}</span>
        </div>
      `;
      lucide.createIcons();
    }
  } catch (err) {
    console.error(err);
    feedback.innerHTML = `<span class="text-rose-600 font-bold">Network error calling QuickCommerce API</span>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i data-lucide="search" class="w-3.5 h-3.5"></i><span>Search API</span>`;
    lucide.createIcons();
  }
}
