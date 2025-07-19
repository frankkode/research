import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { authApi } from '../../services/api';
import { toast } from 'react-hot-toast';
import LoadingSpinner from '../common/LoadingSpinner';
import { 
  CheckCircleIcon, 
  ExclamationTriangleIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

const ConsentForm: React.FC = () => {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [agreed, setAgreed] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!agreed) {
      toast.error('Please read and agree to the consent form to continue');
      return;
    }

    setIsSubmitting(true);
    
    try {
      const response = await authApi.submitConsent(agreed);
      
      // Update user state with the new consent status
      if (response.data.user) {
        // Update localStorage to reflect the change
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        // Force a page refresh to update the auth context
        window.location.href = '/dashboard';
      }
      
      toast.success('Consent submitted successfully!');
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to submit consent form');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white shadow rounded-lg">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mr-4">
                <DocumentTextIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Informed Consent</h1>
                <p className="text-gray-600">Linux Learning Study - Participant {user?.participant_id}</p>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="px-6 py-6">
            <div className="prose max-w-none">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Study Title: Comparing Learning Effectiveness: Interactive AI Assistance vs. Traditional Documentation for Linux Command Learning
              </h2>

              <div className="space-y-6 text-gray-700">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Principal Investigator:</h3>
                  <p>Research:Mr, Frank Masabo<br />
                  Computer Science Department<br />
                  International University of Applied Sciences</p>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Study Purpose:</h3>
                  <p>You are being invited to participate in a research study investigating how different learning methods affect the acquisition and retention of Linux command knowledge. This study compares learning through interactive AI assistance versus traditional PDF documentation.</p>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">What You Will Be Asked To Do:</h3>
                  <ul className="list-disc list-inside space-y-2">
                    <li><strong>Duration:</strong> Approximately 45-60 minutes</li>
                    <li><strong>Format:</strong> Online study session</li>
                    <li><strong>Components:</strong> Learning phase, practice/interaction phase, and two quiz assessments</li>
                  </ul>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Study Procedures:</h3>
                  <ol className="list-decimal list-inside space-y-2">
                    <li><strong>Pre-Assessment Quiz:</strong> Test your current Linux knowledge (5-10 minutes)</li>
                    <li><strong>Learning Session:</strong> Study Linux commands using your assigned method (20-30 minutes)</li>
                    <li><strong>Post-Assessment Quiz:</strong> Test your knowledge after learning (5-10 minutes)</li>
                    <li><strong>24-Hour Follow-up:</strong> Transfer quiz to test knowledge retention (5-10 minutes)</li>
                  </ol>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Risks and Benefits:</h3>
                  <p><strong>Risks:</strong> There are no significant risks associated with this study. You may experience mild fatigue from computer use.</p>
                  <p><strong>Benefits:</strong> You will learn useful Linux commands and contribute to research on effective learning methods.</p>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Confidentiality:</h3>
                  <p>All data collected will be kept confidential and used only for research purposes. Your responses will be identified only by a participant ID number. No personal identifying information will be included in any reports or publications.</p>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Voluntary Participation:</h3>
                  <p>Your participation is entirely voluntary. You may withdraw from the study at any time without penalty. You may also skip any questions you do not wish to answer.</p>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Data Storage:</h3>
                  <p>Study data will be stored securely and deleted after the research is completed and published (approximately 2 years).</p>
                </div>
              </div>

              {/* Consent Agreement */}
              <div className="mt-8 p-6 bg-gray-50 rounded-lg border">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    {agreed ? (
                      <CheckCircleIcon className="h-6 w-6 text-green-500" />
                    ) : (
                      <ExclamationTriangleIcon className="h-6 w-6 text-yellow-500" />
                    )}
                  </div>
                  <div className="flex-1">
                    <label className="flex items-start space-x-3 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={agreed}
                        onChange={(e) => setAgreed(e.target.checked)}
                        className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <div className="text-sm text-gray-700">
                        <p className="font-medium">I agree to participate in this study</p>
                        <p className="mt-1">
                          I have read and understood the information provided above. I understand that my participation is voluntary and that I can withdraw at any time. I consent to participate in this research study.
                        </p>
                      </div>
                    </label>
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <div className="mt-6 flex justify-end space-x-4">
                <button
                  type="button"
                  onClick={() => navigate('/dashboard')}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={!agreed || isSubmitting}
                  className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <>
                      <LoadingSpinner size="sm" />
                      <span className="ml-2">Submitting...</span>
                    </>
                  ) : (
                    'Continue to Study'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConsentForm;