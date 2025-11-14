// API Base URL
const API_BASE = '/api';

// State Management
let currentPokemon = null;
let currentPokemonId = null;
let allPokemon = [];
let searchResults = [];
let viewHistory = [];

// Type Colors (matching the Python version)
const TYPE_COLORS = {
    "normal": "#A8A77A",
    "fire": "#EE8130",
    "water": "#6390F0",
    "electric": "#F7D02C",
    "grass": "#7AC74C",
    "ice": "#96D9D6",
    "fighting": "#C22E28",
    "poison": "#A33EA1",
    "ground": "#E2BF65",
    "flying": "#A98FF3",
    "psychic": "#F95587",
    "bug": "#A6B91A",
    "rock": "#B6A136",
    "ghost": "#735797",
    "dragon": "#6F35FC",
    "dark": "#705746",
    "steel": "#B7B7CE",
    "fairy": "#D685AD",
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadAllPokemon();
});

function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');

    if (searchInput) {
        // Ensure input is focusable and clickable
        searchInput.setAttribute('tabindex', '0');
        searchInput.style.pointerEvents = 'auto';
        searchInput.removeAttribute('readonly');
        searchInput.removeAttribute('disabled');
        
        // Multiple event listeners for better compatibility with webview
        searchInput.addEventListener('keypress', (e) => {
            e.stopPropagation();
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch();
            }
        });
        
        searchInput.addEventListener('keydown', (e) => {
            e.stopPropagation();
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch();
            }
        });
        
        searchInput.addEventListener('input', (e) => {
            e.stopPropagation();
        });
        
        searchInput.addEventListener('click', (e) => {
            e.stopPropagation();
            e.preventDefault();
            searchInput.focus();
            // Force cursor to end of text
            if (searchInput.value) {
                searchInput.setSelectionRange(searchInput.value.length, searchInput.value.length);
            }
        });
        
        searchInput.addEventListener('mousedown', (e) => {
            e.stopPropagation();
            searchInput.focus();
        });
        
        searchInput.addEventListener('focus', (e) => {
            e.stopPropagation();
        });
        
        // Make sure input is always interactive
        searchInput.addEventListener('touchstart', (e) => {
            e.stopPropagation();
            searchInput.focus();
        });
    }

    if (searchBtn) {
        searchBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            performSearch();
        });
        searchBtn.addEventListener('mousedown', (e) => {
            e.stopPropagation();
        });
    }
    
    // Mark input as having listeners set up
    if (searchInput) {
        searchInput.setAttribute('data-listeners-setup', 'true');
    }
}

// API Functions
async function loadAllPokemon() {
    try {
        const response = await fetch(`${API_BASE}/pokemon`);
        allPokemon = await response.json();
    } catch (error) {
        console.error('Error loading Pokemon:', error);
        showError('Failed to load Pokemon data');
    }
}

async function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    
    if (!query) {
        return;
    }

    try {
        showView('searchResultsView');
        const resultsDiv = document.getElementById('searchResults');
        resultsDiv.innerHTML = '<div class="loading">SEARCHING...</div>';

        const response = await fetch(`${API_BASE}/pokemon/search/${encodeURIComponent(query)}`);
        searchResults = await response.json();

        if (searchResults.length === 0) {
            resultsDiv.innerHTML = '<div class="loading">NO POKÉMON FOUND</div>';
            return;
        }

        displaySearchResults(searchResults);
    } catch (error) {
        console.error('Error searching:', error);
        showError('Search failed');
    }
}

async function loadPokemonDetail(pokemonId) {
    try {
        const response = await fetch(`${API_BASE}/pokemon/${pokemonId}`);
        const pokemon = await response.json();
        currentPokemon = pokemon;
        currentPokemonId = pokemonId;
        displayPokemonDetail(pokemon);
        showView('detailView');
    } catch (error) {
        console.error('Error loading Pokemon detail:', error);
        showError('Failed to load Pokemon details');
    }
}

// View Management
function showView(viewId) {
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });
    document.getElementById(viewId).classList.add('active');
    viewHistory.push(viewId);
    
    // If showing landing view, ensure search input is ready (for webview compatibility)
    if (viewId === 'landingView') {
        setTimeout(() => {
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.removeAttribute('readonly');
                searchInput.removeAttribute('disabled');
                searchInput.style.pointerEvents = 'auto';
                // Re-enable if needed
                if (!searchInput.hasAttribute('data-listeners-setup')) {
                    setupEventListeners();
                }
            }
        }, 50);
    }
}

function showLanding() {
    showView('landingView');
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.value = '';
        // Re-focus and re-setup if needed for webview
        setTimeout(() => {
            if (searchInput) {
                searchInput.removeAttribute('readonly');
                searchInput.removeAttribute('disabled');
                searchInput.style.pointerEvents = 'auto';
                // Re-setup event listeners for webview compatibility
                if (!searchInput.hasAttribute('data-listeners-setup')) {
                    setupEventListeners();
                }
            }
        }, 100);
    }
    viewHistory = [];
}

function goBack() {
    if (viewHistory.length > 1) {
        viewHistory.pop();
        const previousView = viewHistory[viewHistory.length - 1];
        showView(previousView);
    } else {
        showLanding();
    }
}

// Display Functions
function displaySearchResults(results) {
    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.innerHTML = '';

    results.forEach(pokemon => {
        const card = createPokemonCard(pokemon);
        resultsDiv.appendChild(card);
    });
}

function createPokemonCard(pokemon) {
    const card = document.createElement('div');
    card.className = 'pokemon-card';
    card.onclick = () => loadPokemonDetail(pokemon.id);

    const img = document.createElement('img');
    img.src = pokemon.official_artwork_url || pokemon.sprite_url || '';
    img.alt = pokemon.name;
    img.onerror = function() {
        this.src = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${pokemon.id}.png`;
    };

    const name = document.createElement('div');
    name.className = 'pokemon-name';
    name.textContent = `#${pokemon.id} ${pokemon.name.charAt(0).toUpperCase() + pokemon.name.slice(1)}`;

    const types = document.createElement('div');
    types.className = 'type-badges';
    
    if (pokemon.primary_type) {
        const type1 = createTypeBadge(pokemon.primary_type);
        types.appendChild(type1);
    }
    
    if (pokemon.secondary_type && pokemon.secondary_type !== pokemon.primary_type) {
        const type2 = createTypeBadge(pokemon.secondary_type);
        types.appendChild(type2);
    }

    card.appendChild(img);
    card.appendChild(name);
    card.appendChild(types);

    return card;
}

function createTypeBadge(typeName) {
    const badge = document.createElement('span');
    badge.className = 'type-badge';
    badge.textContent = typeName.toUpperCase();
    badge.style.backgroundColor = TYPE_COLORS[typeName.toLowerCase()] || '#888888';
    return badge;
}

function displayPokemonDetail(pokemon) {
    const detailDiv = document.getElementById('pokemonDetail');
    
    const html = `
        <div class="detail-main">
            <div class="detail-image">
                <img src="${pokemon.official_artwork_url || pokemon.sprite_url || ''}" 
                     alt="${pokemon.name}"
                     onerror="this.src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${pokemon.id}.png'">
            </div>
            <div class="detail-info">
                <h2>#${pokemon.id} ${pokemon.name.charAt(0).toUpperCase() + pokemon.name.slice(1)}</h2>
                <div class="info-row">
                    <span class="info-label">SPECIES:</span>
                    <span>${pokemon.species || 'Unknown'}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">GENERATION:</span>
                    <span>${pokemon.generation || 'Unknown'}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">TYPE(S):</span>
                    <div class="type-badges" style="margin-top: 5px;">
                        ${pokemon.primary_type ? createTypeBadgeHTML(pokemon.primary_type) : ''}
                        ${pokemon.secondary_type && pokemon.secondary_type !== pokemon.primary_type ? createTypeBadgeHTML(pokemon.secondary_type) : ''}
                    </div>
                </div>
                <div class="info-row">
                    <span class="info-label">HEIGHT:</span>
                    <span>${pokemon.height_m || 'Unknown'} m</span>
                </div>
                <div class="info-row">
                    <span class="info-label">WEIGHT:</span>
                    <span>${pokemon.weight_kg || 'Unknown'} kg</span>
                </div>
            </div>
        </div>

        <!-- Tabs -->
        <div class="tabs-container">
            <div class="tabs">
                <button class="tab-button active" onclick="switchTab('general', this)">GENERAL</button>
                <button class="tab-button" onclick="switchTab('more-info', this)">MORE INFO</button>
            </div>
            
            <!-- General Tab Content -->
            <div id="tab-general" class="tab-content active">
                <div class="detail-section">
                    <h3>BASE STATS</h3>
                    <div class="stats-grid">
                        ${createStatHTML('HP', pokemon.hp, 255)}
                        ${createStatHTML('ATTACK', pokemon.attack, 255)}
                        ${createStatHTML('DEFENSE', pokemon.defense, 255)}
                        ${createStatHTML('SP. ATK', pokemon.special_attack, 255)}
                        ${createStatHTML('SP. DEF', pokemon.special_defense, 255)}
                        ${createStatHTML('SPEED', pokemon.speed, 255)}
                        ${createStatHTML('TOTAL', pokemon.base_stat_total, 780)}
                    </div>
                </div>

                ${pokemon.flavor_text ? `
                <div class="detail-section">
                    <h3>POKÉDEX ENTRY</h3>
                    <p>${pokemon.flavor_text}</p>
                </div>
                ` : ''}
            </div>
            
            <!-- More Info Tab Content -->
            <div id="tab-more-info" class="tab-content">
                ${buildEvolutionChain(pokemon)}

                <div class="detail-section">
                    <h3>DAMAGE TAKEN</h3>
                    <div class="damage-section">
                        ${createDamageCategory('WEAK TO (2×)', parseListField(pokemon.double_damage_from))}
                        ${createDamageCategory('RESISTS (½×)', parseListField(pokemon.half_damage_from))}
                        ${createDamageCategory('IMMUNE TO (0×)', parseListField(pokemon.no_damage_from))}
                    </div>
                </div>
            </div>
        </div>
    `;

    detailDiv.innerHTML = html;
}

function switchTab(tabName, buttonElement) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // Show selected tab content
    document.getElementById(`tab-${tabName}`).classList.add('active');
    
    // Add active class to clicked button
    if (buttonElement) {
        buttonElement.classList.add('active');
    } else {
        // Fallback: find button by text content
        document.querySelectorAll('.tab-button').forEach(button => {
            if (button.textContent.trim() === (tabName === 'general' ? 'GENERAL' : 'MORE INFO')) {
                button.classList.add('active');
            }
        });
    }
}

function createTypeBadgeHTML(typeName) {
    const color = TYPE_COLORS[typeName.toLowerCase()] || '#888888';
    return `<span class="type-badge" style="background-color: ${color};">${typeName.toUpperCase()}</span>`;
}

function createStatHTML(label, value, max) {
    if (!value) return '';
    const percentage = Math.min((value / max) * 100, 100);
    return `
        <div class="stat-item">
            <span><strong>${label}:</strong> ${value}</span>
            <div class="stat-bar">
                <div class="stat-bar-fill" style="width: ${percentage}%"></div>
            </div>
        </div>
    `;
}

function parseListField(value) {
    if (!value || value === '' || value === 'nan') return [];
    if (typeof value === 'string') {
        return value.split(',').map(x => x.trim().toLowerCase()).filter(x => x);
    }
    return [];
}

function createDamageCategory(label, types) {
    const badges = types.length > 0 
        ? types.map(type => createTypeBadgeHTML(type)).join('')
        : '<span style="opacity: 0.5;">None</span>';
    
    return `
        <div class="damage-category">
            <h4>${label}</h4>
            <div class="damage-types">${badges}</div>
        </div>
    `;
}

function buildEvolutionChain(pokemon) {
    if (!allPokemon.length) return '';

    // Build evolution chain
    const chain = buildFullEvoChain(pokemon.id);
    
    if (chain.length <= 1) {
        return '<div class="detail-section"><h3>EVOLUTION CHAIN</h3><p>This Pokémon does not evolve.</p></div>';
    }

    let html = '<div class="detail-section"><h3>EVOLUTION CHAIN</h3><div class="evolution-chain">';
    
    for (let i = 0; i < chain.length; i++) {
        const stage = chain[i];
        
        html += '<div class="evolution-stage">';
        
        for (const pokemonId of stage) {
            const pkmn = allPokemon.find(p => p.id === pokemonId);
            if (pkmn) {
                const isCurrent = pokemonId === pokemon.id;
                html += `
                    <div class="evolution-pokemon ${isCurrent ? 'current' : ''}" onclick="loadPokemonDetail(${pokemonId})">
                        <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${pokemonId}.png" 
                             alt="${pkmn.name}">
                        <div>#${pokemonId}</div>
                    </div>
                `;
            }
        }
        
        html += '</div>';
        
        if (i < chain.length - 1) {
            html += '<div class="evolution-arrow">→</div>';
        }
    }
    
    html += '</div></div>';
    return html;
}

function buildFullEvoChain(currentId) {
    // Find the earliest ancestor
    let ancestor = currentId;
    const visited = new Set();
    
    while (true) {
        const pokemon = allPokemon.find(p => p.id === ancestor);
        if (!pokemon) break;
        
        const prevId = safeId(pokemon.previous_evolution_id);
        if (!prevId || visited.has(prevId)) break;
        
        visited.add(prevId);
        ancestor = prevId;
    }
    
    // Build chain forward
    const chain = [];
    let stage = [ancestor];
    visited.clear();
    
    while (stage.length > 0) {
        chain.push([...stage]);
        const nextStage = [];
        
        for (const pid of stage) {
            const pokemon = allPokemon.find(p => p.id === pid);
            if (!pokemon) continue;
            
            const nextIds = parseListField(pokemon.next_evolution_id)
                .map(id => safeId(id))
                .filter(id => id && !visited.has(id));
            
            for (const nid of nextIds) {
                nextStage.push(nid);
                visited.add(nid);
            }
        }
        
        stage = nextStage;
    }
    
    return chain;
}

function safeId(value) {
    if (!value || value === '' || value === 'nan') return null;
    if (typeof value === 'number') {
        return isNaN(value) ? null : Math.floor(value);
    }
    if (typeof value === 'string') {
        const trimmed = value.trim();
        if (trimmed === '') return null;
        const num = parseFloat(trimmed);
        return isNaN(num) ? null : Math.floor(num);
    }
    return null;
}

// Navigation Functions
function navigatePokemon(direction) {
    if (!currentPokemonId || !allPokemon.length) return;
    
    const currentIndex = allPokemon.findIndex(p => p.id === currentPokemonId);
    if (currentIndex === -1) return;
    
    let newIndex;
    if (direction === 'next') {
        newIndex = (currentIndex + 1) % allPokemon.length;
    } else {
        newIndex = (currentIndex - 1 + allPokemon.length) % allPokemon.length;
    }
    
    loadPokemonDetail(allPokemon[newIndex].id);
}

function selectPokemon() {
    // Check if we're on the detail view
    const detailView = document.getElementById('detailView');
    if (detailView && detailView.classList.contains('active')) {
        // Cycle through tabs on detail page
        cycleTabs();
    } else {
        // If on landing page with search text, perform search
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            const query = searchInput.value.trim();
            if (query) {
                performSearch();
            }
        }
    }
}

function cycleTabs() {
    // Get all tab buttons and contents
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    if (tabButtons.length === 0 || tabContents.length === 0) {
        return; // Not on detail page
    }
    
    // Find current active tab
    let currentIndex = -1;
    tabButtons.forEach((btn, index) => {
        if (btn.classList.contains('active')) {
            currentIndex = index;
        }
    });
    
    // Cycle to next tab
    const nextIndex = (currentIndex + 1) % tabButtons.length;
    
    // Remove active from all
    tabButtons.forEach(btn => btn.classList.remove('active'));
    tabContents.forEach(content => content.classList.remove('active'));
    
    // Activate next tab
    tabButtons[nextIndex].classList.add('active');
    tabContents[nextIndex].classList.add('active');
}

function triggerSearch() {
    // Always go to landing/search page
    showLanding();
    setTimeout(() => {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.focus();
        }
    }, 100);
}

function showError(message) {
    const screenContent = document.getElementById('screenContent');
    screenContent.innerHTML = `<div class="loading" style="color: #f00;">ERROR: ${message}</div>`;
    setTimeout(() => {
        showLanding();
    }, 2000);
}

