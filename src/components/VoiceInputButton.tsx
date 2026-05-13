import React from 'react';
import { Mic } from 'lucide-react';

interface VoiceInputButtonProps {
  onResult: (text: string) => void;
  onError?: (error: any) => void;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const VoiceInputButton: React.FC<VoiceInputButtonProps> = ({
  onResult,
  onError,
  size = 'md',
  className = '',
}) => {
  const [isListening, setIsListening] = React.useState(false);
  const recognitionRef = React.useRef<any>(null);

  React.useEffect(() => {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) return;
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.continuous = false;
    recognitionRef.current.interimResults = false;
    recognitionRef.current.lang = 'en-US';

    recognitionRef.current.onresult = (event: any) => {
      let transcript = event.results[0][0].transcript;
      // Remove trailing full stop if present
      transcript = transcript.replace(/[.。]+$/, '');
      setIsListening(false);
      onResult(transcript);
    };
    recognitionRef.current.onend = () => setIsListening(false);
    recognitionRef.current.onerror = (event: any) => {
      setIsListening(false);
      if (onError) onError(event.error);
    };
  }, [onResult, onError]);

  const handleMicClick = () => {
    if (recognitionRef.current) {
      setIsListening(true);
      recognitionRef.current.start();
    }
  };

  let sizeClass = 'h-6 w-6';
  if (size === 'sm') sizeClass = 'h-5 w-5';
  if (size === 'lg') sizeClass = 'h-8 w-8';

  return (
    <button
      type="button"
      onClick={handleMicClick}
      className={`rounded-full p-2 ${isListening ? 'bg-lavender-500 text-white animate-pulse' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'} ${className}`}
      title={isListening ? 'Listening...' : 'Voice Search'}
      aria-label="Voice Search"
    >
      <Mic className={sizeClass} />
    </button>
  );
};

export default VoiceInputButton; 