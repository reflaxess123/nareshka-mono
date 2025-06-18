import { useAuth } from '@/shared/hooks';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Landing from '../../Landing/ui/Landing';

const Home = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  if (isAuthenticated) {
    return null;
  }

  return <Landing />;
};

export default Home;
