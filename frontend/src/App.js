import React, {useState} from "react";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import ArticleDetailPage from "./pages/ArticleDetailPage";
import MisinformationDetector from "./components/MisinformationDetector";
import "./App.css";

function App() {
  const [currentPage, setCurrentPage] = useState("home");
  const [selectedArticleId, setSelectedArticleId] = useState(null);

  const handleNavigation = (page) => {
    setCurrentPage(page);
    if (page === "home") {
      setSelectedArticleId(null);
    }
  };

  const handleOpenArticle = (articleId) => {
    setSelectedArticleId(articleId);
    setCurrentPage("article");
  };

  const handleBackToHome = () => {
    setSelectedArticleId(null);
    setCurrentPage("home");
  };

  const renderCurrentPage = () => {
    switch (currentPage) {
      case "home":
        return <Home onOpenArticle={handleOpenArticle} />;
      case "detect":
        return <MisinformationDetector />;
      case "article":
        return (
          <ArticleDetailPage
            articleId={selectedArticleId}
            onBack={handleBackToHome}
          />
        );
      default:
        return <Home onOpenArticle={handleOpenArticle} />;
    }
  };

  return (
    <div className="app">
      <div className="app-background">
        <Navbar currentPage={currentPage} onNavigate={handleNavigation} />
        <main className="app-main">{renderCurrentPage()}</main>
      </div>
    </div>
  );
}

export default App;
