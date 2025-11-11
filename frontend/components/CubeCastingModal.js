'use client';

import { useState, useEffect } from 'react';
import Modal from './ui/Modal';
import Button from './ui/Button';
import Input from './ui/Input';
import { Calendar, Beaker, Building2, Clock, CheckCircle2 } from 'lucide-react';

/**
 * Cube Casting Modal
 * 
 * Shown after batch entry is saved. Allows user to specify:
 * - Which test ages to create (3, 7, 28, 56 days)
 * - Number of sets per age
 * - Third-party lab assignments
 * - Curing details
 * 
 * Automatically calculates test dates and creates reminder schedule.
 */
export default function CubeCastingModal({ 
  isOpen, 
  onClose, 
  batchData,
  onSubmit,
  labs = []
}) {
  const [selectedAges, setSelectedAges] = useState([7, 28]);
  const [setsPerAge, setSetsPerAge] = useState(1);
  const [thirdPartyAssignments, setThirdPartyAssignments] = useState({});
  const [curingMethod, setCuringMethod] = useState('Water');
  const [curingTemperature, setCuringTemperature] = useState(23);
  const [castingTime, setCastingTime] = useState('');
  const [showPreview, setShowPreview] = useState(false);
  const [loading, setLoading] = useState(false);

  const testAgeOptions = [
    { days: 3, label: '3 Days', description: 'Early strength check' },
    { days: 7, label: '7 Days', description: 'Week strength' },
    { days: 28, label: '28 Days', description: 'Design strength (Standard)' },
    { days: 56, label: '56 Days', description: 'Long-term strength' }
  ];

  const curingMethods = ['Water', 'Wet Burlap', 'Curing Compound', 'Steam'];

  useEffect(() => {
    if (isOpen) {
      // Set default casting time to current time
      const now = new Date();
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      setCastingTime(`${hours}:${minutes}`);
      
      // Reset to defaults
      setSelectedAges([7, 28]);
      setSetsPerAge(1);
      setThirdPartyAssignments({});
      setCuringMethod('Water');
      setCuringTemperature(23);
      setShowPreview(false);
    }
  }, [isOpen]);

  const toggleTestAge = (days) => {
    setSelectedAges(prev => 
      prev.includes(days) 
        ? prev.filter(d => d !== days)
        : [...prev, days].sort((a, b) => a - b)
    );
  };

  const handleLabAssignment = (age, labId) => {
    setThirdPartyAssignments(prev => ({
      ...prev,
      [age]: labId || null
    }));
  };

  const calculateTestDate = (days) => {
    if (!batchData?.deliveryDate) return 'N/A';
    const castingDate = new Date(batchData.deliveryDate);
    const testDate = new Date(castingDate);
    testDate.setDate(testDate.getDate() + days);
    return testDate.toLocaleDateString('en-IN', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const getTotalCubeSets = () => {
    return selectedAges.length * setsPerAge;
  };

  const getTotalCubes = () => {
    return getTotalCubeSets() * 3; // 3 cubes per set (A, B, C)
  };

  const handleSubmit = async () => {
    if (selectedAges.length === 0) {
      alert('Please select at least one test age');
      return;
    }

    setLoading(true);
    
    try {
      const data = {
        batch_id: batchData.batchId,
        project_id: batchData.projectId || parseInt(new URLSearchParams(window.location.search).get('project_id')),
        casting_date: batchData.deliveryDate,
        casting_time: castingTime,
        test_ages: selectedAges,
        number_of_sets_per_age: setsPerAge,
        third_party_lab_assignments: Object.fromEntries(
          Object.entries(thirdPartyAssignments).filter(([_, v]) => v)
        ),
        curing_method: curingMethod,
        curing_temperature: parseFloat(curingTemperature)
      };

      await onSubmit(data);
      onClose();
    } catch (error) {
      console.error('Error creating cube sets:', error);
      alert('Failed to create cube sets. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!batchData) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="🧪 Cast Cube Test Specimens"
      size="large"
    >
      <div className="space-y-6">
        {/* Batch Summary */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Building2 className="w-5 h-5 text-blue-600 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 mb-2">Batch Details</h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span className="text-gray-600">Batch:</span>
                  <span className="ml-2 font-medium text-gray-900">{batchData.batchNumber}</span>
                </div>
                <div>
                  <span className="text-gray-600">Date:</span>
                  <span className="ml-2 font-medium text-gray-900">
                    {new Date(batchData.deliveryDate).toLocaleDateString('en-IN')}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Quantity:</span>
                  <span className="ml-2 font-medium text-gray-900">
                    {batchData.quantityReceived || batchData.quantityOrdered} m³
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Location:</span>
                  <span className="ml-2 font-medium text-gray-900">
                    {batchData.location?.elementId || 'N/A'}
                  </span>
                </div>
              </div>
              
              {batchData.recommendations && (
                <div className="mt-3 pt-3 border-t border-blue-200">
                  <p className="text-sm text-blue-900">
                    💡 <strong>Recommended:</strong> {batchData.recommendations.recommendedSets} sets
                    <span className="text-blue-700 ml-1">
                      ({batchData.recommendations.reason})
                    </span>
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {!showPreview ? (
          <>
            {/* Test Age Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Select Test Ages <span className="text-red-500">*</span>
              </label>
              <div className="grid grid-cols-2 gap-3">
                {testAgeOptions.map(option => (
                  <div
                    key={option.days}
                    onClick={() => toggleTestAge(option.days)}
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      selectedAges.includes(option.days)
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-gray-900">{option.label}</span>
                      {selectedAges.includes(option.days) && (
                        <CheckCircle2 className="w-5 h-5 text-blue-600" />
                      )}
                    </div>
                    <p className="text-sm text-gray-600">{option.description}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      Test date: {calculateTestDate(option.days)}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Number of Sets */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Sets per Age
              </label>
              <Input
                type="number"
                min="1"
                max="10"
                value={setsPerAge}
                onChange={(e) => setSetsPerAge(parseInt(e.target.value) || 1)}
                placeholder="Usually 1"
              />
              <p className="mt-1 text-sm text-gray-500">
                Each set contains 3 cubes (A, B, C)
              </p>
            </div>

            {/* Third-party Lab Assignment */}
            {selectedAges.length > 0 && labs.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Third-party Lab Assignment (Optional)
                </label>
                <div className="space-y-2">
                  {selectedAges.map(age => (
                    <div key={age} className="flex items-center gap-3">
                      <span className="text-sm text-gray-700 w-24">{age}-day test:</span>
                      <select
                        value={thirdPartyAssignments[age] || ''}
                        onChange={(e) => handleLabAssignment(age, e.target.value)}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                      >
                        <option value="">In-house testing</option>
                        {labs.map(lab => (
                          <option key={lab.id} value={lab.id}>
                            {lab.labName || lab.lab_name}
                          </option>
                        ))}
                      </select>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Curing Details */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Curing Method
                </label>
                <select
                  value={curingMethod}
                  onChange={(e) => setCuringMethod(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                >
                  {curingMethods.map(method => (
                    <option key={method} value={method}>{method}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Curing Temperature (°C)
                </label>
                <Input
                  type="number"
                  step="0.1"
                  value={curingTemperature}
                  onChange={(e) => setCuringTemperature(e.target.value)}
                  placeholder="23"
                />
                <p className="mt-1 text-xs text-gray-500">Standard: 23±2°C</p>
              </div>
            </div>

            {/* Casting Time */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Casting Time
              </label>
              <Input
                type="time"
                value={castingTime}
                onChange={(e) => setCastingTime(e.target.value)}
              />
            </div>

            {/* Summary Stats */}
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-3">Summary</h4>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-3xl font-bold text-blue-600">{getTotalCubeSets()}</div>
                  <div className="text-sm text-gray-600 mt-1">Total Sets</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-green-600">{getTotalCubes()}</div>
                  <div className="text-sm text-gray-600 mt-1">Total Cubes</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-purple-600">{selectedAges.length}</div>
                  <div className="text-sm text-gray-600 mt-1">Test Ages</div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4 border-t">
              <Button
                variant="outline"
                onClick={onClose}
                className="flex-1"
                disabled={loading}
              >
                Cancel
              </Button>
              <Button
                onClick={() => setShowPreview(true)}
                className="flex-1"
                disabled={selectedAges.length === 0 || loading}
              >
                Preview Schedule
              </Button>
            </div>
          </>
        ) : (
          <>
            {/* Preview Schedule */}
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">📋 Test Schedule Preview</h3>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {selectedAges.map(age => (
                  <div key={age} className="border border-gray-200 rounded-lg p-4 bg-white">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Beaker className="w-5 h-5 text-blue-600" />
                        <span className="font-semibold text-gray-900">{age}-Day Test</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Calendar className="w-4 h-4" />
                        {calculateTestDate(age)}
                      </div>
                    </div>
                    
                    <div className="space-y-2 ml-7">
                      {Array.from({ length: setsPerAge }).map((_, idx) => (
                        <div key={idx} className="text-sm">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-gray-700">
                              Set #{selectedAges.indexOf(age) * setsPerAge + idx + 1}
                            </span>
                            <span className="text-gray-500">→</span>
                            <span className="text-gray-600">Cubes: A, B, C</span>
                            {thirdPartyAssignments[age] && (
                              <span className="ml-auto text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded">
                                🏢 Third-party Lab
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    <div className="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500">
                      <div className="flex items-center gap-2">
                        <Clock className="w-3 h-3" />
                        Curing: {curingMethod} at {curingTemperature}°C
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Confirmation Buttons */}
            <div className="flex gap-3 pt-4 border-t">
              <Button
                variant="outline"
                onClick={() => setShowPreview(false)}
                className="flex-1"
                disabled={loading}
              >
                ← Back to Edit
              </Button>
              <Button
                onClick={handleSubmit}
                className="flex-1"
                disabled={loading}
              >
                {loading ? 'Creating...' : `✓ Create ${getTotalCubeSets()} Sets`}
              </Button>
            </div>
          </>
        )}
      </div>
    </Modal>
  );
}
