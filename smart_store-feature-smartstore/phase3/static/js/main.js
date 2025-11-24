let cart = {};
const cartTable = document.getElementById("cart-table");


function renderCart() {
    cartTable.innerHTML = `
        <tr>
            <th>Name</th>
            <th>Quantity</th>
            <th>Price</th>
        </tr>
    `;

    Object.entries(cart).forEach(([productID, item]) => {
        cartTable.innerHTML += `
        <tr>
            <td>${item.name}</td>
            <td>${item.quantity}</td>
            <td>$${item.price}</td>
            <td>
                <button onclick="removeFromCart('${productID}')">
                    Remove From Cart
                </button>
            </td>
        </tr>
        `
    });

    if (cart != null) {
        cartTable.innerHTML += `
        <tr>
            <button onclick="checkout()">
                Checkout
            </button>
        </tr>
        `
    }
}

function addToCart(productID, name, price, stock) {
    if (!cart[productID] && stock > 0) {
        cart[productID] = { name, price, quantity: 1 };
    } else {
        if (cart[productID].quantity < stock) {
            cart[productID].quantity += 1;
        } else {
            showNotification("No more stock available", "error");
            return;
        }
    }
    renderCart();
    showNotification(`Added ${name} to cart`, "success");
}

function removeFromCart(productID) {
    if (cart[productID]) {
        const name = cart[productID].name;
        cart[productID].quantity -= 1;
        if (cart[productID].quantity <= 0) {
            delete cart[productID];
        }
        renderCart();
        showNotification(`Removed ${name} from cart`, "success");
    }
}

function checkout() {
    fetch("/checkout/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({
            action: "checkout",
            cart: cart
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification("Checkout completed", "success");
            window.location.href = data.redirect_url;
        } else {
            showNotification(data.error || "Checkout failed", "error");
        }
    })
    .catch(err => {
        console.error("Checkout error", err);
        showNotification("Checkout failed", "error");
    });
}

function handleScan(event) {
    event.preventDefault();

    const input = document.getElementById("scan-code");
    if (!input) return;

    const code = input.value.trim();
    if (!code) return;

    const row = document.querySelector(
        `[data-barcode="${code}"], [data-rfid="${code}"]`
    );

    if (!row) {
        showNotification("Product not found for code " + code, "error");
        input.value = "";
        return;
    }

    const productId = row.dataset.productId;
    const name = row.dataset.name;
    const price = parseFloat(row.dataset.price);
    const stock = parseInt(row.dataset.stock, 10);

    addToCart(productId, name, price, stock);
    showNotification(`Scanned ${name}`, "success");
    input.value = "";
}

function showNotification(message, type = "success") {
    const container = document.getElementById("notification-container");
    if (!container) return;

    const div = document.createElement("div");
    div.className = `notification ${type}`;
    div.textContent = message;

    container.appendChild(div);

    setTimeout(() => {
        div.remove();
    }, 3000);
}

function getCSRFToken() {
    const name = "csrftoken=";
    const decoded = decodeURIComponent(document.cookie);
    const cookies = decoded.split("; ");
    for (let c of cookies) {
        if (c.startsWith(name)) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}