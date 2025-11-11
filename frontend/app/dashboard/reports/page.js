'use client';

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FileText, Download } from 'lucide-react';

export default function ReportsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
        <p className="text-gray-600 mt-1">Generate and download quality control reports</p>
      </div>

      <Card>
        <CardContent className="py-12 text-center">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Coming Soon</h3>
          <p className="text-gray-600 mb-6">Reporting module with PDF generation will be available soon</p>
          <Button disabled variant="outline">
            Feature Under Development
          </Button>
        </CardContent>
      </Card>

      <div className="grid md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Batch Reports</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 text-sm mb-4">Comprehensive batch register with photos and approval status</p>
            <Button size="sm" variant="outline" disabled>
              <Download className="w-4 h-4 mr-2" />
              Generate
            </Button>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Test Reports</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 text-sm mb-4">Cube test results with strength analysis and pass/fail status</p>
            <Button size="sm" variant="outline" disabled>
              <Download className="w-4 h-4 mr-2" />
              Generate
            </Button>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Training Reports</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 text-sm mb-4">Training attendance records with session details</p>
            <Button size="sm" variant="outline" disabled>
              <Download className="w-4 h-4 mr-2" />
              Generate
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
