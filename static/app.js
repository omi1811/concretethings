// Pure JavaScript (no TypeScript) - Commercial-ready Mix Design Management

// Authentication utilities
const Auth = {
  getToken: () => localStorage.getItem('access_token'),
  getUser: () => JSON.parse(localStorage.getItem('user') || 'null'),
  isAuthenticated: () => !!Auth.getToken(),
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '/static/login.html';
  },
  checkAuth: () => {
    if (!Auth.isAuthenticated()) {
      window.location.href = '/static/login.html';
      return false;
    }
    return true;
  }
};

// API client with JWT authentication
const API = {
  getHeaders: () => {
    const headers = {};
    const token = Auth.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  },
  
  handleResponse: async (response) => {
    if (response.status === 401) {
      // Token expired or invalid
      Auth.logout();
      throw new Error('Authentication required');
    }
    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Request failed' }));
      throw new Error(error.error || 'Request failed');
    }
    return response.json();
  },
  
  list: () => fetch('/api/mix-designs', { 
    headers: API.getHeaders() 
  }).then(API.handleResponse),
  
  create: (formData) => {
    const headers = API.getHeaders();
    // Don't set Content-Type for FormData, browser will set it with boundary
    return fetch('/api/mix-designs', { 
      method: 'POST', 
      headers: headers,
      body: formData 
    }).then(API.handleResponse);
  },
  
  update: (id, formData) => {
    const headers = API.getHeaders();
    return fetch(`/api/mix-designs/${id}`, { 
      method: 'PUT', 
      headers: headers,
      body: formData 
    }).then(API.handleResponse);
  },
  
  delete: (id) => fetch(`/api/mix-designs/${id}`, { 
    method: 'DELETE',
    headers: API.getHeaders()
  }).then(API.handleResponse),
  
  getImage: (id) => `/api/mix-designs/${id}/image`,
};

const el = (id) => document.getElementById(id);

const state = {
  items: [],
  editingId: null,
  search: '',
  imagePreview: null,
};

function toFormData(values) {
  const fd = new FormData();
  Object.entries(values).forEach(([k, v]) => {
    if (v === undefined || v === null || v === '') return;
    // Handle File objects
    if (v instanceof File) {
      fd.append(k, v);
    } else {
      fd.append(k, v);
    }
  });
  return fd;
}

function readForm() {
  const imageFile = el('image').files[0] || null;
  return {
    projectName: el('projectName').value.trim(),
    mixDesignId: el('mixDesignId').value.trim(),
    specifiedStrengthPsi: el('specifiedStrengthPsi').value || 0,
    slumpInches: el('slumpInches').value,
    airContentPercent: el('airContentPercent').value,
    batchVolume: el('batchVolume').value,
    volumeUnit: el('volumeUnit').value || null,
    materials: el('materials').value || null,
    notes: el('notes').value || null,
    document: el('document').files[0] || null,
    image: imageFile,
  };
}

function resetForm() {
  el('id').value = '';
  el('projectName').value = '';
  el('mixDesignId').value = '';
  el('specifiedStrengthPsi').value = '0';
  el('slumpInches').value = '';
  el('airContentPercent').value = '';
  el('batchVolume').value = '';
  el('volumeUnit').value = '';
  el('materials').value = '';
  el('notes').value = '';
  el('document').value = '';
  el('image').value = '';
  state.editingId = null;
  state.imagePreview = null;
  el('form-title').textContent = 'Add New Mix Design';
  el('submit-btn').textContent = 'Add Mix Design';
  el('cancel-btn').style.display = 'none';
  el('image-preview').style.display = 'none';
  el('image-preview').innerHTML = '';
}

function setAlert(msg, type = 'muted') {
  const a = el('alert');
  a.className = type;
  a.textContent = msg || '';
  if (msg) {
    setTimeout(() => setAlert(''), 5000);
  }
}

function render() {
  const tbody = document.querySelector('#table tbody');
  tbody.innerHTML = '';
  const q = state.search.toLowerCase();
  const rows = state.items.filter(i =>
    !q || i.projectName.toLowerCase().includes(q) || i.mixDesignId.toLowerCase().includes(q)
  );
  if (rows.length === 0) {
    const tr = document.createElement('tr');
    const td = document.createElement('td');
    td.colSpan = 9;
    td.innerHTML = '<span class="muted">No mix designs found.</span>';
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }
  rows.forEach(mix => {
    const tr = document.createElement('tr');
    const imageCell = mix.hasImage 
      ? `<img src="${API.getImage(mix.id)}" alt="Mix design" style="width:50px;height:50px;object-fit:cover;border-radius:4px;cursor:pointer" onclick="showImageModal(${mix.id})" />`
      : '<span class="badge">No Image</span>';
    
    tr.innerHTML = `
      <td>${imageCell}</td>
      <td>${escapeHtml(mix.projectName)}</td>
      <td>${escapeHtml(mix.mixDesignId)}</td>
      <td>${mix.specifiedStrengthPsi}</td>
      <td>${mix.slumpInches != null ? Number(mix.slumpInches).toFixed(1) : 'N/A'}</td>
      <td>${mix.airContentPercent != null ? Number(mix.airContentPercent).toFixed(1) : 'N/A'}</td>
      <td>${mix.batchVolume != null ? `${Number(mix.batchVolume).toFixed(2)} ${mix.volumeUnit === 'cubic_yards' ? 'yd³' : (mix.volumeUnit === 'cubic_meters' ? 'm³' : '')}` : 'N/A'}</td>
      <td>${mix.documentName ? `<span class="badge">${escapeHtml(mix.documentName)}</span>` : '<span class="badge">No Document</span>'}</td>
      <td>
        <div class="actions">
          <button class="secondary" data-edit="${mix.id}">Edit</button>
          <button data-delete="${mix.id}">Delete</button>
        </div>
      </td>`;
    tbody.appendChild(tr);
  });
}

function escapeHtml(str) {
  return String(str).replace(/[&<>"]+/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[s]));
}

async function load() {
  try {
    const items = await API.list();
    state.items = items;
    render();
  } catch (err) {
    console.error(err);
    setAlert('Failed to load mix designs.', 'error');
  }
}

// Image preview handler
el('image').addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file && file.type.startsWith('image/')) {
    const reader = new FileReader();
    reader.onload = (evt) => {
      const preview = el('image-preview');
      preview.innerHTML = `<img src="${evt.target.result}" alt="Preview" style="max-width:200px;max-height:200px;border-radius:8px" />`;
      preview.style.display = 'block';
    };
    reader.readAsDataURL(file);
  }
});

// Image modal (fullscreen view)
window.showImageModal = function(id) {
  const modal = document.createElement('div');
  modal.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.9);z-index:9999;display:flex;align-items:center;justify-content:center;cursor:pointer';
  modal.innerHTML = `<img src="${API.getImage(id)}" style="max-width:90%;max-height:90%;border-radius:8px" />`;
  modal.onclick = () => document.body.removeChild(modal);
  document.body.appendChild(modal);
};

// Event listeners
el('mix-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  setAlert('');
  const values = readForm();
  
  // Validation
  if (!values.projectName || !values.mixDesignId) {
    setAlert('Project Name and Mix Design ID are required.', 'error');
    return;
  }
  
  try {
    const fd = toFormData(values);
    if (state.editingId) {
      await API.update(state.editingId, fd);
      setAlert('Mix design updated successfully.', 'success');
    } else {
      await API.create(fd);
      setAlert('Mix design created successfully.', 'success');
    }
    resetForm();
    await load();
  } catch (err) {
    console.error(err);
    setAlert('Failed to save mix design.', 'error');
  }
});

el('cancel-btn').addEventListener('click', () => {
  resetForm();
});

document.querySelector('#table').addEventListener('click', async (e) => {
  const t = e.target;
  if (!(t instanceof HTMLElement)) return;
  const del = t.getAttribute('data-delete');
  const edit = t.getAttribute('data-edit');
  if (del) {
    if (confirm('Delete this mix design? This action cannot be undone.')) {
      try {
        await API.delete(Number(del));
        setAlert('Mix design deleted.', 'success');
        await load();
      } catch (err) {
        setAlert('Failed to delete mix design.', 'error');
      }
    }
  } else if (edit) {
    const id = Number(edit);
    const item = state.items.find(x => x.id === id);
    if (!item) return;
    state.editingId = id;
    el('id').value = String(id);
    el('projectName').value = item.projectName;
    el('mixDesignId').value = item.mixDesignId;
    el('specifiedStrengthPsi').value = String(item.specifiedStrengthPsi ?? 0);
    el('slumpInches').value = item.slumpInches ?? '';
    el('airContentPercent').value = item.airContentPercent ?? '';
    el('batchVolume').value = item.batchVolume ?? '';
    el('volumeUnit').value = item.volumeUnit ?? '';
    el('materials').value = item.materials ?? '';
    el('notes').value = item.notes ?? '';
    el('document').value = '';
    el('image').value = '';
    
    // Show existing image if available
    if (item.hasImage) {
      const preview = el('image-preview');
      preview.innerHTML = `<img src="${API.getImage(item.id)}" alt="Current" style="max-width:200px;max-height:200px;border-radius:8px" />`;
      preview.style.display = 'block';
    }
    
    el('form-title').textContent = 'Edit Mix Design';
    el('submit-btn').textContent = 'Update Mix Design';
    el('cancel-btn').style.display = '';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
});

// Simple debounced search
let searchTimer = null;
el('search').addEventListener('input', (e) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    state.search = e.target.value || '';
    render();
  }, 250);
});

// Initialize app - check auth and display user info
function initApp() {
  // Check if user is authenticated
  if (!Auth.checkAuth()) {
    return;
  }
  
  // Display user info
  const user = Auth.getUser();
  if (user) {
    el('user-name').textContent = user.fullName || 'User';
    el('user-email').textContent = user.email;
    
    // Show admin badge if applicable
    if (user.isSystemAdmin) {
      el('user-name').innerHTML += ' <span class="badge" style="background: #ff9800; color: white; border: none;">System Admin</span>';
    } else if (user.isCompanyAdmin) {
      el('user-name').innerHTML += ' <span class="badge" style="background: #2196f3; color: white; border: none;">Admin</span>';
    }
  }
  
  // Logout button handler
  el('logout-btn').addEventListener('click', () => {
    if (confirm('Are you sure you want to logout?')) {
      Auth.logout();
    }
  });
  
  // Initial load
  load();
}

// Start app
initApp();
