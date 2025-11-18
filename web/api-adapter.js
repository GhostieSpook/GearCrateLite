// GearCrate API Abstraction Layer
// Works with pywebview AND browser mode

const isPywebview = typeof pywebview !== 'undefined';
const apiBase = '/api';

// API call helper
async function apiCall(method, data = {}) {
    if (isPywebview) {
        // pywebview mode
        return await pywebview.api[method](...Object.values(data));
    } else {
        // Browser mode - HTTP API
        const response = await fetch(`${apiBase}/${method}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        return await response.json();
    }
}

// API Wrapper
const api = {
    // Snake_case (Python style)
    search_items_local: (query) => apiCall('search_items_local', { query }),
    search_items_cstone: (query) => apiCall('search_items_cstone', { query }),
    add_item: (name, item_type, image_url, notes, initial_count) => 
        apiCall('add_item', { name, item_type, image_url, notes, initial_count }),
    get_item: (name) => apiCall('get_item', { name }),
    update_count: (name, count) => apiCall('update_count', { name, count }),
    update_notes: (name, notes) => apiCall('update_notes', { name, notes }),
    delete_item: (name) => apiCall('delete_item', { name }),
    clear_inventory: () => apiCall('clear_inventory', {}),
    delete_all_items: () => apiCall('delete_all_items', {}),
    clear_cache: () => apiCall('clear_cache', {}),
    get_stats: () => apiCall('get_stats', {}),
    get_categories: () => apiCall('get_categories', {}),
    
    // camelCase (JavaScript style)
    searchItemsLocal: (query) => apiCall('search_items_local', { query }),
    searchItemsCstone: (query) => apiCall('search_items_cstone', { query }),
    addItem: (name, item_type, image_url, notes, initial_count) => 
        apiCall('add_item', { name, item_type, image_url, notes, initial_count }),
    getItem: (name) => apiCall('get_item', { name }),
    updateCount: (name, count) => apiCall('update_count', { name, count }),
    updateNotes: (name, notes) => apiCall('update_notes', { name, notes }),
    deleteItem: (name) => apiCall('delete_item', { name }),
    clearInventory: () => apiCall('clear_inventory', {}),
    deleteAllItems: () => apiCall('delete_all_items', {}),
    clearCache: () => apiCall('clear_cache', {}),
    getStats: () => apiCall('get_stats', {}),
    getCategories: () => apiCall('get_categories', {})
};

console.log('GearCrate API loaded. Available methods:', Object.keys(api).slice(0, 15));
