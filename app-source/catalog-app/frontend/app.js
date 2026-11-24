const form = document.querySelector("#product-form");
const nameInput = document.querySelector("#name");
const descriptionInput = document.querySelector("#description");
const priceInput = document.querySelector("#price");
const products = document.querySelector("#products");
const status = document.querySelector("#status");

async function request(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.error || `Request failed (${response.status})`);
  }
  return response.status === 204 ? null : response.json();
}

function renderProducts(items) {
  products.replaceChildren();
  for (const product of items) {
    const item = document.createElement("li");
    const details = document.createElement("span");
    const remove = document.createElement("button");
    details.textContent = `${product.name} - $${product.price.toFixed(2)}${product.description ? `: ${product.description}` : ""}`;
    remove.type = "button";
    remove.textContent = "Delete";
    remove.addEventListener("click", async () => {
      try {
        await request(`/api/products/${product.id}`, { method: "DELETE" });
        await loadProducts();
      } catch (error) {
        status.textContent = error.message;
      }
    });
    item.append(details, remove);
    products.append(item);
  }
}

async function loadProducts() {
  const data = await request("/api/products");
  renderProducts(data.products);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  status.textContent = "";
  try {
    await request("/api/products", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: nameInput.value,
        description: descriptionInput.value,
        price: priceInput.value,
      }),
    });
    form.reset();
    await loadProducts();
  } catch (error) {
    status.textContent = error.message;
  }
});

loadProducts().catch((error) => {
  status.textContent = error.message;
});
