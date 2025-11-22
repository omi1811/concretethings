'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import {
    Building2, Users, ArrowLeft, Mail, Phone, MapPin,
    FileText, CheckCircle2, XCircle, Clock, Plus, Shield, Trash2
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';

const SUPPORT_API_BASE = '/api/support';

export default function CompanyDetailsPage() {
    const params = useParams();
    const router = useRouter();
    const [loading, setLoading] = useState(true);
    const [company, setCompany] = useState(null);
    const [projects, setProjects] = useState([]);
    const [users, setUsers] = useState([]);
    const [showAssignAdminModal, setShowAssignAdminModal] = useState(false);

    useEffect(() => {
        if (params.id) {
            fetchCompanyDetails();
        }
    }, [params.id]);

    const fetchCompanyDetails = async () => {
        try {
            const res = await api.get(`${SUPPORT_API_BASE}/companies/${params.id}`);
            const data = res.data.data;

            setCompany(data);
            setProjects(data.projects || []);
            setUsers(data.users || []);
        } catch (error) {
            console.error('Error fetching company details:', error);
            if (error.response?.status === 404) {
                alert('Company not found');
                router.push('/support');
            }
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-muted/30">
                <div className="text-center space-y-4">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                    <p className="text-muted-foreground">Loading company details...</p>
                </div>
            </div>
        );
    }

    if (!company) return null;

    return (
        <div className="min-h-screen bg-muted/30 p-6 space-y-8">
            {/* Header */}
            <div className="flex items-center gap-4">
                <Button variant="ghost" size="sm" onClick={() => router.back()}>
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Back to Dashboard
                </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Company Info */}
                <div className="space-y-8 lg:col-span-1">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Building2 className="w-5 h-5 text-primary" />
                                Company Profile
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div>
                                <h2 className="text-2xl font-bold text-foreground">{company.name}</h2>
                                <div className="mt-2 flex flex-wrap gap-2">
                                    <StatusBadge status={company.billingStatus} />
                                    <Badge variant="outline">
                                        Limit: {company.activeProjectsLimit} Projects
                                    </Badge>
                                </div>
                            </div>

                            <div className="space-y-3 text-sm">
                                {company.companyEmail && (
                                    <div className="flex items-center gap-3 text-muted-foreground">
                                        <Mail className="w-4 h-4" />
                                        <span>{company.companyEmail}</span>
                                    </div>
                                )}
                                {company.companyPhone && (
                                    <div className="flex items-center gap-3 text-muted-foreground">
                                        <Phone className="w-4 h-4" />
                                        <span>{company.companyPhone}</span>
                                    </div>
                                )}
                                {company.companyAddress && (
                                    <div className="flex items-start gap-3 text-muted-foreground">
                                        <MapPin className="w-4 h-4 mt-0.5" />
                                        <span>{company.companyAddress}</span>
                                    </div>
                                )}
                                {company.gstin && (
                                    <div className="flex items-center gap-3 text-muted-foreground">
                                        <FileText className="w-4 h-4" />
                                        <span>GSTIN: {company.gstin}</span>
                                    </div>
                                )}
                            </div>

                            <div className="pt-4 border-t">
                                <div className="grid grid-cols-2 gap-4 text-center">
                                    <div className="p-3 bg-muted/50 rounded-lg">
                                        <p className="text-2xl font-bold text-foreground">{projects.length}</p>
                                        <p className="text-xs text-muted-foreground">Total Projects</p>
                                    </div>
                                    <div className="p-3 bg-muted/50 rounded-lg">
                                        <p className="text-2xl font-bold text-foreground">{users.length}</p>
                                        <p className="text-xs text-muted-foreground">Total Users</p>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* System Admins Section */}
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between">
                            <CardTitle className="flex items-center gap-2">
                                <Shield className="w-5 h-5 text-primary" />
                                System Admins
                            </CardTitle>
                            <Button size="sm" variant="outline" onClick={() => setShowAssignAdminModal(true)}>
                                <Plus className="w-4 h-4 mr-2" />
                                Assign
                            </Button>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {users.filter(u => u.isCompanyAdmin).length === 0 ? (
                                    <p className="text-sm text-muted-foreground text-center py-4">
                                        No System Admins assigned.
                                    </p>
                                ) : (
                                    users.filter(u => u.isCompanyAdmin).map(user => (
                                        <div key={user.id} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                                            <div className="flex items-center gap-3">
                                                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-xs">
                                                    {user.fullName?.charAt(0) || user.email?.charAt(0)}
                                                </div>
                                                <div>
                                                    <p className="text-sm font-medium text-foreground">{user.fullName || 'Unknown Name'}</p>
                                                    <p className="text-xs text-muted-foreground">{user.email}</p>
                                                </div>
                                            </div>
                                            <Badge variant="secondary" className="text-xs">Admin</Badge>
                                        </div>
                                    ))
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Right Column: Projects & Activity */}
                <div className="lg:col-span-2 space-y-8">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <FileText className="w-5 h-5 text-primary" />
                                Projects
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead className="bg-muted/50">
                                        <tr>
                                            <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Project Name</th>
                                            <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Location</th>
                                            <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Status</th>
                                            <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Created</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-border">
                                        {projects.length === 0 ? (
                                            <tr>
                                                <td colSpan="4" className="px-4 py-8 text-center text-muted-foreground">
                                                    No projects found for this company.
                                                </td>
                                            </tr>
                                        ) : (
                                            projects.map((project) => (
                                                <tr key={project.id} className="hover:bg-muted/30">
                                                    <td className="px-4 py-3">
                                                        <p className="font-medium text-foreground">{project.name}</p>
                                                        <p className="text-xs text-muted-foreground">{project.projectCode}</p>
                                                    </td>
                                                    <td className="px-4 py-3 text-sm text-muted-foreground">
                                                        {project.location || '-'}
                                                    </td>
                                                    <td className="px-4 py-3">
                                                        <Badge variant={project.isActive ? 'success' : 'secondary'}>
                                                            {project.status}
                                                        </Badge>
                                                    </td>
                                                    <td className="px-4 py-3 text-sm text-muted-foreground">
                                                        {new Date(project.createdAt).toLocaleDateString()}
                                                    </td>
                                                </tr>
                                            ))
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>

            {/* Assign Admin Modal */}
            {showAssignAdminModal && (
                <AssignAdminModal
                    companyId={company.id}
                    onClose={() => setShowAssignAdminModal(false)}
                    onSuccess={() => {
                        setShowAssignAdminModal(false);
                        fetchCompanyDetails();
                    }}
                />
            )}
        </div>
    );
}

function StatusBadge({ status }) {
    const variants = {
        active: { variant: 'success', icon: CheckCircle2, label: 'Active' },
        suspended: { variant: 'destructive', icon: XCircle, label: 'Suspended' },
        cancelled: { variant: 'secondary', icon: XCircle, label: 'Cancelled' },
        trial: { variant: 'info', icon: Clock, label: 'Trial' }
    };
    const config = variants[status] || variants.active;
    const Icon = config.icon;

    return (
        <Badge variant={config.variant} className="flex items-center gap-1">
            <Icon className="w-3 h-3" />
            {config.label}
        </Badge>
    );
}

function AssignAdminModal({ companyId, onClose, onSuccess }) {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            await api.post(`${SUPPORT_API_BASE}/companies/${companyId}/admins`, { email });
            alert('System Admin assigned successfully!');
            onSuccess();
        } catch (error) {
            console.error('Error assigning admin:', error);
            alert(error.response?.data?.error || 'Failed to assign admin');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Modal isOpen={true} onClose={onClose} title="Assign System Admin">
            <form onSubmit={handleSubmit} className="space-y-4">
                <p className="text-sm text-muted-foreground">
                    Enter the email address of the user you want to assign as a System Admin for this company.
                    They will have full control over the company's projects.
                </p>

                <Input
                    label="User Email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="admin@company.com"
                />

                <div className="flex gap-3 pt-4 justify-end">
                    <Button type="button" variant="outline" onClick={onClose}>
                        Cancel
                    </Button>
                    <Button type="submit" disabled={loading}>
                        {loading ? 'Assigning...' : 'Assign Admin'}
                    </Button>
                </div>
            </form>
        </Modal>
    );
}
