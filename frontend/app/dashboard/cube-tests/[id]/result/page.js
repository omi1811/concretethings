'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Save, Calculator, Beaker } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Spinner } from '@/components/ui/Spinner';
import { cubeTestAPI } from '@/lib/api-optimized';

export default function RecordResultPage({ params }) {
    const router = useRouter();
    const { id } = params;
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [test, setTest] = useState(null);

    const [inputMode, setInputMode] = useState('strength'); // 'strength' or 'load'

    const [formData, setFormData] = useState({
        testingDate: new Date().toISOString().slice(0, 10),
        remarks: '',
        // Strength Mode Inputs
        cube1Strength: '',
        cube2Strength: '',
        cube3Strength: '',
        // Load Mode Inputs
        cube1Load: '',
        cube2Load: '',
        cube3Load: '',
        // Dimensions (default 150mm)
        cube1Length: '150', cube1Width: '150',
        cube2Length: '150', cube2Width: '150',
        cube3Length: '150', cube3Width: '150',
    });

    useEffect(() => {
        fetchTest();
    }, [id]);

    const fetchTest = async () => {
        try {
            const projectId = localStorage.getItem('currentProjectId') || '1';
            const result = await cubeTestAPI.get(id, projectId);
            if (result.data) {
                setTest(result.data);
                // Pre-fill if exists
                if (result.data.cube1) {
                    setFormData(prev => ({
                        ...prev,
                        cube1Strength: result.data.cube1.strength || '',
                        cube2Strength: result.data.cube2.strength || '',
                        cube3Strength: result.data.cube3.strength || '',
                        cube1Load: result.data.cube1.load || '',
                        cube2Load: result.data.cube2.load || '',
                        cube3Load: result.data.cube3.load || '',
                    }));
                }
            }
        } catch (error) {
            console.error('Error fetching test:', error);
            alert('Failed to load test details');
        } finally {
            setLoading(false);
        }
    };

    const calculateStrength = (load, length, width) => {
        if (!load || !length || !width) return null;
        const area = parseFloat(length) * parseFloat(width);
        if (area === 0) return 0;
        return ((parseFloat(load) * 1000) / area).toFixed(2);
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);

        try {
            const projectId = localStorage.getItem('currentProjectId') || '1';

            let payload = {
                project_id: parseInt(projectId),
                testing_date: formData.testingDate,
                remarks: formData.remarks
            };

            if (inputMode === 'strength') {
                payload.cube_1_strength_mpa = parseFloat(formData.cube1Strength);
                payload.cube_2_strength_mpa = parseFloat(formData.cube2Strength);
                payload.cube_3_strength_mpa = parseFloat(formData.cube3Strength);
            } else {
                // Load Mode
                payload.cube_1_load_kn = parseFloat(formData.cube1Load);
                payload.cube_2_load_kn = parseFloat(formData.cube2Load);
                payload.cube_3_load_kn = parseFloat(formData.cube3Load);

                // Send dimensions too if needed, but for now backend defaults to 150x150
                // We rely on backend calculation or send calculated strength?
                // Plan said backend calculates. So we send loads.
            }

            await cubeTestAPI.update(id, payload);
            alert('Result recorded successfully!');
            router.push('/dashboard/cube-tests');
        } catch (error) {
            console.error('Error saving result:', error);
            alert('Failed to save result');
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
    if (!test) return <div className="text-center py-12">Test not found</div>;

    return (
        <div className="space-y-6 max-w-4xl mx-auto">
            {/* Header */}
            <div className="flex items-center gap-4">
                <Link href="/dashboard/cube-tests">
                    <Button variant="outline" size="sm">
                        <ArrowLeft className="w-4 h-4 mr-2" />
                        Back
                    </Button>
                </Link>
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Record Test Result</h1>
                    <p className="text-gray-600 mt-1">
                        {test.batchNumber !== 'Planned' ? `Batch #${test.batchNumber}` : 'Planned Test'} • {test.concreteType} • {test.testAgeDays} Days
                    </p>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Input Mode Toggle */}
                <Card>
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <CardTitle className="flex items-center gap-2">
                                <Beaker className="w-5 h-5" />
                                Test Results
                            </CardTitle>
                            <div className="flex bg-gray-100 p-1 rounded-lg">
                                <button
                                    type="button"
                                    onClick={() => setInputMode('strength')}
                                    className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${inputMode === 'strength' ? 'bg-white shadow text-blue-600' : 'text-gray-600 hover:text-gray-900'
                                        }`}
                                >
                                    Strength (MPa)
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setInputMode('load')}
                                    className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${inputMode === 'load' ? 'bg-white shadow text-blue-600' : 'text-gray-600 hover:text-gray-900'
                                        }`}
                                >
                                    Load (KN)
                                </button>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {/* Cube 1 */}
                            <div className="space-y-3 p-4 bg-gray-50 rounded-lg border border-gray-200">
                                <h3 className="font-medium text-gray-900">Cube 1</h3>
                                {inputMode === 'load' ? (
                                    <>
                                        <div>
                                            <label className="block text-xs font-medium text-gray-500 mb-1">Load (KN)</label>
                                            <input
                                                type="number"
                                                name="cube1Load"
                                                value={formData.cube1Load}
                                                onChange={handleChange}
                                                required
                                                step="0.1"
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                            />
                                        </div>
                                        <div className="text-xs text-gray-500 pt-1">
                                            Calc: {calculateStrength(formData.cube1Load, formData.cube1Length, formData.cube1Width) || '-'} MPa
                                        </div>
                                    </>
                                ) : (
                                    <div>
                                        <label className="block text-xs font-medium text-gray-500 mb-1">Strength (MPa)</label>
                                        <input
                                            type="number"
                                            name="cube1Strength"
                                            value={formData.cube1Strength}
                                            onChange={handleChange}
                                            required
                                            step="0.1"
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                        />
                                    </div>
                                )}
                            </div>

                            {/* Cube 2 */}
                            <div className="space-y-3 p-4 bg-gray-50 rounded-lg border border-gray-200">
                                <h3 className="font-medium text-gray-900">Cube 2</h3>
                                {inputMode === 'load' ? (
                                    <>
                                        <div>
                                            <label className="block text-xs font-medium text-gray-500 mb-1">Load (KN)</label>
                                            <input
                                                type="number"
                                                name="cube2Load"
                                                value={formData.cube2Load}
                                                onChange={handleChange}
                                                required
                                                step="0.1"
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                            />
                                        </div>
                                        <div className="text-xs text-gray-500 pt-1">
                                            Calc: {calculateStrength(formData.cube2Load, formData.cube2Length, formData.cube2Width) || '-'} MPa
                                        </div>
                                    </>
                                ) : (
                                    <div>
                                        <label className="block text-xs font-medium text-gray-500 mb-1">Strength (MPa)</label>
                                        <input
                                            type="number"
                                            name="cube2Strength"
                                            value={formData.cube2Strength}
                                            onChange={handleChange}
                                            required
                                            step="0.1"
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                        />
                                    </div>
                                )}
                            </div>

                            {/* Cube 3 */}
                            <div className="space-y-3 p-4 bg-gray-50 rounded-lg border border-gray-200">
                                <h3 className="font-medium text-gray-900">Cube 3</h3>
                                {inputMode === 'load' ? (
                                    <>
                                        <div>
                                            <label className="block text-xs font-medium text-gray-500 mb-1">Load (KN)</label>
                                            <input
                                                type="number"
                                                name="cube3Load"
                                                value={formData.cube3Load}
                                                onChange={handleChange}
                                                required
                                                step="0.1"
                                                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                            />
                                        </div>
                                        <div className="text-xs text-gray-500 pt-1">
                                            Calc: {calculateStrength(formData.cube3Load, formData.cube3Length, formData.cube3Width) || '-'} MPa
                                        </div>
                                    </>
                                ) : (
                                    <div>
                                        <label className="block text-xs font-medium text-gray-500 mb-1">Strength (MPa)</label>
                                        <input
                                            type="number"
                                            name="cube3Strength"
                                            value={formData.cube3Strength}
                                            onChange={handleChange}
                                            required
                                            step="0.1"
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                        />
                                    </div>
                                )}
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Metadata */}
                <Card>
                    <CardContent className="pt-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Testing Date</label>
                                <input
                                    type="date"
                                    name="testingDate"
                                    value={formData.testingDate}
                                    onChange={handleChange}
                                    required
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Remarks</label>
                                <input
                                    type="text"
                                    name="remarks"
                                    value={formData.remarks}
                                    onChange={handleChange}
                                    placeholder="Any observations..."
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Action Buttons */}
                <div className="flex gap-4">
                    <Button type="submit" disabled={saving} className="flex-1">
                        {saving ? (
                            <>
                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                                Saving...
                            </>
                        ) : (
                            <>
                                <Save className="w-4 h-4 mr-2" />
                                Save Result
                            </>
                        )}
                    </Button>
                    <Link href="/dashboard/cube-tests">
                        <Button type="button" variant="outline">
                            Cancel
                        </Button>
                    </Link>
                </div>
            </form>
        </div>
    );
}
