import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

/**
 * Wrap any page that requires login. Pass `allowedRoles` to also restrict by role.
 *   <ProtectedRoute allowedRoles={["admin"]}><AdminDashboard /></ProtectedRoute>
 */
export default function ProtectedRoute({ children, allowedRoles }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div style={{ padding: "2rem" }}>Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    // logged in, but wrong role — send them to their own dashboard rather than a dead end
    return <Navigate to={`/${user.role}`} replace />;
  }

  return children;
}
