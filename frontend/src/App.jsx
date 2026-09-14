import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { BookmarksProvider } from "./context/BookmarksContext";
import Navbar from "./components/common/Navbar";
import AppRoutes from "./routes/AppRoutes";
import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <BookmarksProvider>
          <Navbar />
          <AppRoutes />
        </BookmarksProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
