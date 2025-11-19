'use client';

import { useState } from 'react';
import { 
  Shield, Save, User, Phone, Calendar, Package, 
  AlertTriangle, CheckCircle
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';

export default function IssuePPEPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    worker_id: '',
    worker_name: '',
    contractor_name: '',
    phone_number: '',
    items: []
  });

  const [selectedItems, setSelectedItems] = useState([]);

  const ppeItems = [
    { 
      id: 1, 
      name: 'Safety Helmet', 
      icon: '⛑️', 
      category: 'Head Protection',
      mandatory: true,
      lifespan: '2 years'
    },
    { 
      id: 2, 
      name: 'Safety Shoes', 
      icon: '👞', 
      category: 'Foot Protection',
      mandatory: true,
      lifespan: '1 year'
    },
    { 
      id: 3, 
      name: 'High Visibility Vest', 
      icon: '🦺', 
      category: 'Visibility',
      mandatory: true,
      lifespan: '1 year'
    },
    { 
      id: 4, 
      name: 'Safety Glasses', 
      icon: '🥽', 
      category: 'Eye Protection',
      mandatory: true,
      lifespan: '1 year'
    },
    { 
      id: 5, 
      name: 'Work Gloves', 
      icon: '🧤', 
      category: 'Hand Protection',
      mandatory: true,
      lifespan: '6 months'
    },
    { 
      id: 6, 
      name: 'Dust Mask/Respirator', 
      icon: '😷', 
      category: 'Respiratory Protection',
      mandatory: false,
      lifespan: '3 months'
    },
    { 
      id: 7, 
      name: 'Ear Plugs/Muffs', 
      icon: '👂', 
      category: 'Hearing Protection',
      mandatory: false,
      lifespan: '6 months'
    },
    { 
      id: 8, 
      name: 'Fall Protection Harness', 
      icon: '🪢', 
      category: 'Fall Protection',
      mandatory: false,
      lifespan: '2 years'
    },
    { 
      id: 9, 
      name: 'Welding Shield', 
      icon: '🛡️', 
      category: 'Face Protection',
      mandatory: false,
      lifespan: '2 years'
    },
    { 
      id: 10, 
      name: 'Rain Coat', 
      icon: '🧥', 
      category: 'Weather Protection',
      mandatory: false,
      lifespan: '1 year'
    },
    { 
      id: 11, 
      name: 'Knee Pads', 
      icon: '🦵', 
      category: 'Knee Protection',
      mandatory: false,
      lifespan: '1 year'
    },
    { 
      id: 12, 
      name: 'Tool Belt', 
      icon: '🔨', 
      category: 'Tool Management',
      mandatory: false,
      lifespan: '2 years'
    }
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const togglePPEItem = (item) => {
    setSelectedItems(prev => {
      const exists = prev.find(i => i.id === item.id);
      if (exists) {
        return prev.filter(i => i.id !== item.id);
      } else {
        return [...prev, { ...item, quantity: 1, size: 'M' }];
      }
    });
  };

  const updateItemQuantity = (itemId, quantity) => {
    setSelectedItems(prev =>
      prev.map(item =>
        item.id === itemId ? { ...item, quantity: parseInt(quantity) || 1 } : item
      )
    );
  };

  const updateItemSize = (itemId, size) => {
    setSelectedItems(prev =>
      prev.map(item =>
        item.id === itemId ? { ...item, size } : item
      )
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.worker_id || !formData.worker_name || selectedItems.length === 0) {
      toast.error('Please fill in worker details and select at least one PPE item');
      return;
    }

    // Check if all mandatory items are selected
    const mandatoryItems = ppeItems.filter(item => item.mandatory);
    const selectedMandatory = selectedItems.filter(item => item.mandatory);
    
    if (selectedMandatory.length < mandatoryItems.length) {
      toast.error('All mandatory PPE items must be issued');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const projectId = localStorage.getItem('activeProjectId');
      
      const response = await fetch('/api/ppe/issue', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          project_id: parseInt(projectId),
          issued_by: parseInt(localStorage.getItem('userId')),
          items: selectedItems.map(item => ({
            ppe_item: item.name,
            category: item.category,
            quantity: item.quantity,
            size: item.size
          }))
        })
      });

      if (!response.ok) throw new Error('Failed to issue PPE');

      const data = await response.json();
      toast.success('PPE issued successfully');
      router.push('/dashboard/ppe');
    } catch (error) {
      console.error('Error issuing PPE:', error);
      toast.error('Failed to issue PPE');
    } finally {
      setLoading(false);
    }
  };

  const mandatoryCount = ppeItems.filter(i => i.mandatory).length;
  const selectedMandatoryCount = selectedItems.filter(i => i.mandatory).length;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
            <Shield className="w-6 h-6 text-green-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Issue PPE to Worker</h1>
            <p className="text-sm text-gray-600">Distribute personal protective equipment</p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Worker Details */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <User className="w-5 h-5 text-gray-600" />
            Worker Information
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Worker ID*
              </label>
              <input
                type="text"
                name="worker_id"
                value={formData.worker_id}
                onChange={handleChange}
                placeholder="e.g., WKR-001"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Worker Name*
              </label>
              <input
                type="text"
                name="worker_name"
                value={formData.worker_name}
                onChange={handleChange}
                placeholder="e.g., Rajesh Kumar"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contractor Name
              </label>
              <input
                type="text"
                name="contractor_name"
                value={formData.contractor_name}
                onChange={handleChange}
                placeholder="e.g., ABC Contractors"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Phone className="w-4 h-4 inline mr-1" />
                Phone Number
              </label>
              <input
                type="tel"
                name="phone_number"
                value={formData.phone_number}
                onChange={handleChange}
                placeholder="e.g., +91 9876543210"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
            </div>
          </div>
        </div>

        {/* PPE Selection */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Package className="w-5 h-5 text-green-600" />
              Select PPE Items*
            </h2>
            <div className="text-sm">
              <span className="text-gray-600">Mandatory: </span>
              <span className={selectedMandatoryCount === mandatoryCount ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
                {selectedMandatoryCount}/{mandatoryCount}
              </span>
              <span className="text-gray-600 ml-3">Total: </span>
              <span className="text-blue-600 font-medium">{selectedItems.length}</span>
            </div>
          </div>

          {/* Mandatory Items */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-red-600 mb-3 flex items-center gap-1">
              <AlertTriangle className="w-4 h-4" />
              Mandatory Items (Must Issue All)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {ppeItems.filter(item => item.mandatory).map((item) => {
                const isSelected = selectedItems.find(i => i.id === item.id);
                return (
                  <label
                    key={item.id}
                    className={`relative flex flex-col p-4 border-2 rounded-lg cursor-pointer transition ${
                      isSelected
                        ? 'border-green-500 bg-green-50'
                        : 'border-red-300 bg-red-50'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={!!isSelected}
                      onChange={() => togglePPEItem(item)}
                      className="sr-only"
                    />
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl">{item.icon}</span>
                      <div className="flex-1">
                        <span className="font-medium text-gray-900 text-sm block">{item.name}</span>
                        <span className="text-xs text-gray-600">{item.category}</span>
                      </div>
                      {isSelected && (
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      )}
                    </div>
                    <p className="text-xs text-gray-500">Lifespan: {item.lifespan}</p>
                  </label>
                );
              })}
            </div>
          </div>

          {/* Optional Items */}
          <div>
            <h3 className="text-sm font-medium text-gray-600 mb-3">
              Optional Items (Based on Job Requirements)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {ppeItems.filter(item => !item.mandatory).map((item) => {
                const isSelected = selectedItems.find(i => i.id === item.id);
                return (
                  <label
                    key={item.id}
                    className={`relative flex flex-col p-4 border-2 rounded-lg cursor-pointer transition ${
                      isSelected
                        ? 'border-green-500 bg-green-50'
                        : 'border-gray-200 hover:border-green-300'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={!!isSelected}
                      onChange={() => togglePPEItem(item)}
                      className="sr-only"
                    />
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl">{item.icon}</span>
                      <div className="flex-1">
                        <span className="font-medium text-gray-900 text-sm block">{item.name}</span>
                        <span className="text-xs text-gray-600">{item.category}</span>
                      </div>
                      {isSelected && (
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      )}
                    </div>
                    <p className="text-xs text-gray-500">Lifespan: {item.lifespan}</p>
                  </label>
                );
              })}
            </div>
          </div>
        </div>

        {/* Selected Items Details */}
        {selectedItems.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              Selected Items ({selectedItems.length})
            </h2>
            <div className="space-y-3">
              {selectedItems.map((item) => (
                <div key={item.id} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
                  <span className="text-2xl">{item.icon}</span>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{item.name}</p>
                    <p className="text-xs text-gray-600">{item.category}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <label className="text-sm">
                      <span className="text-gray-600 mr-2">Qty:</span>
                      <input
                        type="number"
                        min="1"
                        max="10"
                        value={item.quantity}
                        onChange={(e) => updateItemQuantity(item.id, e.target.value)}
                        className="w-16 px-2 py-1 border border-gray-300 rounded text-center"
                      />
                    </label>
                    {['Safety Shoes', 'Work Gloves', 'Rain Coat'].includes(item.name) && (
                      <label className="text-sm">
                        <span className="text-gray-600 mr-2">Size:</span>
                        <select
                          value={item.size}
                          onChange={(e) => updateItemSize(item.id, e.target.value)}
                          className="px-2 py-1 border border-gray-300 rounded"
                        >
                          <option value="S">S</option>
                          <option value="M">M</option>
                          <option value="L">L</option>
                          <option value="XL">XL</option>
                          <option value="XXL">XXL</option>
                        </select>
                      </label>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex gap-3">
            <AlertTriangle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">PPE Issuance Process:</p>
              <ol className="list-decimal list-inside space-y-1">
                <li>Worker will be notified about PPE issuance</li>
                <li>Digital acknowledgment will be recorded</li>
                <li>Return dates will be set based on lifespan</li>
                <li>Replacement reminders will be sent automatically</li>
                <li>Worker's PPE compliance status will be updated</li>
              </ol>
            </div>
          </div>
        </div>

        {/* Submit Buttons */}
        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => router.back()}
            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading || selectedMandatoryCount < mandatoryCount}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Issuing...
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                Issue PPE ({selectedItems.length} items)
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
