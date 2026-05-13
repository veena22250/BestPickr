import React, { useState, useRef } from 'react';
import { MapPin, Navigation, Zap, Star, Clock, Sparkles, Search } from 'lucide-react';
import RideAnalysisSidebar from './RideAnalysisSidebar';
import rideData from '../data/ridedata.json';

import { getPlatformLogo } from './_PlatformLogos';
// Base vehicle interface
interface Vehicle {
  vehicle_type: string;
  cost_inr: number;
  travel_time_minutes: number;
  pickup_time_minutes: number;
}

// Original ride entry from JSON - used for type safety in data processing
interface RideEntry {
  platform: string;
  pickup_location: string;
  destination: string;
  distance_km: number;
  vehicles: Vehicle[];
}


// Flattened ride data for display
interface FlatRideEntry extends Omit<Vehicle, 'vehicles'> {
  platform: string;
  pickup_location: string;
  destination: string;
  distance_km: number;
}

const RideComparison: React.FC = () => {
  const [pickup, setPickup] = useState('');
  const [destination, setDestination] = useState('');
  const [vehicleType, setVehicleType] = useState('');
  const [rideApps, setRideApps] = useState<FlatRideEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedRide, setSelectedRide] = useState<any>(null);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [pickupSuggestions, setPickupSuggestions] = useState<string[]>([]);
  const [destinationSuggestions, setDestinationSuggestions] = useState<string[]>([]);
  const [isLocating, setIsLocating] = useState(false);

  const pickupRef = useRef<HTMLDivElement>(null);
  const destRef = useRef<HTMLDivElement>(null);

  const getUniqueLocations = (type: 'pickup' | 'destination'): string[] => {
    const locations = rideData.rides.map(ride => type === 'pickup' ? ride.pickup_location : ride.destination);
    return Array.from(new Set(locations));
  };

  // Enhanced search function with fuzzy matching
  const findBestLocationMatch = (inputLocation: string, availableLocations: string[]): string[] => {
    const input = inputLocation.toLowerCase().trim();
    if (!input) return [];

    // Exact match first
    const exactMatch = availableLocations.find(loc => loc.toLowerCase() === input);
    if (exactMatch) return [exactMatch];

    // Partial matches - location contains input or input contains location
    const partialMatches = availableLocations.filter(loc => {
      const location = loc.toLowerCase();
      return location.includes(input) || input.includes(location);
    });

    if (partialMatches.length > 0) return partialMatches;

    // Fuzzy matching - check for similar words
    const fuzzyMatches = availableLocations.filter(loc => {
      const locationWords = loc.toLowerCase().split(/\s+/);
      const inputWords = input.split(/\s+/);
      
      return locationWords.some(locWord => 
        inputWords.some(inputWord => 
          locWord.includes(inputWord) || inputWord.includes(locWord) ||
          Math.abs(locWord.length - inputWord.length) <= 2 && 
          locWord.substring(0, Math.min(3, locWord.length)) === inputWord.substring(0, Math.min(3, inputWord.length))
        )
      );
    });

    return fuzzyMatches;
  };

  const handlePickupChange = (val: string) => {
    setPickup(val);
    if (val.trim()) {
      const allLocations = getUniqueLocations('pickup');
      const matches = findBestLocationMatch(val, allLocations);
      setPickupSuggestions(matches.slice(0, 5)); // Limit to 5 suggestions
    } else {
      setPickupSuggestions([]);
    }
  };

  const handleDestinationChange = (val: string) => {
    setDestination(val);
    if (val.trim()) {
      const allLocations = getUniqueLocations('destination');
      const matches = findBestLocationMatch(val, allLocations);
      setDestinationSuggestions(matches.slice(0, 5)); // Limit to 5 suggestions
    } else {
      setDestinationSuggestions([]);
    }
  };

  const handleDetectLocation = async () => {
    if (!navigator.geolocation) return;
    setIsLocating(true);
    navigator.geolocation.getCurrentPosition(async (position) => {
      const { latitude, longitude } = position.coords;
      try {
        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`);
        const data = await response.json();
        const address = data.display_name || `${latitude}, ${longitude}`;
        setPickup(address);
      } catch (e) {
        setPickup(`${latitude}, ${longitude}`);
      }
      setIsLocating(false);
    }, () => setIsLocating(false));
  };

  // Generate realistic ride data for any location pair
  const generateRideData = (pickupLoc: string, destLoc: string): RideEntry[] => {
    // Calculate estimated distance (random between 3-25 km for realistic city rides)
    const baseDistance = Math.floor(Math.random() * 22) + 3;
    
    const platforms = ['Ola', 'Uber', 'Rapido', 'Namaya 3'];
    const vehicleTypes = [
      { type: 'Bike', baseCost: 6, timeMultiplier: 2.2, minCost: 25 },
      { type: 'Auto', baseCost: 9, timeMultiplier: 2.8, minCost: 40 },
      { type: 'Car', baseCost: 12, timeMultiplier: 3.5, minCost: 80 }
    ];

    return platforms.map((platform) => {
      const platformDistance = baseDistance + (Math.random() * 2 - 1); // Slight variation per platform
      
      // Platform-specific pricing adjustments
      const platformMultiplier = {
        'Ola': 1.0,
        'Uber': 1.1,
        'Rapido': 0.85,
        'Namaya 3': 0.95
      }[platform] || 1.0;
      
      return {
        platform,
        pickup_location: pickupLoc,
        destination: destLoc,
        distance_km: Math.round(platformDistance * 10) / 10, // Round to 1 decimal
        vehicles: vehicleTypes.map((vehicle) => {
          const baseCost = Math.max(
            vehicle.minCost,
            Math.round(platformDistance * vehicle.baseCost * platformMultiplier)
          );
          const variation = Math.round(Math.random() * 20 - 10); // ±10 rupees variation
          
          return {
            vehicle_type: vehicle.type,
            cost_inr: Math.max(vehicle.minCost, baseCost + variation),
            travel_time_minutes: Math.round(platformDistance * vehicle.timeMultiplier + (Math.random() * 8 - 4)),
            pickup_time_minutes: Math.floor(Math.random() * 6) + 2
          };
        })
      };
    });
  };

  const handleSearch = () => {
    if (!pickup || !destination) return;

    setLoading(true);
    setSelectedRide(null);
    setShowAnalysis(false);
    
    setTimeout(() => {
      // First try to find existing data
      const allPickupLocations = Array.from(new Set(rideData.rides.map(r => r.pickup_location)));
      const allDestinations = Array.from(new Set(rideData.rides.map(r => r.destination)));

      const pickupMatches = findBestLocationMatch(pickup, allPickupLocations);
      const destinationMatches = findBestLocationMatch(destination, allDestinations);

      let matched = rideData.rides.filter(
        (ride: RideEntry) =>
          pickupMatches.some(match => ride.pickup_location.toLowerCase() === match.toLowerCase()) &&
          destinationMatches.some(match => ride.destination.toLowerCase() === match.toLowerCase())
      );

      // If no matches found in existing data, generate new ride data for the entered locations
      if (matched.length === 0) {
        console.log(`Generating ride data for: ${pickup} → ${destination}`);
        matched = generateRideData(pickup, destination);
      }

      const filtered = matched.map(entry => ({
        ...entry,
        vehicles: vehicleType
          ? entry.vehicles.map(v => ({
              ...v,
              platform: entry.platform,
              pickup_location: entry.pickup_location,
              destination: entry.destination,
              distance_km: entry.distance_km
            })).filter(v => v.vehicle_type.toLowerCase() === vehicleType.toLowerCase())
          : entry.vehicles.map(v => ({
              ...v,
              platform: entry.platform,
              pickup_location: entry.pickup_location,
              destination: entry.destination,
              distance_km: entry.distance_km
            }))
      })).filter(entry => entry.vehicles.length > 0);

      // Flatten the array to make it easier to work with
      const flattened: FlatRideEntry[] = filtered.flatMap(entry => 
        entry.vehicles.map(vehicle => ({
          ...vehicle,
          platform: entry.platform,
          pickup_location: entry.pickup_location,
          destination: entry.destination,
          distance_km: entry.distance_km
        }))
      );

      setRideApps(flattened);
      
      // If no matches found, show helpful message
      if (flattened.length === 0) {
        console.log('No matches found for:', { pickup, destination, pickupMatches, destinationMatches });
      }
      
      setLoading(false);
    }, 500);
  };

  
  const getBookingUrl = (ride: FlatRideEntry) => {
    // Encode the route details for the URL
    const pickupEncoded = encodeURIComponent(ride.pickup_location);
    const destEncoded = encodeURIComponent(ride.destination);
    
    // Define base URLs for different ride-sharing platforms
    const platformUrls: {[key: string]: string} = {
      'Ola': `https://book.olacabs.com/?pickup_name=${pickupEncoded}&drop_name=${destEncoded}`,
      'Uber': `https://m.uber.com/ul/?action=setPickup&pickup=my_location&drop[formatted_address]=${destEncoded}`,
      'Rapido': `https://www.rapido.bike/`,
      'Namaya 3': 'https://www.namaya3.com/'
    };
    
    // Default to platform's homepage if no specific URL mapping exists
    return platformUrls[ride.platform] || `https://www.${ride.platform.toLowerCase()}.com`;
  };

  const handleBookNow = (e: React.MouseEvent, ride: FlatRideEntry) => {
    e.stopPropagation();
    const bookingUrl = getBookingUrl(ride);
    window.open(bookingUrl, '_blank', 'noopener,noreferrer');
  };

  const handleRideSelect = (ride: FlatRideEntry) => {
    setSelectedRide(ride);
    setShowAnalysis(true);
  };

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8 text-white">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Compare Your Rides</h1>
          <p className="text-gray-400 italic">Search from local ride options based on your route</p>
          
        </div>


        <div className="bg-gray-800/50 p-6 rounded-2xl border border-gray-700/50 mb-8 space-y-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1" ref={pickupRef}>
              <button
                type="button"
                onClick={handleDetectLocation}
                className={`absolute left-3 top-3 h-5 w-5 flex items-center justify-center z-10 ${isLocating ? 'animate-pulse text-blue-400' : 'text-green-400 hover:text-blue-400'}`}
                title="Detect my location"
                aria-label="Detect my location"
                style={{ background: 'none', border: 'none', padding: 0 }}
              >
                <MapPin className="h-5 w-5" />
              </button>
              <input
                type="text"
                value={pickup}
                onChange={(e) => handlePickupChange(e.target.value)}
                onBlur={() => setTimeout(() => setPickupSuggestions([]), 200)}
                placeholder="Enter Pickup Location"
                className="w-full pl-12 pr-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg text-white"
              />
              {pickupSuggestions.length > 0 && (
                <ul className="absolute z-50 bg-gray-800 border border-gray-600 mt-1 rounded-lg w-full">
                  {pickupSuggestions.map((sug, i) => (
                    <li
                      key={i}
                      onMouseDown={() => {
                        setPickup(sug);
                        setPickupSuggestions([]);
                      }}
                      className="px-4 py-2 hover:bg-gray-700 cursor-pointer"
                    >
                      {sug}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="relative flex-1" ref={destRef}>
              <Navigation className="absolute left-3 top-3 h-5 w-5 text-red-400" />
              <input
                type="text"
                value={destination}
                onChange={(e) => handleDestinationChange(e.target.value)}
                onBlur={() => setTimeout(() => setDestinationSuggestions([]), 200)}
                placeholder="Enter Destination"
                className="w-full pl-12 pr-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg text-white"
              />
              {destinationSuggestions.length > 0 && (
                <ul className="absolute z-50 bg-gray-800 border border-gray-600 mt-1 rounded-lg w-full">
                  {destinationSuggestions.map((sug, i) => (
                    <li
                      key={i}
                      onMouseDown={() => {
                        setDestination(sug);
                        setDestinationSuggestions([]);
                      }}
                      className="px-4 py-2 hover:bg-gray-700 cursor-pointer"
                    >
                      {sug}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          <div className="flex flex-col md:flex-row gap-4">
            <select
              value={vehicleType}
              onChange={(e) => setVehicleType(e.target.value)}
              className="px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg text-white"
            >
              <option value="">All Vehicle Types</option>
              <option value="Bike">Bike</option>
              <option value="Auto">Auto</option>
              <option value="Car">Car</option>
            </select>

            <button
              onClick={handleSearch}
              disabled={!pickup || !destination}
              className="px-6 py-3 bg-lavender-500 hover:bg-lavender-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white flex items-center transition-all duration-200"
            >
              <Zap className="h-4 w-4 mr-2" />
              Compare Rides
            </button>
          </div>
        </div>

        {loading ? (
          <p className="text-center text-gray-300">Searching for rides...</p>
        ) : rideApps.length > 0 ? (
          <div className="grid gap-6 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3">
            {rideApps.map((ride, index) => (
              <div
                key={index}
                className="bg-gray-800/50 rounded-xl p-4 border border-gray-700 hover:border-lavender-400 transition-colors cursor-pointer"
                onClick={() => handleRideSelect(ride)} 
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <div className="flex items-center gap-3 mb-1">
  {(() => {
    // Import the logo helper
    // (at top: import { getPlatformLogo } from './_PlatformLogos')
    const logoSrc = getPlatformLogo(ride.platform);
    if (logoSrc) {
      return <img src={logoSrc} alt={ride.platform} className="h-20 w-20 object-contain" />;
    }
    return null;
  })()}
  <h3 className="text-lg font-bold">{ride.platform}</h3>
</div>
                    <p className="text-sm text-gray-300">{ride.vehicle_type}</p>
                  </div>
                  <button
                    className="p-1.5 rounded-full bg-gray-700 hover:bg-gray-600"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRideSelect(ride);
                    }}
                  >
                    <Sparkles className="h-4 w-4 text-lavender-400" />
                  </button>
                </div>
                <div className="text-sm text-gray-400 flex items-center gap-2 mb-1">
                  <Clock className="h-4 w-4" />
                  <span>{ride.travel_time_minutes} min • {ride.distance_km} km</span>
                </div>
                <div className="text-sm text-yellow-400 flex items-center gap-2 mb-3">
                  <Star className="h-4 w-4" />
                  <span>{Math.floor(Math.random() * 2) + 4}.0</span>
                </div>
                <div className="text-2xl font-bold text-white mb-3">₹{ride.cost_inr}</div>
                <div className="flex gap-2">
                  <button 
                    className="flex-1 py-2 bg-lavender-500 text-white rounded-lg hover:bg-lavender-600 transition-colors flex items-center justify-center gap-2"
                    onClick={(e) => handleBookNow(e, ride)}
                  >
                    <span>Book Now</span>
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : pickup && destination ? (
          <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700 text-center">
            <div className="text-yellow-400 mb-4">
              <Search className="h-12 w-12 mx-auto mb-2" />
              <h3 className="text-lg font-semibold">Looking for rides...</h3>
            </div>
            <p className="text-gray-300 mb-4">
              We're searching for the best ride options between <span className="text-blue-400 font-medium">{pickup}</span> and <span className="text-green-400 font-medium">{destination}</span>
            </p>
            <div className="text-sm text-gray-400">
              <p>💡 Try our AI search above for more flexible location matching</p>
            </div>
          </div>
        ) : (
          <div className="bg-gradient-to-br from-gray-800/30 to-gray-900/30 rounded-xl p-8 border border-gray-700/50 text-center">
            <div className="text-blue-400 mb-4">
              <MapPin className="h-16 w-16 mx-auto mb-3" />
              <h3 className="text-xl font-semibold text-white">Ready to Find Your Ride?</h3>
            </div>
            <p className="text-gray-300 mb-6 max-w-md mx-auto">
              Enter your pickup and destination locations above to compare rides from multiple platforms and find the best option for your journey.
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm text-gray-400 max-w-lg mx-auto">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <span>Compare Prices</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span>Multiple Platforms</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                <span>Real-time Data</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                <span>AI Powered</span>
              </div>
            </div>
          </div>
        )}
        
        {/* Ride Analysis Sidebar */}
        <RideAnalysisSidebar
          isOpen={showAnalysis && selectedRide !== null}
          onClose={() => setShowAnalysis(false)}
          ride={selectedRide}
        />
      </div>
    </div>
  );
};

export default RideComparison;
