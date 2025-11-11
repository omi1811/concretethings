'use client';

import { useRef, useState, useEffect } from 'react';
import { X, RotateCcw, Check, Download } from 'lucide-react';
import Button from './ui/Button';

/**
 * SignatureCanvas Component
 * 
 * Digital signature whiteboard for capturing signatures on documents.
 * Used for:
 * - Cube test verification
 * - Handover register signatures
 * - QM approvals
 * - Site engineer sign-offs
 * 
 * Features:
 * - Touch and mouse support
 * - Smooth drawing
 * - Clear/redo
 * - Save as PNG/base64
 * - Responsive canvas
 */
export default function SignatureCanvas({ 
  onSave, 
  onCancel, 
  title = "Digital Signature",
  subtitle = "Please sign below",
  width = 500,
  height = 200
}) {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [hasSignature, setHasSignature] = useState(false);
  const [context, setContext] = useState(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 2;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      setContext(ctx);

      // Set canvas size
      canvas.width = width;
      canvas.height = height;
      
      // Fill with white background
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(0, 0, width, height);
    }
  }, [width, height]);

  const getCoordinates = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    if (e.touches && e.touches[0]) {
      return {
        x: (e.touches[0].clientX - rect.left) * scaleX,
        y: (e.touches[0].clientY - rect.top) * scaleY
      };
    }
    
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY
    };
  };

  const startDrawing = (e) => {
    e.preventDefault();
    setIsDrawing(true);
    setHasSignature(true);
    const coords = getCoordinates(e);
    context.beginPath();
    context.moveTo(coords.x, coords.y);
  };

  const draw = (e) => {
    if (!isDrawing) return;
    e.preventDefault();
    
    const coords = getCoordinates(e);
    context.lineTo(coords.x, coords.y);
    context.stroke();
  };

  const stopDrawing = () => {
    if (isDrawing) {
      context.closePath();
      setIsDrawing(false);
    }
  };

  const clearSignature = () => {
    const canvas = canvasRef.current;
    context.fillStyle = '#FFFFFF';
    context.fillRect(0, 0, canvas.width, canvas.height);
    setHasSignature(false);
  };

  const saveSignature = () => {
    if (!hasSignature) {
      alert('Please provide a signature before saving');
      return;
    }

    const canvas = canvasRef.current;
    
    // Convert to blob
    canvas.toBlob((blob) => {
      // Also get base64 for immediate use
      const dataUrl = canvas.toDataURL('image/png');
      
      onSave({
        blob: blob,
        dataUrl: dataUrl,
        timestamp: new Date().toISOString()
      });
    }, 'image/png');
  };

  const downloadSignature = () => {
    if (!hasSignature) {
      alert('Please provide a signature before downloading');
      return;
    }

    const canvas = canvasRef.current;
    const dataUrl = canvas.toDataURL('image/png');
    const link = document.createElement('a');
    link.download = `signature_${Date.now()}.png`;
    link.href = dataUrl;
    link.click();
  };

  return (
    <div className="bg-white rounded-lg border border-gray-300 p-6 shadow-lg">
      {/* Header */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
      </div>

      {/* Canvas */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg overflow-hidden bg-white mb-4">
        <canvas
          ref={canvasRef}
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseLeave={stopDrawing}
          onTouchStart={startDrawing}
          onTouchMove={draw}
          onTouchEnd={stopDrawing}
          className="cursor-crosshair touch-none"
          style={{ 
            width: '100%', 
            height: 'auto',
            display: 'block'
          }}
        />
      </div>

      {/* Instructions */}
      <div className="text-xs text-gray-500 mb-4 text-center">
        {hasSignature 
          ? '✓ Signature captured. You can clear and re-sign if needed.'
          : 'Sign above using your mouse or touchscreen'
        }
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-2 justify-end">
        <Button
          variant="outline"
          size="sm"
          onClick={clearSignature}
          disabled={!hasSignature}
        >
          <RotateCcw className="w-4 h-4 mr-2" />
          Clear
        </Button>
        
        <Button
          variant="outline"
          size="sm"
          onClick={downloadSignature}
          disabled={!hasSignature}
        >
          <Download className="w-4 h-4 mr-2" />
          Download
        </Button>
        
        {onCancel && (
          <Button
            variant="outline"
            size="sm"
            onClick={onCancel}
          >
            <X className="w-4 h-4 mr-2" />
            Cancel
          </Button>
        )}
        
        <Button
          size="sm"
          onClick={saveSignature}
          disabled={!hasSignature}
        >
          <Check className="w-4 h-4 mr-2" />
          Save Signature
        </Button>
      </div>

      {/* Timestamp Info */}
      {hasSignature && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            📅 Signature will be timestamped: {new Date().toLocaleString('en-IN', {
              year: 'numeric',
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}
          </p>
        </div>
      )}
    </div>
  );
}
