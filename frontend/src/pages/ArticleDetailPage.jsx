import React from 'react';
import ArticleDetails from '../components/ArticleDetails';

const ArticleDetailPage = ({ articleId, onBack }) => {
  return <ArticleDetails articleId={articleId} onBack={onBack} />;
};

export default ArticleDetailPage;