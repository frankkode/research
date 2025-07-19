import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import LoadingSpinner from '../common/LoadingSpinner';
import { toast } from 'react-hot-toast';
import { 
  ChevronLeftIcon, 
  ChevronRightIcon, 
  MagnifyingGlassMinusIcon, 
  MagnifyingGlassPlusIcon,
  DocumentTextIcon,
  EyeIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

// Import CSS for react-pdf
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

// Set up PDF.js worker - use the correct version from react-pdf
pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';

interface PDFViewerProps {
  sessionId: string;
  onInteractionUpdate?: (totalTime: number, pagesVisited: number) => void;
}

interface PageTracking {
  pageNumber: number;
  timeEntered: number;
  totalTime: number;
  scrollDepth: number;
  maxScrollDepth: number;
}

const PDFViewer: React.FC<PDFViewerProps> = ({ sessionId, onInteractionUpdate }) => {
  const [numPages, setNumPages] = useState<number | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [scale, setScale] = useState(1.0);
  const [isLoading, setIsLoading] = useState(true);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [pageTracking, setPageTracking] = useState<Map<number, PageTracking>>(new Map());
  const [totalReadingTime, setTotalReadingTime] = useState(0);
  const [startTime] = useState(Date.now());
  const pageContainer = useRef<HTMLDivElement>(null);
  const scrollTimeoutRef = useRef<NodeJS.Timeout>();
  const callbackTimeoutRef = useRef<NodeJS.Timeout>();

  // Track current page time
  useEffect(() => {
    const interval = setInterval(() => {
      setPageTracking(prev => {
        const newTracking = new Map(prev);
        const current = newTracking.get(currentPage) || {
          pageNumber: currentPage,
          timeEntered: Date.now(),
          totalTime: 0,
          scrollDepth: 0,
          maxScrollDepth: 0
        };
        
        current.totalTime += 1000; // Add 1 second
        newTracking.set(currentPage, current);
        
        // Update total reading time
        const totalTime = Math.floor((Date.now() - startTime) / 1000);
        setTotalReadingTime(totalTime);
        
        return newTracking;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [currentPage, startTime]);

  // Separate useEffect to handle the callback to avoid render cycle issues
  useEffect(() => {
    // Clear any existing timeout
    if (callbackTimeoutRef.current) {
      clearTimeout(callbackTimeoutRef.current);
    }
    
    // Debounce the callback to prevent excessive calls
    callbackTimeoutRef.current = setTimeout(() => {
      const totalTime = Math.floor((Date.now() - startTime) / 1000);
      const pagesVisited = pageTracking.size;
      
      // Only call the callback if we have meaningful data
      if (totalTime > 0 && pagesVisited > 0) {
        onInteractionUpdate?.(totalTime, pagesVisited);
      }
    }, 250);

    // Cleanup function
    return () => {
      if (callbackTimeoutRef.current) {
        clearTimeout(callbackTimeoutRef.current);
      }
    };
  }, [pageTracking, startTime, onInteractionUpdate]);

  // Track page entry
  useEffect(() => {
    setPageTracking(prev => {
      const newTracking = new Map(prev);
      if (!newTracking.has(currentPage)) {
        newTracking.set(currentPage, {
          pageNumber: currentPage,
          timeEntered: Date.now(),
          totalTime: 0,
          scrollDepth: 0,
          maxScrollDepth: 0
        });
      }
      return newTracking;
    });
  }, [currentPage]);

  // Load PDF document
  useEffect(() => {
    loadPDFDocument();
  }, []);

  const loadPDFDocument = async () => {
    try {
      setIsLoading(true);
      // For now, use local PDF file
      // TODO: Implement backend PDF document retrieval
      setPdfUrl('/linux-commands-guide.pdf');
    } catch (error) {
      toast.error('Failed to load PDF document');
      setPdfUrl('/linux-commands-guide.pdf');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    setIsLoading(false);
  };

  const handleDocumentLoadError = (error: Error) => {
    console.error('Error loading PDF:', error);
    toast.error('Failed to load PDF document');
    setIsLoading(false);
  };

  const logPageInteraction = useCallback(async (pageNumber: number) => {
    const tracking = pageTracking.get(pageNumber);
    if (tracking) {
      try {
        // TODO: Implement proper PDF interaction logging
        console.log('Page interaction:', {
          sessionId,
          pageNumber,
          timeOnPage: Math.floor(tracking.totalTime / 1000),
          scrollDepth: tracking.maxScrollDepth
        });
      } catch (error) {
        console.error('Failed to log page interaction:', error);
      }
    }
  }, [sessionId, pageTracking]);

  const logScrollInteraction = useCallback(async (pageNumber: number, scrollDepth: number) => {
    try {
      // TODO: Implement proper scroll interaction logging
      console.log('Scroll interaction:', {
        sessionId,
        pageNumber,
        scrollDepth,
        totalReadingTime
      });
    } catch (error) {
      console.error('Failed to log scroll interaction:', error);
    }
  }, [sessionId, totalReadingTime]);

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= (numPages || 1)) {
      logPageInteraction(currentPage);
      setCurrentPage(newPage);
    }
  };

  const handleScroll = useCallback(() => {
    if (pageContainer.current) {
      const { scrollTop, scrollHeight, clientHeight } = pageContainer.current;
      const scrollPercentage = Math.round((scrollTop / (scrollHeight - clientHeight)) * 100);
      
      setPageTracking(prev => {
        const newTracking = new Map(prev);
        const current = newTracking.get(currentPage);
        if (current) {
          current.scrollDepth = scrollPercentage;
          current.maxScrollDepth = Math.max(current.maxScrollDepth, scrollPercentage);
          newTracking.set(currentPage, current);
        }
        return newTracking;
      });

      // Debounced logging
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
      scrollTimeoutRef.current = setTimeout(() => {
        logScrollInteraction(currentPage, scrollPercentage);
      }, 500);
    }
  }, [currentPage, logScrollInteraction]);

  const handleZoomIn = () => {
    setScale(prev => Math.min(prev + 0.1, 2.0));
  };

  const handleZoomOut = () => {
    setScale(prev => Math.max(prev - 0.1, 0.5));
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getReadingProgress = () => {
    if (!numPages) return 0;
    return Math.round((pageTracking.size / numPages) * 100);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
            <DocumentTextIcon className="h-5 w-5 text-green-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Linux Commands Guide</h3>
            <p className="text-sm text-gray-600">
              Study the 10 essential Linux commands
            </p>
          </div>
        </div>
        
        {/* Reading Stats */}
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center space-x-2 text-gray-600">
            <ClockIcon className="h-4 w-4" />
            <span>{formatTime(totalReadingTime)}</span>
          </div>
          
          <div className="flex items-center space-x-2 text-gray-600">
            <EyeIcon className="h-4 w-4" />
            <span>{pageTracking.size} / {numPages || 0} pages</span>
          </div>
          
          <div className="flex items-center space-x-2 text-gray-600">
            <span>{getReadingProgress()}% read</span>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="px-4 py-2 border-b">
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm text-gray-600">Reading Progress</span>
          <span className="text-sm font-medium text-gray-900">
            {getReadingProgress()}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-green-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${getReadingProgress()}%` }}
          />
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage <= 1}
            className="p-2 text-gray-600 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeftIcon className="h-5 w-5" />
          </button>
          
          <span className="text-sm text-gray-700">
            Page {currentPage} of {numPages || 0}
          </span>
          
          <button
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage >= (numPages || 1)}
            className="p-2 text-gray-600 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronRightIcon className="h-5 w-5" />
          </button>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={handleZoomOut}
            className="p-2 text-gray-600 hover:text-gray-900"
          >
            <MagnifyingGlassMinusIcon className="h-5 w-5" />
          </button>
          
          <span className="text-sm text-gray-700 min-w-[50px] text-center">
            {Math.round(scale * 100)}%
          </span>
          
          <button
            onClick={handleZoomIn}
            className="p-2 text-gray-600 hover:text-gray-900"
          >
            <MagnifyingGlassPlusIcon className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* PDF Document */}
      <div 
        ref={pageContainer}
        className="flex-1 overflow-auto p-4 bg-gray-50"
        onScroll={handleScroll}
      >
        {pdfUrl && (
          <div className="flex justify-center">
            <Document
              file={pdfUrl}
              onLoadSuccess={handleDocumentLoadSuccess}
              onLoadError={handleDocumentLoadError}
              loading={<LoadingSpinner size="lg" />}
            >
              <Page
                pageNumber={currentPage}
                scale={scale}
                loading={<LoadingSpinner size="lg" />}
                renderTextLayer={false}
                renderAnnotationLayer={false}
              />
            </Document>
          </div>
        )}
      </div>

      {/* Page Navigation */}
      {numPages && numPages > 1 && (
        <div className="p-4 border-t">
          <div className="flex items-center justify-center space-x-2">
            {Array.from({ length: Math.min(numPages, 10) }, (_, i) => {
              const pageNum = i + 1;
              const isVisited = pageTracking.has(pageNum);
              const isCurrent = pageNum === currentPage;
              
              return (
                <button
                  key={pageNum}
                  onClick={() => handlePageChange(pageNum)}
                  className={`w-8 h-8 text-sm rounded-full transition-colors ${
                    isCurrent
                      ? 'bg-blue-600 text-white'
                      : isVisited
                      ? 'bg-green-100 text-green-700 hover:bg-green-200'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {pageNum}
                </button>
              );
            })}
            {numPages > 10 && (
              <span className="text-sm text-gray-500">
                ... and {numPages - 10} more pages
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default PDFViewer;