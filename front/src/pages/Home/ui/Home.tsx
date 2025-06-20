import { isAdmin } from '@/entities/User/model/types';
import { useAuth } from '@/shared/hooks';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Landing from '../../Landing/ui/Landing';

const Home = () => {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated && user) {
      if (isAdmin(user.role)) {
        navigate('/admin-panel');
      } else {
        navigate('/tasks');
      }
    }
  }, [isAuthenticated, user, navigate]);

  if (isAuthenticated) {
    return null;
  }

  return <Landing />;
};

export default Home;
