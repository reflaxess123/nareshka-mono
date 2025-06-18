import {
  AppRoutes,
  routeConfig,
} from '@/app/providers/router/model/routeConfig';
import { Loading } from '@/shared/components/Loading';
import { Navbar } from '@/shared/components/Navbar';
import { PageTransition } from '@/shared/components/PageTransition';
import { useAuth } from '@/shared/hooks';
import { Sidebar } from '@/widgets/Sidebar';
import { Suspense } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

export const AppRouter = () => {
  const { isAuthenticated } = useAuth();

  const homeElement = routeConfig.find(
    (route) => route.path === AppRoutes.HOME
  )?.element;
  const getStartedElement = routeConfig.find(
    (route) => route.path === AppRoutes.GET_STARTED
  )?.element;

  return (
    <BrowserRouter>
      <Navbar />
      {isAuthenticated ? (
        <Sidebar>
          <PageTransition>
            <Routes>
              {routeConfig.map((route) => (
                <Route
                  key={route.path}
                  path={route.path}
                  element={
                    route.path === AppRoutes.HOME ? (
                      route.element
                    ) : (
                      <Suspense fallback={<Loading />}>
                        {route.element}
                      </Suspense>
                    )
                  }
                />
              ))}
            </Routes>
          </PageTransition>
        </Sidebar>
      ) : (
        <Routes>
          <Route
            key={AppRoutes.HOME}
            path={AppRoutes.HOME}
            element={homeElement}
          />
          <Route
            key={AppRoutes.GET_STARTED}
            path={AppRoutes.GET_STARTED}
            element={
              <Suspense fallback={<Loading />}>{getStartedElement}</Suspense>
            }
          />
        </Routes>
      )}
    </BrowserRouter>
  );
};
