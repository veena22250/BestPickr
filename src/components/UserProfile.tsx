import * as React from 'react';
import { getAuth } from 'firebase/auth';
import { ToastContainer, toast } from 'react-toastify';
import { LogOut } from 'lucide-react';
import 'react-toastify/dist/ReactToastify.css';

interface UserData {
  uid: string;
  displayName: string | null;
  email: string | null;
  phoneNumber: string | null;
  photoURL: string | null;
  joinDate: string;
  address?: string;
}

interface BasePreference {
  id: string;
  label: string;
  enabled: boolean;
  description?: string;
  type?: 'toggle' | 'select' | 'multiselect' | 'range' | 'text';
  options?: { label: string; value: string }[];
  value?: any;
  min?: number;
  max?: number;
}

interface UserPreference extends BasePreference {
  category: 'grocery' | 'ride' | 'ecommerce' | 'notifications';
}

interface UserProfileProps {
  onLogout: () => void;
}

const defaultPreferences: UserPreference[] = [
  // Grocery Preferences
  {
    id: 'preferredGroceryCategories',
    label: 'Preferred Grocery Categories',
    enabled: true,
    description: 'Select your preferred grocery categories',
    type: 'multiselect',
    category: 'grocery',
    options: [
      { label: 'Fruits & Vegetables', value: 'fruits-veg' },
      { label: 'Dairy & Eggs', value: 'dairy' },
      { label: 'Snacks & Branded Foods', value: 'snacks' },
      { label: 'Beverages', value: 'beverages' },
      { label: 'Personal Care', value: 'personal-care' },
      { label: 'Household Care', value: 'household' },
    ]
  },
  {
    id: 'deliveryTimePreference',
    label: 'Preferred Delivery Time',
    enabled: true,
    description: 'When do you usually prefer your groceries?',
    type: 'select',
    category: 'grocery',
    options: [
      { label: 'Morning (8AM - 12PM)', value: 'morning' },
      { label: 'Afternoon (12PM - 4PM)', value: 'afternoon' },
      { label: 'Evening (4PM - 8PM)', value: 'evening' },
      { label: 'Night (8PM - 12AM)', value: 'night' },
    ]
  },
  {
    id: 'priceSensitivity',
    label: 'Price Sensitivity',
    enabled: true,
    description: 'How important is price for your grocery purchases?',
    type: 'range',
    category: 'grocery',
    min: 1,
    max: 5
  },

  // Ride Preferences
  {
    id: 'preferredRideType',
    label: 'Preferred Ride Type',
    enabled: true,
    description: 'Your go-to ride option',
    type: 'select',
    category: 'ride',
    options: [
      { label: 'Bike', value: 'bike' },
      { label: 'Auto', value: 'auto' },
      { label: 'Sedan', value: 'sedan' },
      { label: 'SUV', value: 'suv' },
      { label: 'Premium', value: 'premium' },
    ]
  },
  {
    id: 'safetyImportance',
    label: 'Safety Priority',
    enabled: true,
    description: 'How important are safety features to you?',
    type: 'range',
    category: 'ride',
    min: 1,
    max: 5
  },
  {
    id: 'minDriverRating',
    label: 'Minimum Driver Rating',
    enabled: true,
    description: 'Lowest rating you\'d accept for a driver',
    type: 'range',
    category: 'ride',
    min: 1,
    max: 5
  },

  // E-commerce Preferences
  {
    id: 'preferredCategories',
    label: 'Shopping Categories',
    enabled: true,
    description: 'What do you usually shop for?',
    type: 'multiselect',
    category: 'ecommerce',
    options: [
      { label: 'Electronics', value: 'electronics' },
      { label: 'Fashion', value: 'fashion' },
      { label: 'Home & Kitchen', value: 'home' },
      { label: 'Beauty', value: 'beauty' },
      { label: 'Books', value: 'books' },
      { label: 'Toys & Games', value: 'toys' },
    ]
  },
  {
    id: 'deliverySpeedPreference',
    label: 'Delivery Speed',
    enabled: true,
    description: 'How quickly do you need your items?',
    type: 'select',
    category: 'ecommerce',
    options: [
      { label: 'Same/Next Day', value: 'fast' },
      { label: '2-3 Days', value: 'medium' },
      { label: 'No Rush', value: 'slow' },
    ]
  },
  {
    id: 'returnPolicyImportance',
    label: 'Return Policy Importance',
    enabled: true,
    description: 'How important is a good return policy?',
    type: 'range',
    category: 'ecommerce',
    min: 1,
    max: 5
  },

  // Notification Preferences
  {
    id: 'emailNotifications',
    label: 'Email Notifications',
    enabled: true,
    description: 'Receive email notifications',
    type: 'toggle',
    category: 'notifications'
  },
  {
    id: 'pushNotifications',
    label: 'Push Notifications',
    enabled: true,
    description: 'Receive push notifications on your device',
    type: 'toggle',
    category: 'notifications'
  },
  {
    id: 'smsNotifications',
    label: 'SMS Notifications',
    enabled: false,
    description: 'Receive SMS notifications (standard rates may apply)',
    type: 'toggle',
    category: 'notifications'
  },
  {
    id: 'locationServices',
    label: 'Location Services',
    enabled: true,
    description: 'Allow access to your location for better service',
    type: 'toggle',
    category: 'notifications'
  },
  {
    id: 'personalizedAds',
    label: 'Personalized Ads',
    enabled: true,
    description: 'See ads that are more relevant to you',
    type: 'toggle',
    category: 'notifications'
  }
];

const UserProfile: React.FC<UserProfileProps> = ({ onLogout }) => {
  const [activeTab, setActiveTab] = React.useState<'profile' | 'preferences'>('profile');
  const [user, setUser] = React.useState<UserData | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  // Editable profile state
  const [editMode, setEditMode] = React.useState(false);
  const [editData, setEditData] = React.useState<Omit<UserData, 'uid' | 'joinDate'>>(null);
  const [selectedImage, setSelectedImage] = React.useState<string | null>(null);
  const [imageFile, setImageFile] = React.useState<File | null>(null);
  const [preferences, setPreferences] = React.useState<UserPreference[]>(defaultPreferences);
  const auth = getAuth();

  // Load user data on component mount
  React.useEffect(() => {
    const currentUser = auth.currentUser;
    if (currentUser) {
      setUser({
        uid: currentUser.uid,
        displayName: currentUser.displayName,
        email: currentUser.email,
        phoneNumber: currentUser.phoneNumber,
        photoURL: currentUser.photoURL,
        joinDate: currentUser.metadata?.creationTime || new Date().toISOString(),
      });
      setEditData({
        displayName: currentUser.displayName,
        email: currentUser.email,
        phoneNumber: currentUser.phoneNumber,
        photoURL: currentUser.photoURL,
        address: '', // Add address if you want to load it from somewhere
      });
    }
    loadPreferences();
  }, []);

  // Load preferences from session storage
  const loadPreferences = () => {
    try {
      const savedPreferences = sessionStorage.getItem('userPreferences');
      if (savedPreferences) {
        setPreferences(JSON.parse(savedPreferences));
      }
    } catch (error) {
      console.error('Error loading preferences:', error);
      toast.error('Failed to load preferences');
    } finally {
      setIsLoading(false);
    }
  };

  // Save preferences to session storage
  const savePreferences = () => {
    try {
      sessionStorage.setItem('userPreferences', JSON.stringify(preferences));
      toast.success('Preferences saved successfully!');
    } catch (error) {
      console.error('Error saving preferences:', error);
      toast.error('Failed to save preferences');
    }
  };

  // Update a preference value
  const updatePreference = (id: string, value: any) => {
    setPreferences(prevPrefs => 
      prevPrefs.map(pref => 
        pref.id === id 
          ? { ...pref, value, enabled: pref.type === 'toggle' ? value : pref.enabled } 
          : pref
      )
    );
  };

  // Render preference input based on type
  const renderPreferenceInput = (pref: UserPreference) => {
    switch (pref.type) {
      case 'toggle':
        return (
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={pref.enabled}
              onChange={(e) => updatePreference(pref.id, e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-700 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-lavender-400"></div>
          </label>
        );

      case 'select':
        return (
          <select
            className="bg-gray-700 text-white text-sm rounded-lg block w-full p-2.5 focus:ring-lavender-400 focus:border-lavender-400"
            value={pref.value}
            onChange={(e) => updatePreference(pref.id, e.target.value)}
          >
            {pref.options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'multiselect':
        return (
          <div className="space-y-2">
            {pref.options?.map((option) => (
              <div key={option.value} className="flex items-center">
                <input
                  id={`${pref.id}-${option.value}`}
                  type="checkbox"
                  checked={pref.value?.includes(option.value) || false}
                  onChange={(e) => {
                    const newValue = e.target.checked
                      ? [...(pref.value || []), option.value]
                      : (pref.value || []).filter((v: string) => v !== option.value);
                    updatePreference(pref.id, newValue);
                  }}
                  className="h-4 w-4 text-lavender-400 focus:ring-lavender-400 border-gray-600 rounded"
                />
                <label htmlFor={`${pref.id}-${option.value}`} className="ml-2 text-sm text-gray-300">
                  {option.label}
                </label>
              </div>
            ))}
          </div>
        );

      case 'range':
        return (
          <div className="w-full">
            <input
              type="range"
              min={pref.min || 1}
              max={pref.max || 5}
              value={pref.value || 3}
              onChange={(e) => updatePreference(pref.id, parseInt(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>1</span>
              <span>2</span>
              <span>3</span>
              <span>4</span>
              <span>5</span>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  // Group preferences by category
  const preferencesByCategory = React.useMemo(() => {
    return preferences.reduce((acc, pref) => {
      if (!acc[pref.category]) {
        acc[pref.category] = [];
      }
      acc[pref.category].push(pref);
      return acc;
    }, {} as Record<string, UserPreference[]>);
  }, [preferences]);

  // Category display names
  const categoryNames = {
    grocery: 'Grocery',
    ride: 'Ride',
    ecommerce: 'E-commerce',
    notifications: 'Notifications'
  };

  // State for active category tab
  const [activeCategory, setActiveCategory] = React.useState<keyof typeof categoryNames>('grocery');

  // Render preferences section
  const renderPreferences = () => {
    if (isLoading) {
      return <div className="text-center py-8">Loading preferences...</div>;
    }

    return (
      <div className="space-y-6">
        {/* Category Tabs */}
        <div className="border-b border-gray-700">
          <nav className="-mb-px flex space-x-8">
            {(Object.keys(categoryNames) as Array<keyof typeof categoryNames>).map((category) => (
              <button
                key={category}
                onClick={() => setActiveCategory(category)}
                className={`${
                  activeCategory === category
                    ? 'border-lavender-400 text-lavender-400'
                    : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-500'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                {categoryNames[category]}
              </button>
            ))}
          </nav>
        </div>

        {/* Active Category Content */}
        <div className="space-y-4">
          {preferencesByCategory[activeCategory]?.map((pref) => (
            <div key={pref.id} className="bg-gray-700/30 rounded-lg p-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex-1">
                  <h3 className="text-white font-medium">{pref.label}</h3>
                  {pref.description && (
                    <p className="text-gray-400 text-sm mt-1">{pref.description}</p>
                  )}
                </div>
                <div className="sm:w-64">
                  {renderPreferenceInput(pref)}
                </div>
              </div>
            </div>
          ))}
          
          {!preferencesByCategory[activeCategory]?.length && (
            <div className="text-center py-8 text-gray-400">
              No preferences found in this category.
            </div>
          )}
        </div>

        {/* Save Button */}
        <div className="sticky bottom-0 bg-gray-800/80 backdrop-blur-sm py-4 border-t border-gray-700 -mx-6 px-6 mt-8">
          <div className="flex justify-end">
            <button
              onClick={savePreferences}
              className="px-6 py-2.5 bg-lavender-500 text-white rounded-lg hover:bg-lavender-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-lavender-500 transition-colors font-medium"
            >
              Save All Preferences
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Render profile section
  const renderProfile = () => {
    if (isLoading) {
      return (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-lavender-400"></div>
        </div>
      );
    }

    if (!user || !editData) {
      return (
        <div className="text-center py-12">
          <p className="text-gray-400">No user data available</p>
        </div>
      );
    }

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      const { name, value } = e.target;
      setEditData((prev) => prev ? { ...prev, [name]: value } : prev);
    };

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files[0]) {
        const file = e.target.files[0];
        setImageFile(file);
        const reader = new FileReader();
        reader.onload = (ev) => {
          setSelectedImage(ev.target?.result as string);
        };
        reader.readAsDataURL(file);
      }
    };

    const handleSave = () => {
      setUser((prev) => prev ? {
        ...prev,
        displayName: editData.displayName,
        phoneNumber: editData.phoneNumber,
        address: editData.address,
        photoURL: selectedImage || prev.photoURL,
      } : prev);
      setEditMode(false);
      toast.success('Profile updated locally!');
      // TODO: Integrate with Firebase updateProfile and storage for real saving
    };

    return (
      <div className="space-y-6">
        {/* Profile Header */}
        <div className="flex flex-col items-center space-y-4">
          <div className="relative group">
            {(selectedImage || user.photoURL) ? (
              <img
                src={selectedImage || user.photoURL}
                alt={editData.displayName || 'User'}
                className="h-32 w-32 rounded-full object-cover border-4 border-lavender-400"
              />
            ) : (
              <div className="h-32 w-32 rounded-full bg-lavender-500 flex items-center justify-center text-white text-4xl font-bold">
                {editData.displayName ? editData.displayName.charAt(0).toUpperCase() : 'U'}
              </div>
            )}
            {editMode && (
              <label className="absolute bottom-0 right-0 bg-lavender-400 text-white rounded-full p-2 cursor-pointer shadow-lg group-hover:scale-105 transition-transform">
                <input type="file" accept="image/*" className="hidden" onChange={handleImageChange} />
                <span className="text-xs">Edit</span>
              </label>
            )}
          </div>
          <div className="text-center">
            {editMode ? (
              <input
                type="text"
                name="displayName"
                value={editData.displayName || ''}
                onChange={handleInputChange}
                className="text-2xl font-bold text-white bg-gray-800 rounded px-2 py-1 text-center"
                placeholder="Full Name"
              />
            ) : (
              <h2 className="text-2xl font-bold text-white">{user.displayName || 'User'}</h2>
            )}
            <p className="text-gray-400">{user.email}</p>
          </div>
        </div>

        {/* Account Details */}
        <div className="bg-gray-700/30 rounded-xl p-6 space-y-4">
          <h3 className="text-lg font-semibold text-white mb-4">Account Details</h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
            <dt className="text-sm font-medium text-gray-400">Full name</dt>
            <dd className="text-sm text-gray-200 md:col-span-2">
              {editMode ? (
                <input
                  type="text"
                  name="displayName"
                  value={editData.displayName || ''}
                  onChange={handleInputChange}
                  className="w-full bg-gray-800 rounded px-2 py-1 text-white"
                  placeholder="Full Name"
                />
              ) : (
                user.displayName || 'Not set'
              )}
            </dd>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
            <dt className="text-sm font-medium text-gray-400">Email address</dt>
            <dd className="text-sm text-gray-200 md:col-span-2">
              {user.email || 'Not set'}
            </dd>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
            <dt className="text-sm font-medium text-gray-400">Phone number</dt>
            <dd className="text-sm text-gray-200 md:col-span-2">
              {editMode ? (
                <input
                  type="text"
                  name="phoneNumber"
                  value={editData.phoneNumber || ''}
                  onChange={handleInputChange}
                  className="w-full bg-gray-800 rounded px-2 py-1 text-white"
                  placeholder="Phone Number"
                />
              ) : (
                user.phoneNumber || 'Not set'
              )}
            </dd>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
            <dt className="text-sm font-medium text-gray-400">Address</dt>
            <dd className="text-sm text-gray-200 md:col-span-2">
              {editMode ? (
                <textarea
                  name="address"
                  value={editData.address || ''}
                  onChange={handleInputChange}
                  className="w-full bg-gray-800 rounded px-2 py-1 text-white"
                  placeholder="Address"
                  rows={2}
                />
              ) : (
                user.address || 'Not set'
              )}
            </dd>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
            <dt className="text-sm font-medium text-gray-400">Member since</dt>
            <dd className="text-sm text-gray-200 md:col-span-2">
              {new Date(user.joinDate).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </dd>
          </div>

          <div className="flex space-x-4 pt-4 border-t border-gray-600 mt-6">
            {editMode ? (
              <>
                <button
                  onClick={handleSave}
                  className="flex-1 flex items-center justify-center px-4 py-2 bg-lavender-500 hover:bg-lavender-600 text-white rounded-md transition-colors"
                >
                  Save
                </button>
                <button
                  onClick={() => { setEditMode(false); setSelectedImage(null); setEditData({ ...editData, photoURL: user.photoURL }); }}
                  className="flex-1 flex items-center justify-center px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md transition-colors"
                >
                  Cancel
                </button>
              </>
            ) : (
              <button
                onClick={() => setEditMode(true)}
                className="w-full flex items-center justify-center px-4 py-2 bg-lavender-500 hover:bg-lavender-600 text-white rounded-md transition-colors"
              >
                Edit Profile
              </button>
            )}
            <button
              onClick={onLogout}
              className="flex-1 flex items-center justify-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Sign out
            </button>
          </div>
        </div>
      </div>
    );
  };


  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black p-4 md:p-8">
      <ToastContainer position="top-right" autoClose={3000} theme="dark" />
      <div className="max-w-4xl mx-auto">
        <div className="bg-gray-800/50 backdrop-blur-md rounded-xl shadow-xl overflow-hidden border border-gray-700/50">
          {/* Tabs */}
          <div className="border-b border-gray-700">
            <nav className="flex">
              <button
                onClick={() => setActiveTab('profile')}
                className={`${
                  activeTab === 'profile'
                    ? 'border-lavender-400 text-lavender-400'
                    : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-600'
                } flex-1 py-4 px-1 text-center border-b-2 font-medium text-sm transition-colors`}
              >
                Profile
              </button>
              <button
                onClick={() => setActiveTab('preferences')}
                className={`${
                  activeTab === 'preferences'
                    ? 'border-lavender-400 text-lavender-400'
                    : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-600'
                } flex-1 py-4 px-1 text-center border-b-2 font-medium text-sm transition-colors`}
              >
                Preferences
              </button>
            </nav>
          </div>
          
          {/* Content */}
          <div className="p-6">
            {activeTab === 'profile' ? renderProfile() : renderPreferences()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
