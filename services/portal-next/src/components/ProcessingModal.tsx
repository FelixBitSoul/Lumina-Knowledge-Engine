import React, { useEffect, useState, useCallback } from 'react';
import { X, Loader, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import { Button } from './ui/button';
import { useWebSocket } from '../hooks/useUpload';
import { WebSocketMessage } from '../types';

interface ProcessingModalProps {
  isOpen: boolean;
  onClose: () => void;
  websocketUrl: string;
  fileName: string;
}

const ProcessingModal: React.FC<ProcessingModalProps> = ({
  isOpen,
  onClose,
  websocketUrl,
  fileName,
}) => {
  const [status, setStatus] = useState<'connecting' | 'processing' | 'completed' | 'failed'>('connecting');
  const [progress, setProgress] = useState(0);
  const [total, setTotal] = useState(100);
  const [currentStep, setCurrentStep] = useState<string>('Initializing');
  const [error, setError] = useState<string | null>(null);
  const [chunksCreated, setChunksCreated] = useState<number | null>(null);

  // Debug: Log state changes
  useEffect(() => {
    console.log('[ProcessingModal] State updated:', { status, currentStep, progress, total, chunksCreated, error });
  }, [status, currentStep, progress, total, chunksCreated, error]);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    console.log('[ProcessingModal] Received message:', message);
    switch (message.status) {
      case 'connected':
        console.log('[ProcessingModal] Status: connected');
        setStatus('processing');
        setCurrentStep('Processing document...');
        break;
      case 'processing':
        console.log('[ProcessingModal] Status: processing', message.progress, '/', message.total);
        setStatus('processing');
        setProgress(message.progress || 0);
        setTotal(message.total || 100);
        setCurrentStep(message.step || 'Processing');
        break;
      case 'completed':
        console.log('[ProcessingModal] Status: completed', message.chunks_created);
        setStatus('completed');
        setChunksCreated(message.chunks_created || null);
        setCurrentStep('Completed');
        break;
      case 'failed':
        console.log('[ProcessingModal] Status: failed', message.error);
        setStatus('failed');
        setError(message.error || 'Processing failed');
        setCurrentStep('Failed');
        break;
      default:
        console.log('[ProcessingModal] Unknown status:', message.status);
        break;
    }
  }, []);

  const { connect } = useWebSocket(websocketUrl, handleMessage);

  useEffect(() => {
    if (isOpen && websocketUrl) {
      console.log('[ProcessingModal] Opening WebSocket connection...');
      const ws = connect();

      return () => {
        console.log('[ProcessingModal] Closing WebSocket connection...');
        if (ws) {
          ws.close();
        }
      };
    }
  }, [isOpen, websocketUrl]); // Removed 'connect' from dependencies

  if (!isOpen) return null;

  const getStatusIcon = () => {
    switch (status) {
      case 'connecting':
      case 'processing':
        return <Loader className="h-6 w-6 animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-6 w-6 text-red-500" />;
      default:
        return <Clock className="h-6 w-6" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'connecting':
      case 'processing':
        return 'text-blue-500';
      case 'completed':
        return 'text-green-500';
      case 'failed':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-[#161B22] rounded-xl border border-slate-200 dark:border-slate-800 shadow-2xl w-full max-w-md">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-2">
              <div className={`${getStatusColor()}`}>
                {getStatusIcon()}
              </div>
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white">
                {status === 'completed' ? 'Processing Complete' :
                 status === 'failed' ? 'Processing Failed' :
                 'Processing Document'}
              </h3>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              aria-label="Close"
            >
              <X className="h-5 w-5 text-slate-500 dark:text-slate-400" />
            </button>
          </div>

          <div className="space-y-4">
            <div>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
                File: {fileName}
              </p>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
                Status: {currentStep}
              </p>

              {status === 'processing' && (
                <div className="space-y-2">
                  <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2.5">
                    <div
                      className="bg-blue-600 h-2.5 rounded-full transition-all duration-300 ease-out"
                      style={{ width: `${(progress / total) * 100}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 text-right">
                    {progress}/{total}
                  </p>
                </div>
              )}

              {status === 'completed' && (
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                  <p className="text-green-800 dark:text-green-400 text-sm">
                    ✅ Document processed successfully!
                  </p>
                  {chunksCreated !== null && chunksCreated !== undefined && (
                    <p className="text-green-700 dark:text-green-300 text-sm mt-1">
                      {chunksCreated} chunks created and indexed
                    </p>
                  )}
                </div>
              )}

              {status === 'failed' && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                  <p className="text-red-800 dark:text-red-400 text-sm">
                    ❌ Processing failed
                  </p>
                  {error && (
                    <p className="text-red-700 dark:text-red-300 text-sm mt-1">
                      {error}
                    </p>
                  )}
                </div>
              )}
            </div>

            <div className="pt-4">
              <Button
                onClick={onClose}
                className="w-full"
              >
                {status === 'completed' || status === 'failed' ? 'Close' : 'Cancel'}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProcessingModal;
