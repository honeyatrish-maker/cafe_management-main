// Cafe Management System JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Dark Mode Toggle
    const themeToggle = document.getElementById('theme-toggle');
    const currentTheme = localStorage.getItem('theme') || 'light';

    // Set initial theme
    document.documentElement.setAttribute('data-theme', currentTheme);

    // Update toggle button state based on current theme
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);

            // Add smooth transition effect
            document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
            setTimeout(() => {
                document.body.style.transition = '';
            }, 300);
        });
    }

    // Menu management
    const addItemBtn = document.getElementById('add-item-btn');
    const addItemForm = document.getElementById('add-item-form');
    const cancelAddBtn = document.getElementById('cancel-add');
    const editItemForm = document.getElementById('edit-item-form');
    const cancelEditBtn = document.getElementById('cancel-edit');
    const editBtns = document.querySelectorAll('.edit-btn');

    if (addItemBtn && addItemForm) {
        addItemBtn.addEventListener('click', function() {
            addItemForm.style.display = 'block';
            if (editItemForm) editItemForm.style.display = 'none';
            addItemForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });

        cancelAddBtn.addEventListener('click', function() {
            addItemForm.style.display = 'none';
        });
    }

    if (editBtns.length > 0 && editItemForm) {
        editBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const itemId = this.getAttribute('data-id');
                const itemDiv = this.closest('.menu-item');
                const name = itemDiv.querySelector('h3').textContent;
                const description = itemDiv.querySelector('p').textContent;
                const price = itemDiv.querySelector('.price').textContent.replace('$', '');
                const category = itemDiv.querySelector('.category').textContent;
                const available = itemDiv.querySelector('.availability').textContent === 'Available';

                document.getElementById('edit-item-id').value = itemId;
                document.getElementById('edit-name').value = name;
                document.getElementById('edit-description').value = description;
                document.getElementById('edit-price').value = price;
                document.getElementById('edit-category').value = category;
                document.getElementById('edit-available').checked = available;

                editItemForm.style.display = 'block';
                if (addItemForm) addItemForm.style.display = 'none';
                editItemForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
            });
        });

        cancelEditBtn.addEventListener('click', function() {
            editItemForm.style.display = 'none';
        });
    }

    // Add smooth animations to cards
    const cards = document.querySelectorAll('.card, .stat-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });

    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="loading"></span> Processing...';
                submitBtn.disabled = true;
            }
        });
    });

    // Enhanced table interactions
    const tableRows = document.querySelectorAll('.table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.01)';
        });

        row.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.animation = 'slideOutRight 0.5s ease-out forwards';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });

    // Add to order functionality
    const addToOrderButtons = document.querySelectorAll('.add-to-order');
    const orderModal = document.getElementById('order-modal');
    const closeModal = document.querySelector('.close-modal');
    const orderForm = document.getElementById('order-form');
    const orderItems = document.getElementById('order-items');
    const orderTotal = document.getElementById('order-total');

    let currentOrder = [];
    const cartToggle = document.getElementById('cart-toggle');
    const searchInput = document.getElementById('menu-search');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const menuCards = document.querySelectorAll('.menu-item-card');
    let activeCategory = 'all';

    const hasOrderPage = orderModal && orderItems && orderTotal && orderForm && addToOrderButtons.length > 0;

    function saveCart() {
        localStorage.setItem('cafe_cart', JSON.stringify(currentOrder));
    }

    function loadCart() {
        const savedCart = localStorage.getItem('cafe_cart');
        if (savedCart) {
            try {
                currentOrder = JSON.parse(savedCart) || [];
            } catch (error) {
                currentOrder = [];
            }
        }
        updateOrderDisplay();
        updateCartBadge();
    }

    function updateCartBadge() {
        const count = currentOrder.reduce((sum, item) => sum + item.quantity, 0);
        const badge = document.getElementById('cart-count');
        if (badge) {
            badge.textContent = count;
            badge.style.opacity = count ? '1' : '0.65';
        }
    }

    function filterMenu() {
        const query = searchInput ? searchInput.value.trim().toLowerCase() : '';
        menuCards.forEach(card => {
            const cardName = card.querySelector('h4')?.textContent.toLowerCase() || '';
            const cardDesc = card.querySelector('p')?.textContent.toLowerCase() || '';
            const cardCategory = card.closest('.menu-category')?.querySelector('h3')?.textContent.toLowerCase() || '';
            const matchesSearch = query === '' || cardName.includes(query) || cardDesc.includes(query);
            const matchesCategory = activeCategory === 'all' || cardCategory === activeCategory;
            card.style.display = matchesSearch && matchesCategory ? 'grid' : 'none';
        });
    }

    // Handle quantity selectors on menu items
    const quantityMinusBtns = document.querySelectorAll('.qty-minus');
    const quantityPlusBtns = document.querySelectorAll('.qty-plus');
    const quantityInputs = document.querySelectorAll('.qty-input');

    quantityMinusBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const input = this.nextElementSibling;
            const currentVal = parseInt(input.value) || 1;
            input.value = Math.max(1, currentVal - 1);
        });
    });

    quantityPlusBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const input = this.previousElementSibling;
            const currentVal = parseInt(input.value) || 1;
            input.value = Math.min(99, currentVal + 1);
        });
    });

    if (hasOrderPage) {
        addToOrderButtons.forEach(button => {
            button.addEventListener('click', function() {
                const itemId = this.getAttribute('data-item-id');
                const itemName = this.getAttribute('data-name');
                const itemPrice = parseFloat(this.getAttribute('data-price'));
                
                // Get quantity from the associated input
                const quantityInput = this.closest('.menu-item-card').querySelector('.qty-input');
                const quantity = Math.max(1, parseInt(quantityInput.value) || 1);

                addItemToOrder(itemId, itemName, itemPrice, quantity);
                updateOrderDisplay();
                orderModal.style.display = 'block';
                
                // Reset quantity selector for next use
                quantityInput.value = 1;
            });
        });

        if (closeModal) {
            closeModal.addEventListener('click', function() {
                orderModal.style.display = 'none';
            });
        }

        if (cartToggle) {
            cartToggle.addEventListener('click', function() {
                updateOrderDisplay();
                orderModal.style.display = 'block';
            });
        }
    }

    if (searchInput) {
        searchInput.addEventListener('input', filterMenu);
    }

    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            activeCategory = this.getAttribute('data-category') || 'all';
            filterMenu();
        });
    });

    if (hasOrderPage) {
        loadCart();
    }

    // Close modal only on X button or when placing order, not on outside click
    window.addEventListener('click', function(event) {
        // Don't close if clicking inside the modal or on Add to Order buttons
        if (event.target === orderModal && event.target.classList.contains('modal')) {
            orderModal.style.display = 'none';
        }
    });

    function addItemToOrder(itemId, itemName, itemPrice, quantity = 1) {
        const existingItem = currentOrder.find(item => item.id === itemId);
        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            currentOrder.push({
                id: itemId,
                name: itemName,
                price: itemPrice,
                quantity: quantity
            });
        }
    }

    function updateOrderDisplay() {
        if (!orderItems || !orderTotal) {
            return;
        }

        orderItems.innerHTML = '';
        let total = 0;

        if (currentOrder.length === 0) {
            orderItems.innerHTML = '<p class="empty-order">Your cart is empty. Add items to place an order.</p>';
        }

        currentOrder.forEach((item, index) => {
            const itemTotal = item.price * item.quantity;
            total += itemTotal;

            const orderItemDiv = document.createElement('div');
            orderItemDiv.className = 'order-item';
            orderItemDiv.innerHTML = `
                <div class="order-item-info">
                    <h4>${item.name}</h4>
                    <p>₹${item.price.toFixed(2)} each</p>
                </div>
                <div class="order-item-controls">
                    <button class="quantity-btn" onclick="changeQuantity(${index}, -1)">-</button>
                    <span>${item.quantity}</span>
                    <button class="quantity-btn" onclick="changeQuantity(${index}, 1)">+</button>
                    <span class="remove-item" onclick="removeItem(${index})">×</span>
                </div>
            `;
            orderItems.appendChild(orderItemDiv);
        });

        orderTotal.textContent = total.toFixed(2);
        saveCart();
        updateCartBadge();
    }

    // Make functions global for onclick handlers
    window.changeQuantity = function(index, change) {
        currentOrder[index].quantity += change;
        if (currentOrder[index].quantity <= 0) {
            currentOrder.splice(index, 1);
        }
        updateOrderDisplay();
    };

    window.removeItem = function(index) {
        currentOrder.splice(index, 1);
        updateOrderDisplay();
    };

    // Continue shopping button
    const continueShoppingBtn = document.getElementById('continue-shopping');
    if (continueShoppingBtn) {
        continueShoppingBtn.addEventListener('click', function() {
            orderModal.style.display = 'none';
        });
    }

    if (orderForm) {
        orderForm.addEventListener('submit', function(e) {
            e.preventDefault();

            if (currentOrder.length === 0) {
                alert('Please add some items to your order first.');
                return;
            }

            const formData = new FormData(orderForm);
            formData.append('order_items', JSON.stringify(currentOrder));

            // Submit order via fetch
            fetch('/place_order', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Order placed successfully! Order #' + data.order_id);
                    currentOrder = [];
                    updateOrderDisplay();
                    orderModal.style.display = 'none';
                    orderForm.reset();
                    // Redirect to order details
                    window.location.href = '/order/' + data.order_id;
                } else {
                    alert('Error placing order: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error placing order. Please try again.');
            });
        });
    }

    // Add slideOutRight animation for alerts
    const style = document.createElement('style');
    style.textContent = `
@keyframes slideOutRight {
    from {
        opacity: 1;
        transform: translateX(0);
    }
    to {
        opacity: 0;
        transform: translateX(30px);
    }
}
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}
`;
    document.head.appendChild(style);

    // Orders management
    const createOrderBtn = document.getElementById('create-order-btn');
    const createOrderForm = document.getElementById('create-order-form');
    const cancelCreateBtn = document.getElementById('cancel-create');

    if (createOrderBtn && createOrderForm) {
        createOrderBtn.addEventListener('click', function() {
            createOrderForm.style.display = 'block';
        });

        cancelCreateBtn.addEventListener('click', function() {
            createOrderForm.style.display = 'none';
        });
    }

    // Form validation
    const formElements = document.querySelectorAll('form');
    formElements.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.style.borderColor = 'red';
                    isValid = false;
                } else {
                    field.style.borderColor = '#ddd';
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });

    // Auto-hide alerts after 5 seconds
    const alertElements = document.querySelectorAll('.alert');
    alertElements.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Print functionality for bills
    const printBtn = document.querySelector('button[onclick="window.print()"]');
    if (printBtn) {
        printBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    }

    // Dynamic menu item selection
    const menuItemSelect = document.getElementById('menu_item_id');
    if (menuItemSelect) {
        menuItemSelect.addEventListener('change', function() {
            // Could add price display or other dynamic features
        });
    }

    // Table availability check (basic)
    const tableSelect = document.getElementById('table_id');
    if (tableSelect) {
        // In a real app, this would check availability via AJAX
        tableSelect.addEventListener('change', function() {
            // Placeholder for table availability check
        });
    }
});

// Utility functions
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

function formatCurrency(amount) {
    return '$' + parseFloat(amount).toFixed(2);
}

// AJAX helper for future enhancements
function makeRequest(url, method = 'GET', data = null) {
    return fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: data ? JSON.stringify(data) : null
    })
    .then(response => response.json())
    .catch(error => console.error('Error:', error));
}