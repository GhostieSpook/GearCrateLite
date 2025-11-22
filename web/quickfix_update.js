// SCHNELLE MINIMALE LÖSUNG - Ersetze nur diese eine Funktion in app.js
// Diese Version macht nur die wichtigste Optimierung: Kein vollständiges Reload

async function quickUpdateCount(itemName, delta) {
    try {
        const item = await api.get_item(itemName);
        if (!item) {
            console.error('Item not found:', itemName);
            return;
        }
        
        const newCount = Math.max(0, item.count + delta);
        await api.update_count(itemName, newCount);
        
        // Clear cache
        searchCache = {};
        
        // WICHTIGSTE OPTIMIERUNG: Nur wenn wirklich nötig neu laden
        // Fall 1: Item wird ins Inventar hinzugefügt (0 -> 1+)
        if (item.count === 0 && newCount > 0) {
            await loadInventory();
            await loadStats();
        }
        // Fall 2: Item wird aus Inventar entfernt (1+ -> 0) 
        else if (item.count > 0 && newCount === 0) {
            await loadInventory();
            await loadStats();
        }
        // Fall 3: Nur Count-Änderung - KEIN RELOAD, nur UI update
        else {
            // Update im Inventar-Grid
            const inventoryItem = document.querySelector(`.inventory-item[data-name="${CSS.escape(itemName)}"]`);
            if (inventoryItem) {
                const countElement = inventoryItem.querySelector('.count');
                if (countElement) {
                    countElement.textContent = `${newCount}x`;
                }
            }
            
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
                    
                    // Minus-Button Status
                    const minusBtn = result.querySelector('.search-btn-minus');
                    if (minusBtn) {
                        minusBtn.disabled = newCount === 0;
                        minusBtn.style.opacity = newCount === 0 ? '0.3' : '1';
                        minusBtn.style.cursor = newCount === 0 ? 'not-allowed' : 'pointer';
                    }
                }
            });
            
            // Stats nur verzögert updaten
            setTimeout(() => loadStats(), 500);
        }
        
        // Refresh search results if needed
        const searchInput = document.getElementById('search-input');
        if (searchInput && searchInput.value && searchInput.value.length >= 2) {
            await handleSearch(searchInput.value);
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
    }
}