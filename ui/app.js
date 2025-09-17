const screens = [
  { id: 'attract', name: 'Attract Loop' },
  { id: 'catalog', name: 'Product Selection' },
  { id: 'cart', name: 'Cart Review' },
  { id: 'payment', name: 'Payment & Confirmation' },
  { id: 'dispense', name: 'Dispensing & Pickup' },
  { id: 'admin', name: 'Admin & Analytics' },
];

const categories = ['All', 'Drinks', 'Snacks', 'Fresh', 'Bundles'];

const products = [
  {
    id: 'sparkling-citrus',
    name: 'Sparkling Citrus Fizz',
    price: 3.75,
    category: 'Drinks',
    description: 'Low sugar soda infused with vitamin C and electrolytes.',
    stock: 14,
    tags: ['popular'],
  },
  {
    id: 'cold-brew',
    name: 'Nitro Cold Brew',
    price: 4.5,
    category: 'Drinks',
    description: 'Slow steeped coffee with nitrogen micro-foam for a silky pour.',
    stock: 6,
    tags: ['fresh'],
  },
  {
    id: 'protein-bites',
    name: 'Cacao Protein Bites',
    price: 5.25,
    category: 'Snacks',
    description: 'Plant-based bites packed with 12g protein and omega-3s.',
    stock: 12,
    tags: ['popular'],
  },
  {
    id: 'hummus-pack',
    name: 'Hummus & Veggie Pack',
    price: 4.95,
    category: 'Fresh',
    description: 'Chilled hummus with tri-color carrots and snap peas.',
    stock: 7,
    tags: ['fresh'],
  },
  {
    id: 'smart-water',
    name: 'Electrolyte Water 1L',
    price: 2.85,
    category: 'Drinks',
    description: 'pH balanced mineral water in a recyclable bottle.',
    stock: 18,
    tags: [],
  },
  {
    id: 'trail-mix',
    name: 'Nordic Trail Mix',
    price: 3.95,
    category: 'Snacks',
    description: 'Roasted nuts, tart berries, and dark chocolate shards.',
    stock: 9,
    tags: [],
  },
  {
    id: 'yogurt-parfait',
    name: 'Berry Yogurt Parfait',
    price: 4.2,
    category: 'Fresh',
    description: 'Greek yogurt layered with granola and macerated berries.',
    stock: 5,
    tags: ['fresh', 'popular'],
  },
  {
    id: 'workday-bundle',
    name: 'Workday Power Bundle',
    price: 8.75,
    category: 'Bundles',
    description: 'Mix of protein bites, citrus fizz, and smart water.',
    stock: 4,
    tags: ['popular'],
  },
];

const analyticsSnapshot = {
  salesToday: 162.4,
  transactions: 48,
  avgVendTime: 18,
  uptime: '99.98%',
  salesByHour: [42, 28, 36, 51, 62, 44],
  lowStock: [
    { name: 'Nitro Cold Brew', remaining: 6 },
    { name: 'Berry Yogurt Parfait', remaining: 5 },
    { name: 'Workday Power Bundle', remaining: 4 },
  ],
  telemetry: {
    temperature: 4.2,
    humidity: 43,
    doorOpen: false,
  },
};

let activeCategory = 'All';
let cart = [];
let searchTerm = '';
let lastOrder = null;
let dispensingProgress = 0;
let dispenseTimer = null;
let demoTimers = [];

const screenRoot = document.getElementById('screen-root');
const screenButtonsContainer = document.getElementById('screen-buttons');
const prevButton = document.getElementById('prevScreen');
const nextButton = document.getElementById('nextScreen');
const runDemoButton = document.getElementById('runDemo');
const stopDemoButton = document.getElementById('stopDemo');
const resetButton = document.getElementById('resetFlow');
const statusTime = document.getElementById('status-time');
const statusDay = document.getElementById('status-day');
const statusEnvironment = document.getElementById('status-environment');
const statusDoor = document.getElementById('status-door');
const statusNetwork = document.getElementById('status-network');
const cartIndicator = document.getElementById('cart-indicator');
const flowStatus = document.getElementById('flowStatus');

let currentScreenIndex = 0;

function init() {
  buildScreenButtons();
  attachControls();
  updateDateTime();
  updateEnvironmentReadings();
  updateNetworkStatus();
  updateCartIndicator();
  setInterval(updateDateTime, 30 * 1000);
  setInterval(updateEnvironmentReadings, 12 * 1000);
  setInterval(updateNetworkStatus, 25 * 1000);
  showScreen(0);
  setFlowStatus('Ready to explore.');
}

function buildScreenButtons() {
  screens.forEach((screen, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'control-button';
    button.textContent = screen.name;
    button.dataset.screenId = screen.id;
    button.addEventListener('click', () => {
      stopGuidedFlow();
      showScreen(index);
    });
    screenButtonsContainer.appendChild(button);
  });
}

function attachControls() {
  prevButton.addEventListener('click', () => {
    stopGuidedFlow();
    const target = Math.max(currentScreenIndex - 1, 0);
    showScreen(target);
  });

  nextButton.addEventListener('click', () => {
    stopGuidedFlow();
    const target = Math.min(currentScreenIndex + 1, screens.length - 1);
    showScreen(target);
  });

  runDemoButton.addEventListener('click', runGuidedFlow);
  stopDemoButton.addEventListener('click', () => {
    stopGuidedFlow();
    setFlowStatus('Guided flow paused. Navigate manually.');
  });
  resetButton.addEventListener('click', () => {
    stopGuidedFlow();
    resetExperience();
    showScreen(0);
  });
}

function showScreen(target) {
  const targetIndex = typeof target === 'number' ? target : screens.findIndex((s) => s.id === target);
  if (targetIndex < 0 || targetIndex >= screens.length) return;

  currentScreenIndex = targetIndex;
  const screen = screens[targetIndex];
  screenRoot.className = `screen screen--${screen.id}`;
  screenRoot.innerHTML = '';

  const render = screenRenderers[screen.id];
  if (render) {
    render();
  }

  updateNavigationState();
}

function updateNavigationState() {
  prevButton.disabled = currentScreenIndex === 0;
  nextButton.disabled = currentScreenIndex === screens.length - 1;
  screenButtonsContainer.querySelectorAll('.control-button').forEach((button) => {
    button.classList.toggle('is-active', button.dataset.screenId === screens[currentScreenIndex].id);
  });
}

const screenRenderers = {
  attract: renderAttract,
  catalog: renderCatalog,
  cart: renderCart,
  payment: renderPayment,
  dispense: renderDispense,
  admin: renderAdmin,
};

function renderAttract() {
  const container = document.createElement('div');
  container.className = 'attract';
  const topSellers = products
    .filter((product) => product.tags.includes('popular'))
    .slice(0, 3);

  container.innerHTML = `
    <span class="attract__badge">Always stocked · Always chilled</span>
    <h1 class="attract__title">Fuel your next break</h1>
    <p class="attract__subtitle">Tap the screen to browse hand-picked snacks and drinks.</p>
    <button class="attract__cta" type="button">Start order ▸</button>
    <div class="trending-grid">
      ${topSellers
        .map(
          (product) => `
            <article class="trending-card">
              <strong>${product.name}</strong>
              <span>${product.price.toFixed(2)} USD</span>
              <p>${product.description}</p>
            </article>
          `
        )
        .join('')}
    </div>
  `;

  screenRoot.appendChild(container);

  container.querySelector('.attract__cta').addEventListener('click', () => {
    showScreen('catalog');
    setFlowStatus('Browsing products.');
  });
}

function renderCatalog() {
  const shell = createScreenLayout({
    title: 'What can we get you today?',
    subtitle: 'Tap a product to add it to your pickup queue.',
    pill: `${cart.length} item${cart.length !== 1 ? 's' : ''} ready`,
  });

  const toolbar = document.createElement('div');
  toolbar.className = 'catalog-toolbar';

  const searchWrapper = document.createElement('div');
  searchWrapper.className = 'catalog-search';
  const searchInput = document.createElement('input');
  searchInput.type = 'search';
  searchInput.placeholder = 'Search snacks, drinks, or bundles…';
  searchInput.value = searchTerm;
  searchInput.addEventListener('input', (event) => {
    searchTerm = event.target.value;
    updateCatalogGrid(grid);
  });
  searchWrapper.appendChild(searchInput);

  toolbar.appendChild(searchWrapper);

  const categoriesWrapper = document.createElement('div');
  categoriesWrapper.className = 'catalog-categories';
  categories.forEach((category) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'catalog-category';
    button.textContent = category;
    button.dataset.category = category;
    if (category === activeCategory) button.classList.add('is-active');
    button.addEventListener('click', () => {
      activeCategory = category;
      categoriesWrapper.querySelectorAll('.catalog-category').forEach((btn) => btn.classList.remove('is-active'));
      button.classList.add('is-active');
      updateCatalogGrid(grid);
    });
    categoriesWrapper.appendChild(button);
  });
  toolbar.appendChild(categoriesWrapper);

  shell.body.appendChild(toolbar);

  const scrollArea = document.createElement('div');
  scrollArea.className = 'screen__scroll';
  const grid = document.createElement('div');
  grid.className = 'catalog-grid';
  scrollArea.appendChild(grid);
  shell.body.appendChild(scrollArea);

  updateCatalogGrid(grid);
}

function updateCatalogGrid(grid) {
  grid.innerHTML = '';
  const filtered = products.filter((product) => {
    const matchesCategory = activeCategory === 'All' || product.category === activeCategory;
    const matchesSearch = !searchTerm || product.name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  filtered.forEach((product) => {
    const card = document.createElement('article');
    card.className = 'catalog-card';
    card.innerHTML = `
      <div class="catalog-card__image">${product.category}</div>
      <h3>${product.name}</h3>
      <p>${product.description}</p>
      <div class="catalog-card__meta">
        <span class="catalog-card__price">$${product.price.toFixed(2)}</span>
        ${renderTag(product.tags)}
      </div>
      <div class="catalog-card__cta">
        <span class="catalog-card__stock">${product.stock} in stock</span>
        <button type="button" data-product="${product.id}">Add</button>
      </div>
    `;
    const addButton = card.querySelector('button');
    addButton.addEventListener('click', () => {
      addToCart(product.id);
      setFlowStatus(`${product.name} added to cart.`);
    });
    grid.appendChild(card);
  });
}

function renderTag(tags) {
  if (!tags || tags.length === 0) return '';
  const tagClass = tags.includes('fresh') ? 'tag tag--fresh' : 'tag tag--popular';
  const label = tags.includes('fresh') ? 'Chilled' : 'Top pick';
  return `<span class="${tagClass}">${label}</span>`;
}

function renderCart() {
  const shell = createScreenLayout({
    title: 'Review your picks',
    subtitle: 'Adjust quantities or add extras before checkout.',
    pill: cart.length ? `${cart.length} item${cart.length !== 1 ? 's' : ''} in cart` : 'Cart empty',
  });

  const scrollArea = document.createElement('div');
  scrollArea.className = 'screen__scroll';

  if (!cart.length) {
    const emptyState = document.createElement('div');
    emptyState.className = 'cart-summary';
    emptyState.innerHTML = `
      <h3>Your cart is empty</h3>
      <p>Browse the catalog to add snacks, drinks, or bundles.</p>
      <div class="checkout-actions">
        <button class="primary" type="button">Browse catalog</button>
      </div>
    `;
    emptyState.querySelector('button').addEventListener('click', () => showScreen('catalog'));
    scrollArea.appendChild(emptyState);
  } else {
    const itemsList = document.createElement('div');
    itemsList.className = 'cart-summary';

    const list = document.createElement('div');
    list.className = 'cart-items';

    cart.forEach((item) => {
      const line = document.createElement('div');
      line.className = 'cart-item';
      line.innerHTML = `
        <div class="cart-item__details">
          <span class="cart-item__name">${item.name}</span>
          <span class="cart-item__meta">$${item.price.toFixed(2)} each • ${item.stock} in stock</span>
        </div>
        <div class="cart-item__qty">
          <button class="qty-button" data-direction="down" aria-label="Decrease quantity">−</button>
          <span>${item.quantity}</span>
          <button class="qty-button" data-direction="up" aria-label="Increase quantity">+</button>
        </div>
        <strong>$${(item.price * item.quantity).toFixed(2)}</strong>
      `;

      const [down, , up] = line.querySelectorAll('button');
      down.addEventListener('click', () => updateCartQuantity(item.id, item.quantity - 1));
      up.addEventListener('click', () => updateCartQuantity(item.id, item.quantity + 1));

      list.appendChild(line);
    });

    itemsList.appendChild(list);

    const totals = document.createElement('div');
    totals.className = 'payment-summary';
    const subtotal = calculateCartTotal();
    const tax = subtotal * 0.07;
    const total = subtotal + tax;
    totals.innerHTML = `
      <div class="payment-summary__row"><span>Subtotal</span><span>$${subtotal.toFixed(2)}</span></div>
      <div class="payment-summary__row"><span>Local tax</span><span>$${tax.toFixed(2)}</span></div>
      <div class="payment-summary__row payment-summary__total"><span>Total due</span><span>$${total.toFixed(2)}</span></div>
    `;
    itemsList.appendChild(totals);

    const actions = document.createElement('div');
    actions.className = 'checkout-actions';
    const addMore = document.createElement('button');
    addMore.className = 'secondary';
    addMore.type = 'button';
    addMore.textContent = 'Add more items';
    addMore.addEventListener('click', () => showScreen('catalog'));

    const checkout = document.createElement('button');
    checkout.className = 'primary';
    checkout.type = 'button';
    checkout.textContent = 'Proceed to payment';
    checkout.addEventListener('click', () => showScreen('payment'));

    actions.append(addMore, checkout);
    itemsList.appendChild(actions);
    scrollArea.appendChild(itemsList);
  }

  shell.body.appendChild(scrollArea);
}

function renderPayment() {
  const subtotal = calculateCartTotal();
  const tax = subtotal * 0.07;
  const total = subtotal + tax;
  const shell = createScreenLayout({
    title: 'Choose a payment method',
    subtitle: 'Tap to pay instantly. Digital receipts are sent to your email.',
    pill: `Total $${total.toFixed(2)}`,
  });

  const methods = [
    { id: 'tap', label: 'Tap to pay', description: 'Contactless cards & NFC wallets' },
    { id: 'mobile', label: 'Mobile wallet', description: 'Apple Pay, Google Pay, Samsung Pay' },
    { id: 'account', label: 'Company account', description: 'Bill to your team plan' },
    { id: 'qr', label: 'Scan QR', description: 'Pay with the PiVend mobile app' },
  ];

  const methodGrid = document.createElement('div');
  methodGrid.className = 'payment-methods';

  methods.forEach((method) => {
    const card = document.createElement('button');
    card.type = 'button';
    card.className = 'payment-method';
    card.innerHTML = `
      <span class="payment-method__label">${method.label}</span>
      <span class="payment-method__description">${method.description}</span>
    `;
    card.addEventListener('click', () => completePayment(method));
    methodGrid.appendChild(card);
  });

  const summary = document.createElement('div');
  summary.className = 'payment-summary';
  summary.innerHTML = `
    <div class="payment-summary__row"><span>Subtotal</span><span>$${subtotal.toFixed(2)}</span></div>
    <div class="payment-summary__row"><span>Tax (7%)</span><span>$${tax.toFixed(2)}</span></div>
    <div class="payment-summary__row payment-summary__total"><span>Charged now</span><span>$${total.toFixed(2)}</span></div>
  `;

  shell.body.append(methodGrid, summary);
}

function renderDispense() {
  const shell = createScreenLayout({
    title: 'Dispensing in progress',
    subtitle: 'Stand by as the locker opens and your order is released.',
    pill: lastOrder ? `Order #${lastOrder.id}` : undefined,
  });

  const panel = document.createElement('div');
  panel.className = 'dispense-panel';

  if (!lastOrder) {
    panel.innerHTML = `
      <h2>No active order</h2>
      <p>Select items and complete payment to start dispensing.</p>
      <button type="button" class="attract__cta">Browse catalog</button>
    `;
    panel.querySelector('button').addEventListener('click', () => showScreen('catalog'));
    shell.body.appendChild(panel);
    return;
  }

  panel.innerHTML = `
    <h2>Your order is on the way!</h2>
    <p>${lastOrder.items.length} item${lastOrder.items.length !== 1 ? 's' : ''} • $${lastOrder.total.toFixed(2)} charged</p>
    <div class="dispense-progress">
      <div class="dispense-progress__bar" style="width: ${dispensingProgress}%"></div>
    </div>
    <div class="dispense-tips">
      <span id="dispense-status">Preparing locker…</span>
      <span>Hold the door handle and retrieve items once the light turns green.</span>
    </div>
  `;

  shell.body.appendChild(panel);

  const bar = panel.querySelector('.dispense-progress__bar');
  const status = panel.querySelector('#dispense-status');
  startDispenseCountdown(bar, status);
}

function renderAdmin() {
  const shell = createScreenLayout({
    title: 'Operational overview',
    subtitle: 'Live stats sync automatically to the remote dashboard.',
    pill: `Uptime ${analyticsSnapshot.uptime}`,
  });

  const grid = document.createElement('div');
  grid.className = 'admin-grid';

  const metricsCard = document.createElement('div');
  metricsCard.className = 'kpi-card';
  metricsCard.innerHTML = `
    <span>Revenue today</span>
    <strong>$${analyticsSnapshot.salesToday.toFixed(2)}</strong>
    <span>${analyticsSnapshot.transactions} transactions</span>
  `;

  const speedCard = document.createElement('div');
  speedCard.className = 'kpi-card';
  speedCard.innerHTML = `
    <span>Average vend time</span>
    <strong>${analyticsSnapshot.avgVendTime}s</strong>
    <span>Across last 20 orders</span>
  `;

  const chartCard = document.createElement('div');
  chartCard.className = 'kpi-card';
  chartCard.innerHTML = '<span>Sales by hour</span>';
  const chartBars = document.createElement('div');
  chartBars.className = 'chart-bars';
  const max = Math.max(...analyticsSnapshot.salesByHour);
  analyticsSnapshot.salesByHour.forEach((value, index) => {
    const bar = document.createElement('div');
    bar.className = 'chart-bar';
    bar.style.height = `${Math.round((value / max) * 100)}%`;
    bar.innerHTML = `<span>${value}</span>`;
    chartBars.appendChild(bar);
  });
  chartCard.appendChild(chartBars);

  const alertsCard = document.createElement('div');
  alertsCard.className = 'alert-card';
  alertsCard.innerHTML = '<h3>Restock priorities</h3>';
  analyticsSnapshot.lowStock.forEach((item) => {
    const line = document.createElement('div');
    line.className = 'alert-card__item';
    line.innerHTML = `<span>${item.name}</span><span>${item.remaining} left</span>`;
    alertsCard.appendChild(line);
  });

  grid.append(metricsCard, speedCard, chartCard, alertsCard);

  const telemetryCard = document.createElement('div');
  telemetryCard.className = 'alert-card';
  telemetryCard.innerHTML = `
    <h3>Cabinet telemetry</h3>
    <div class="alert-card__item"><span>Temperature</span><span>${analyticsSnapshot.telemetry.temperature.toFixed(1)}°C</span></div>
    <div class="alert-card__item"><span>Humidity</span><span>${analyticsSnapshot.telemetry.humidity}%</span></div>
    <div class="alert-card__item"><span>Door status</span><span>${analyticsSnapshot.telemetry.doorOpen ? 'Open' : 'Closed'}</span></div>
  `;

  const scrollArea = document.createElement('div');
  scrollArea.className = 'screen__scroll';
  scrollArea.append(grid, telemetryCard);
  shell.body.appendChild(scrollArea);
}

function createScreenLayout({ title, subtitle, pill }) {
  const content = document.createElement('div');
  content.className = 'screen-content';

  const header = document.createElement('div');
  header.className = 'screen__header';

  const heading = document.createElement('div');
  const titleEl = document.createElement('h1');
  titleEl.className = 'screen__title';
  titleEl.textContent = title;
  heading.appendChild(titleEl);
  if (subtitle) {
    const subtitleEl = document.createElement('p');
    subtitleEl.className = 'screen__subtitle';
    subtitleEl.textContent = subtitle;
    heading.appendChild(subtitleEl);
  }
  header.appendChild(heading);

  if (pill) {
    const pillEl = document.createElement('span');
    pillEl.className = 'screen__pill';
    pillEl.textContent = pill;
    header.appendChild(pillEl);
  }

  const body = document.createElement('div');
  body.className = 'screen__body';

  content.append(header, body);
  screenRoot.appendChild(content);
  return { content, body };
}

function addToCart(productId) {
  const product = products.find((item) => item.id === productId);
  if (!product) return;
  const existing = cart.find((item) => item.id === productId);
  if (existing) {
    existing.quantity = Math.min(existing.quantity + 1, product.stock);
  } else {
    cart.push({ ...product, quantity: 1 });
  }
  updateCartIndicator();
}

function updateCartQuantity(productId, quantity) {
  const item = cart.find((entry) => entry.id === productId);
  if (!item) return;
  if (quantity <= 0) {
    cart = cart.filter((entry) => entry.id !== productId);
  } else {
    const max = products.find((product) => product.id === productId)?.stock ?? quantity;
    item.quantity = Math.min(quantity, max);
  }
  updateCartIndicator();
  showScreen('cart');
}

function calculateCartTotal() {
  return cart.reduce((total, item) => total + item.price * item.quantity, 0);
}

function completePayment(method) {
  if (!cart.length) {
    setFlowStatus('Cart empty. Add products before paying.');
    showScreen('catalog');
    return;
  }

  const subtotal = calculateCartTotal();
  const tax = subtotal * 0.07;
  const total = subtotal + tax;
  lastOrder = {
    id: Math.floor(Math.random() * 9000) + 1000,
    method,
    items: cart.map((item) => ({ id: item.id, name: item.name, quantity: item.quantity })),
    total,
  };

  cart = [];
  updateCartIndicator();
  setFlowStatus(`${method.label} accepted. Dispensing order #${lastOrder.id}.`);
  showScreen('dispense');
}

function startDispenseCountdown(bar, status) {
  if (!lastOrder) return;
  clearInterval(dispenseTimer);
  dispensingProgress = 0;
  bar.style.width = '0%';
  status.textContent = 'Preparing locker…';

  const stages = [
    'Preparing locker…',
    'Unlocking compartment…',
    'Releasing product…',
    'Door ready – please collect.',
  ];
  let stageIndex = 0;

  dispenseTimer = setInterval(() => {
    dispensingProgress += 12;
    if (dispensingProgress >= 100) {
      dispensingProgress = 100;
      bar.style.width = '100%';
      status.textContent = 'Dispense complete. Close the door when finished.';
      clearInterval(dispenseTimer);
      setFlowStatus(`Order #${lastOrder.id} ready for pickup.`);
      return;
    }

    bar.style.width = `${dispensingProgress}%`;
    if (dispensingProgress >= 25 * (stageIndex + 1) && stageIndex < stages.length - 1) {
      stageIndex += 1;
      status.textContent = stages[stageIndex];
    }
  }, 600);
}

function updateCartIndicator() {
  const items = cart.reduce((total, item) => total + item.quantity, 0);
  const total = calculateCartTotal();
  cartIndicator.textContent = `${items} item${items !== 1 ? 's' : ''} • $${total.toFixed(2)}`;
}

function updateDateTime() {
  const now = new Date();
  const hours = now.getHours();
  const minutes = now.getMinutes().toString().padStart(2, '0');
  statusTime.textContent = `${hours}:${minutes}`;
  statusDay.textContent = now.toLocaleDateString(undefined, {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  });
}

function updateEnvironmentReadings() {
  const delta = Math.sin(Date.now() / 60000) * 0.4;
  const humidityDelta = Math.cos(Date.now() / 70000) * 1.2;
  analyticsSnapshot.telemetry.temperature = 4.2 + delta;
  analyticsSnapshot.telemetry.humidity = Math.round(42 + humidityDelta);
  const doorEvent = Math.random() < 0.015;
  analyticsSnapshot.telemetry.doorOpen = doorEvent ? !analyticsSnapshot.telemetry.doorOpen : analyticsSnapshot.telemetry.doorOpen;
  statusEnvironment.textContent = `${analyticsSnapshot.telemetry.temperature.toFixed(1)}°C • ${analyticsSnapshot.telemetry.humidity}% RH`;
  statusDoor.textContent = analyticsSnapshot.telemetry.doorOpen ? 'Door open' : 'Door closed';
}

function updateNetworkStatus() {
  const strength = ['LTE', '5G', 'LTE'];
  const rssi = Math.floor(-60 - Math.random() * 15);
  statusNetwork.textContent = `${strength[Math.floor(Math.random() * strength.length)]} • ${rssi} dBm`;
}

function setFlowStatus(message) {
  flowStatus.textContent = message;
}

function resetExperience() {
  cart = [];
  activeCategory = 'All';
  searchTerm = '';
  lastOrder = null;
  dispensingProgress = 0;
  clearInterval(dispenseTimer);
  dispenseTimer = null;
  updateCartIndicator();
  setFlowStatus('Experience reset. Ready to explore.');
}

function runGuidedFlow() {
  stopGuidedFlow();
  resetExperience();
  setFlowStatus('Guided flow: attracting customers…');
  showScreen('attract');

  const steps = [
    () => {
      setFlowStatus('Guided flow: browsing popular products.');
      showScreen('catalog');
    },
    () => {
      showScreen('catalog');
      addToCart('sparkling-citrus');
      setFlowStatus('Added Sparkling Citrus Fizz to the cart.');
    },
    () => {
      showScreen('cart');
      setFlowStatus('Reviewing selections before checkout.');
    },
    () => {
      showScreen('payment');
      setFlowStatus('Selecting tap-to-pay.');
    },
    () => {
      completePayment({ id: 'tap', label: 'Tap to pay' });
    },
  ];

  let delay = 2000;
  steps.forEach((step) => {
    const timer = setTimeout(step, delay);
    demoTimers.push(timer);
    delay += 2600;
  });
}

function stopGuidedFlow() {
  demoTimers.forEach((timer) => clearTimeout(timer));
  demoTimers = [];
}

init();
