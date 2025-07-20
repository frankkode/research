import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import LoadingSpinner from '../common/LoadingSpinner';
import GoogleSignIn from './GoogleSignIn';
import { RegisterData } from '../../types';
import { generateParticipantId, assignRandomGroup } from '../../utils/studyHelpers';

interface RegisterFormData extends RegisterData {
  password_confirm: string;
}

const RegisterForm: React.FC = () => {
  const { register: registerUser, googleAuth } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    getValues,
    formState: { errors }
  } = useForm<RegisterFormData>();

  const password = watch('password');

  useEffect(() => {
    // Auto-generate and prefill participant ID and study group
    const participantId = generateParticipantId();
    const studyGroup = assignRandomGroup();
    
    setValue('participant_id', participantId);
    setValue('study_group', studyGroup);
  }, [setValue]);

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    try {
      await registerUser(data);
      toast.success('Registration successful!');
      navigate('/dashboard');
    } catch (error: any) {
      const errorMessage = error.response?.data?.email?.[0] || 
                          error.response?.data?.username?.[0] || 
                          error.response?.data?.participant_id?.[0] ||
                          error.response?.data?.detail ||
                          'Registration failed';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSuccess = async (token: string) => {
    setIsLoading(true);
    try {
      const studyGroup = getValues('study_group') || assignRandomGroup();
      const response = await googleAuth(token, studyGroup);
      
      toast.success(response.created ? 'Account created successfully!' : 'Login successful!');
      navigate('/dashboard');
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Google authentication failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleError = (error: string) => {
    toast.error(error);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Join the Research Study
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Create your account to participate in the Linux learning study
          </p>
          <p className="mt-1 text-center text-xs text-green-600">
            Your participant ID and study group will be automatically assigned
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <input
                {...register('email', {
                  required: 'Email is required',
                  pattern: {
                    value: /^\S+@\S+$/i,
                    message: 'Invalid email address'
                  }
                })}
                type="email"
                className="mt-1 input"
                placeholder="Enter your email address"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Username
              </label>
              <input
                {...register('username', {
                  required: 'Username is required',
                  minLength: {
                    value: 3,
                    message: 'Username must be at least 3 characters'
                  },
                  pattern: {
                    value: /^[a-zA-Z0-9_]+$/,
                    message: 'Username can only contain letters, numbers, and underscores'
                  }
                })}
                type="text"
                className="mt-1 input"
                placeholder="Choose a username"
              />
              {errors.username && (
                <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="participant_id" className="block text-sm font-medium text-gray-700">
                Participant ID
              </label>
              <input
                {...register('participant_id', {
                  required: 'Participant ID is required',
                  pattern: {
                    value: /^[A-Za-z0-9_-]+$/,
                    message: 'Participant ID can only contain letters, numbers, hyphens, and underscores'
                  }
                })}
                type="text"
                className="mt-1 input bg-gray-50"
                placeholder="Auto-generated participant ID"
                readOnly
              />
              {errors.participant_id && (
                <p className="mt-1 text-sm text-red-600">{errors.participant_id.message}</p>
              )}
              <p className="mt-1 text-xs text-green-600">
                ✓ Auto-generated unique participant ID
              </p>
            </div>

            <div>
              <label htmlFor="study_group" className="block text-sm font-medium text-gray-700">
                Study Group Assignment
              </label>
              <select
                {...register('study_group', {
                  required: 'Study group is required'
                })}
                className="mt-1 input bg-gray-50"
                disabled
              >
                <option value="">Auto-assigning group...</option>
                <option value="PDF">PDF Group</option>
                <option value="CHATGPT">ChatGPT Group</option>
              </select>
              {errors.study_group && (
                <p className="mt-1 text-sm text-red-600">{errors.study_group.message}</p>
              )}
              <p className="mt-1 text-xs text-green-600">
                ✓ Randomly assigned to ensure balanced groups
              </p>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                {...register('password', {
                  required: 'Password is required',
                  minLength: {
                    value: 8,
                    message: 'Password must be at least 8 characters'
                  }
                })}
                type="password"
                className="mt-1 input"
                placeholder="Create a password"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password_confirm" className="block text-sm font-medium text-gray-700">
                Confirm Password
              </label>
              <input
                {...register('password_confirm', {
                  required: 'Please confirm your password',
                  validate: (value) => value === password || 'Passwords do not match'
                })}
                type="password"
                className="mt-1 input"
                placeholder="Confirm your password"
              />
              {errors.password_confirm && (
                <p className="mt-1 text-sm text-red-600">{errors.password_confirm.message}</p>
              )}
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="btn btn-primary w-full flex justify-center items-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <LoadingSpinner size="sm" />
              ) : (
                'Create Account'
              )}
            </button>
          </div>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-gray-50 text-gray-500">Or</span>
              </div>
            </div>

            <div className="mt-6">
              <GoogleSignIn
                onSuccess={handleGoogleSuccess}
                onError={handleGoogleError}
                text="Sign up with Google"
              />
            </div>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">
                Sign in
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RegisterForm;