// Configuración de la URL base para las peticiones al servidor (API).
const API_URL = 'http://localhost:8000';

// ─── Estado de la Aplicación ──────────────────────────────────────────────────
// Mantenemos en memoria el carrito, el menú cargado y el token de sesión.
let cart = [];
let menu = [];
let token = localStorage.getItem('bt_token');

// ─── Inicialización ──────────────────────────────────────────────────────────
// Al cargar la página, detectamos qué vista mostrar (Cliente o Administrador).
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('menu-container')) initCustomerPage();
    if (document.getElementById('admin-container')) initAdminPage();
});

// ─── Lógica para el Cliente (Menú Digital) ────────────────────────────────────

/**
 * Inicia la página que verán los clientes para realizar sus pedidos.
 */
async function initCustomerPage() {
    await fetchMenu();
    setupCartListeners();
}

/**
 * Obtiene la lista de platos desde la API y activa el renderizado.
 */
async function fetchMenu() {
    try {
        const res = await fetch(`${API_URL}/menu`);
        menu = await res.json();
        renderMenu();
    } catch (e) { 
        console.error("Error al cargar el menú desde el servidor", e); 
    }
}

/**
 * Genera el HTML dinámico para mostrar cada plato del menú.
 */
function renderMenu() {
    const container = document.getElementById('menu-container');
    if (!container) return;
    container.innerHTML = menu.map(item => `
        <div class="glass-card fade-in" style="display: flex; flex-direction: column;">
            <div style="height: 200px; background: #f4f4f5; border-radius: 6px; margin-bottom: 1.25rem; display: flex; align-items: center; justify-content: center; overflow: hidden; border: 1px solid var(--border);">
                ${item.image_url ? `<img src="${item.image_url}" alt="${item.name}" style="width: 100%; height: 100%; object-fit: cover;">` : `<i class="fas fa-utensils fa-2x" style="color: var(--secondary); opacity: 0.3;"></i>`}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--text-main);">${item.name}</h3>
                <span style="font-weight: 800; font-size: 1rem;">$${item.price.toFixed(2)}</span>
            </div>
            <p style="color: var(--text-muted); font-size: 0.875rem; line-height: 1.5; margin-bottom: 1.5rem; flex-grow: 1;">${item.description}</p>
            <button class="btn btn-outline" style="width: 100%; border-width: 1px;" onclick="addToCart(${item.id})">
                <i class="fas fa-plus" style="font-size: 0.8rem;"></i> &nbsp; Añadir al Carrito
            </button>
        </div>
    `).join('');
}

/**
 * Añade un plato seleccionado al carrito de compras.
 * @param {number} id - ID del plato a añadir.
 */
function addToCart(id) {
    const item = menu.find(i => i.id === id);
    const existing = cart.find(i => i.menu_item_id === id);
    if (existing) {
        existing.quantity++;
    } else {
        cart.push({ menu_item_id: id, name: item.name, price: item.price, quantity: 1 });
    }
    updateCartUI();
}

/**
 * Actualiza el contador visual y el contenido del modal del carrito.
 */
function updateCartUI() {
    const count = cart.reduce((total, item) => total + item.quantity, 0);
    document.getElementById('cart-count').textContent = count;
    renderCart();
}

/**
 * Genera el desglose de productos y el total dentro del modal del carrito.
 */
function renderCart() {
    const container = document.getElementById('cart-items');
    if (!container) return;
    
    let total = 0;
    container.innerHTML = cart.map(item => {
        total += item.price * item.quantity;
        return `
            <div style="display: flex; justify-content: space-between; margin-bottom: 1rem; align-items: center;">
                <div>
                    <div style="font-weight: 600;">${item.name}</div>
                    <div style="color: var(--text-muted); font-size: 0.8rem;">$${item.price.toFixed(2)} x ${item.quantity}</div>
                </div>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    <button class="btn btn-outline" style="padding: 0.2rem 0.5rem;" onclick="changeQty(${item.menu_item_id}, -1)">-</button>
                    <span>${item.quantity}</span>
                    <button class="btn btn-outline" style="padding: 0.2rem 0.5rem;" onclick="changeQty(${item.menu_item_id}, 1)">+</button>
                </div>
            </div>
        `;
    }).join('');
    
    if (cart.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-muted);">Tu carrito está vacío</p>';
    }
    document.getElementById('cart-total').textContent = `$${total.toFixed(2)}`;
}

/**
 * Modifica la cantidad de un producto en el carrito.
 */
function changeQty(id, delta) {
    const item = cart.find(i => i.menu_item_id === id);
    if (!item) return;
    item.quantity += delta;
    if (item.quantity <= 0) {
        cart = cart.filter(i => i.menu_item_id !== id);
    }
    updateCartUI();
}

/**
 * Configura los eventos para abrir, cerrar y procesar el carrito.
 */
function setupCartListeners() {
    document.getElementById('view-cart-btn').onclick = () => document.getElementById('cart-modal').style.display = 'flex';
    document.getElementById('close-cart').onclick = () => document.getElementById('cart-modal').style.display = 'none';
    document.getElementById('checkout-btn').onclick = checkout;
}

/**
 * Envía el pedido a la API para ser procesado por la cocina.
 */
async function checkout() {
    const name = document.getElementById('cust-name').value;
    if (!name || cart.length === 0) {
        return alert("Por favor, ingresa tu nombre y añade al menos un plato al carrito.");
    }
    
    const body = {
        customer_name: name,
        items: cart.map(i => ({ menu_item_id: i.menu_item_id, quantity: i.quantity }))
    };

    try {
        const res = await fetch(`${API_URL}/orders`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        if (res.ok) {
            alert("¡Pedido enviado con éxito! Un camarero te atenderá pronto.");
            cart = [];
            updateCartUI();
            document.getElementById('cart-modal').style.display = 'none';
        } else {
            alert("Hubo un problema al procesar tu pedido. Por favor, intenta de nuevo.");
        }
    } catch (e) { 
        alert("No se pudo conectar con el servidor para enviar el pedido."); 
    }
}

// ─── Lógica para el Administrador (Gestión) ───────────────────────────────────

/**
 * Controla el acceso y visualización del panel administrativo.
 */
async function initAdminPage() {
    if (!token) {
        showLogin();
    } else {
        await showAdmin();
    }
    setupAdminListeners();
}

/** Muestra el formulario de inicio de sesión. */
function showLogin() {
    document.getElementById('login-container').style.display = 'block';
    document.getElementById('admin-container').style.display = 'none';
}

/** Muestra el panel de administración tras validar el token. */
async function showAdmin() {
    document.getElementById('login-container').style.display = 'none';
    document.getElementById('admin-container').style.display = 'block';
    document.getElementById('user-display').textContent = 'Panel de Administración';
    await Promise.all([fetchAdminOrders(), fetchMenuAdmin()]);
}

/** Asocia acciones a los botones del panel administrativo. */
function setupAdminListeners() {
    document.getElementById('login-btn').onclick = login;
    document.getElementById('logout-btn').onclick = logout;
    document.getElementById('refresh-orders-btn').onclick = fetchAdminOrders;
    
    // Gestión del modal para añadir platos
    document.getElementById('add-item-btn').onclick = () => document.getElementById('item-modal').style.display = 'flex';
    document.getElementById('close-item-modal').onclick = () => document.getElementById('item-modal').style.display = 'none';
    document.getElementById('item-form').onsubmit = handleItemSubmit;
}

/** Procesa el inicio de sesión enviando las credenciales a la API. */
async function login() {
    const u = document.getElementById('username').value;
    const p = document.getElementById('password').value;
    
    const formData = new URLSearchParams();
    formData.append('username', u);
    formData.append('password', p);

    try {
        const res = await fetch(`${API_URL}/token`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        if (data.access_token) {
            token = data.access_token;
            localStorage.setItem('bt_token', token);
            showAdmin();
        } else {
            alert("Acceso denegado: Usuario o contraseña incorrectos.");
        }
    } catch (e) { 
        alert("Error de conexión: No se pudo verificar la cuenta."); 
    }
}

/** Cierra la sesión y limpia el almacenamiento local. */
function logout() {
    localStorage.removeItem('bt_token');
    location.reload();
}

/** Obtiene todas las órdenes realizadas para mostrarlas en el dashboard. */
async function fetchAdminOrders() {
    try {
        const res = await fetch(`${API_URL}/orders`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const orders = await res.json();
        renderAdminOrders(orders);
    } catch (e) { 
        console.error("Error al obtener las órdenes", e); 
    }
}

/** Renderiza las tarjetas de cada orden en el panel administrativo. */
function renderAdminOrders(orders) {
    const container = document.getElementById('orders-dashboard');
    if (!container) return;
    
    container.innerHTML = orders.reverse().map(o => `
        <div class="glass-card fade-in" style="padding: 1.25rem; border-color: ${o.status === 'pendiente' ? 'var(--border)' : 'var(--secondary)'};">
            <div style="display: flex; justify-content: space-between; margin-bottom: 1.25rem; align-items: center;">
                <span style="color: var(--text-muted); font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">#ORD-${String(o.id).padStart(4, '0')}</span>
                <span class="badge badge-${o.status === 'pendiente' ? 'pending' : 'ready'}">${o.status.replace('_', ' ').toUpperCase()}</span>
            </div>
            <h3 style="margin-bottom: 0.5rem; font-size: 1.1rem; font-weight: 700;">${o.customer_name}</h3>
            <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1.25rem;">
                <i class="far fa-clock"></i> ${new Date(o.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
            </div>
            <div style="margin-bottom: 1.5rem; font-size: 0.85rem; color: var(--text-main);">
                <strong>${o.items.length}</strong> plato(s) solicitado(s)
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border); padding-top: 1.25rem;">
                <span style="font-weight: 800; font-size: 1.1rem;">$${o.total_price.toFixed(2)}</span>
                <select style="width: auto; margin-bottom: 0; font-size: 0.75rem; padding: 0.4rem 0.75rem; height: auto;" onchange="updateStatus(${o.id}, this.value)">
                    <option value="pendiente" ${o.status === 'pendiente' ? 'selected' : ''}>Pendiente</option>
                    <option value="en_preparacion" ${o.status === 'en_preparacion' ? 'selected' : ''}>Preparando</option>
                    <option value="listo" ${o.status === 'listo' ? 'selected' : ''}>Listo</option>
                    <option value="entregado" ${o.status === 'entregado' ? 'selected' : ''}>Entregado</option>
                    <option value="cancelado" ${o.status === 'cancelado' ? 'selected' : ''}>Cancelar</option>
                </select>
            </div>
        </div>
    `).join('');
}

/** Cambia el estado de una orden (ej: de Pendiente a Preparando). */
async function updateStatus(id, newStatus) {
    try {
        await fetch(`${API_URL}/orders/${id}/status`, {
            method: 'PATCH',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: newStatus })
        });
        fetchAdminOrders();
    } catch (e) { 
        console.error("Error al actualizar el estado de la orden", e); 
    }
}

/** Obtiene el menú en el panel admin para permitir ediciones rápidas. */
async function fetchMenuAdmin() {
    const res = await fetch(`${API_URL}/menu`);
    const data = await res.json();
    const container = document.getElementById('admin-menu-container');
    if (!container) return;
    
    container.innerHTML = data.map(item => `
        <div class="glass-card" style="display: flex; gap: 1rem; align-items: center; padding: 1rem;">
            <div style="flex: 1;">
                <h4 style="margin: 0;">${item.name}</h4>
                <div style="color: var(--text-muted); font-size: 0.8rem;">${item.category} - $${item.price.toFixed(2)}</div>
            </div>
            <button class="btn btn-outline" style="color: var(--danger); padding: 0.5rem;" onclick="deleteItem(${item.id})">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `).join('');
}

/** Procesa el envío del formulario para crear un nuevo plato. */
async function handleItemSubmit(e) {
    e.preventDefault();
    const body = {
        name: document.getElementById('m-name').value,
        description: document.getElementById('m-desc').value,
        price: parseFloat(document.getElementById('m-price').value),
        category: document.getElementById('m-cat').value
    };

    try {
        const res = await fetch(`${API_URL}/menu`, {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });
        if (res.ok) {
            document.getElementById('item-modal').style.display = 'none';
            document.getElementById('item-form').reset();
            fetchMenuAdmin();
        } else {
            alert("No se pudo guardar el plato. Verifica los datos.");
        }
    } catch (e) { 
        alert("Error al intentar guardar el nuevo plato."); 
    }
}

/** Elimina un item del menú tras confirmar con el usuario. */
async function deleteItem(id) {
    if (!confirm("¿Estás seguro de que deseas eliminar este plato del menú?")) return;
    try {
        const res = await fetch(`${API_URL}/menu/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            fetchMenuAdmin();
        } else {
            alert("No se pudo eliminar el item. Es posible que tenga pedidos asociados.");
        }
    } catch (e) { 
        console.error("Error al intentar eliminar el item", e); 
    }
}
