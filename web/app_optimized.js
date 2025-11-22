// OPTIMIERTE VERSION von quickUpdateCount
// Kopiere diese Funktion in app.js und ersetze die alte quickUpdateCount

async function quickUpdateCount(itemName, delta) {
    try {
        const item = await api.get_item(itemName);
        if (!item) {
            console.error('Item not found:', itemName);
            return;
        }
        
        const oldCount = item.count;
        const newCount = Math.max(0, oldCount + delta);
        
        // Sofort UI aktualisieren (optimistisches Update)
        updateItemUIOptimistic(itemName, newCount);
        
        // Server-Update im Hintergrund
        await api.update_count(itemName, newCount);
        
        // Clear cache für zukünftige Suchen
        searchCache = {};
        
        // OPTIMIERUNG: Nur betroffene Elemente aktualisieren, nicht alles neu laden
        
        // 1. Update im Inventar-Grid (wenn sichtbar)
        const inventoryItem = document.querySelector(`.inventory-item[data-name="${CSS.escape(itemName)}"]`);
        if (inventoryItem) {
            // Wenn count = 0, Item aus Grid entfernen (wenn nicht in "All Items" View)
            if (newCount === 0 && currentCategoryFilter !== '') {
                inventoryItem.style.transition = 'opacity 0.3s';
                inventoryItem.style.opacity = '0';
                setTimeout(() => inventoryItem.remove(), 300);
            } else {
                // Count-Anzeige aktualisieren
                const countElement = inventoryItem.querySelector('.count');
                if (countElement) {
                    countElement.textContent = `${newCount}x`;
                    // Visuelles Feedback
                    countElement.style.animation = 'pulse 0.3s';
                }
            }
        } else if (newCount > 0 && oldCount === 0) {
            // Item wurde neu hinzugefügt - nur dann Inventar neu laden
            await loadInventory();
        }
        
        // 2. Stats asynchron im Hintergrund aktualisieren (ohne await)
        loadStatsDebounced();
        
        // 3. Suchresultate aktualisieren (wenn aktiv)
        const searchInput = document.getElementById('search-input');
        if (searchInput && searchInput.value && searchInput.value.length >= 2) {
            // Lokales Update der Suchergebnisse
            updateSearchResultCount(itemName, newCount);
        }
        
        // Fokus zurücksetzen
        const filterInput = document.getElementById('filter-input');
        if (searchInput && searchInput.value && searchInput.value.length >= 2) {
            searchInput.focus();
            searchInput.setSelectionRange(searchInput.value.length, searchInput.value.length);
        } else if (filterInput && filterInput.value) {
            filterInput.focus();
            filterInput.setSelectionRange(filterInput.value.length, filterInput.value.length);
        } else if (searchInput) {
            searchInput.focus();
        }
    } catch (error) {
        console.error('Error updating count:', error);
        alert(t('errorUpdating'));
        // Bei Fehler: UI zurücksetzen
        await loadInventory();
    }
}

// Hilfsfunktion: Optimistisches UI-Update
function updateItemUIOptimistic(itemName, newCount) {
    // Update in Suchergebnissen
    const searchResults = document.querySelectorAll('.search-result-item');
    searchResults.forEach(result => {
        const nameSpan = result.querySelector('.search-item-name');
        if (nameSpan && nameSpan.textContent === itemName) {
            const countSpan = result.querySelector('.search-item-count');
            if (countSpan) {
                countSpan.textContent = `${newCount}x`;
                countSpan.style.color = newCount > 0 ? '#00d9ff' : '#666';
            }
            
            // Minus-Button deaktivieren wenn count = 0
            const minusBtn = result.querySelector('.search-btn-minus');
            if (minusBtn) {
                minusBtn.disabled = newCount === 0;
                minusBtn.style.opacity = newCount === 0 ? '0.3' : '1';
                minusBtn.style.cursor = newCount === 0 ? 'not-allowed' : 'pointer';
            }
        }
    });
}

// Hilfsfunktion: Lokales Update der Suchergebnis-Counts
function updateSearchResultCount(itemName, newCount) {
    const searchResults = document.querySelectorAll('.search-result-item');
    searchResults.forEach(result => {
        const nameSpan = result.querySelector('.search-item-name');
        if (nameSpan && nameSpan.textContent === itemName) {
            const countSpan = result.querySelector('.search-item-count');
            if (countSpan) {
                countSpan.textContent = `${newCount}x`;
                countSpan.style.color = newCount > 0 ? '#00d9ff' : '#666';
            }
        }
    });
}

// Debounced Stats-Update (max. einmal pro Sekunde)
let statsUpdateTimeout = null;
function loadStatsDebounced() {
    clearTimeout(statsUpdateTimeout);
    statsUpdateTimeout = setTimeout(async () => {
        await loadStats();
    }, 1000);
}

// CSS für Pulse-Animation (füge das zu styles.css hinzu)
/*
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.2); background: #00d9ff; color: #000; }
    100% { transform: scale(1); }
}
*/