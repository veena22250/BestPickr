import { useState } from "react";
import { notificationAPI } from "../services/api";
import { useAuth } from "../contexts/AuthContext";

interface NotifyButtonProps {
  productId: string;
  productName: string;
}

const NotifyButton: React.FC<NotifyButtonProps> = ({ productId, productName }) => {
  const { user } = useAuth(); // Get OAuth user
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleNotify = async () => {
    if (!user?.email) {
      alert("Please log in first to get notifications!");
      return;
    }

    try {
      setLoading(true);
      await notificationAPI.notifyMe(productId, productName, user.email);
      setSent(true);
    } catch (error) {
      console.error("Error sending notification:", error);
      alert("Failed to send notification. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleNotify}
      disabled={loading || sent}
      className="mt-3 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-500"
    >
      {sent ? "🔔 Notification Sent" : loading ? "Sending..." : "Notify Me"}
    </button>
  );
};

export { NotifyButton };